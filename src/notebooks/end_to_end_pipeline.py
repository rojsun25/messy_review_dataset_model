# Databricks notebook source
# DBTITLE 1,install required libraries
# Initialise libraries
!pip install -r "/Workspace/Users/rojsun.parameshwaran1@royallondon.com/messy_review_dataset_model/requirements.txt"

# # restart kernal
dbutils.library.restartPython()

# COMMAND ----------

# Dynamically retrieve input variables (e.g., file path, target path) for parameterized workflows and reusable functions

dbutils.widgets.text("input_file_path", "")     # /Volumes/dev_edp_internal/byod/gdo_filestore/pre_raw/
dbutils.widgets.text("raw_file_path", "")       # /Volumes/dev_edp_internal/byod/gdo_filestore/raw/
dbutils.widgets.text("transform_file_path", "")    # /Volumes/dev_edp_internal/byod/gdo_filestore/transform_output/
dbutils.widgets.text("output_file_path", "")    # /Volumes/dev_edp_internal/byod/gdo_filestore/output/

input_file_path = dbutils.widgets.get("input_file_path")
raw_file_path = dbutils.widgets.get("raw_file_path")
transform_file_path = dbutils.widgets.get("transform_file_path")
output_file_path = dbutils.widgets.get("output_file_path")

# print variables
print(f"Input file path: {input_file_path}")
print(f"Raw file path: {raw_file_path}")
print(f"Transform file path: {transform_file_path}")
print(f"Output file path: {output_file_path}")

# COMMAND ----------

import glob
import os
import shutil
import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import (
    col, lower, trim, udf, regexp_replace, size, split, array_distinct, when, expr, DataFrame, split, explode_outer, col, length
)
from pyspark.sql.types import StringType

class ReviewDataset:
    """
    A class to process messy review datasets.
    """

    def __init__(self, spark, input_folder, raw_folder, transform_folder,output_folder):
        """
        Initialize the ReviewDataset class with Spark session and input/output paths.
        """
        self.spark = spark
        self.input_folder = input_folder
        self.raw_folder = raw_folder
        self.transform_folder = transform_folder
        self.output_folder = output_folder

    @staticmethod
    def get_latest_file_in_folder(folder_path: str, pattern: str = "*.csv") -> str:  
        """
        Find the latest file in a folder
        """

        files = glob.glob(os.path.join(folder_path, pattern))
        if not files:
            raise FileNotFoundError(f"No files found in {folder_path} with pattern {pattern}")
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    @staticmethod
    def move_file_to_folder(src_file_path: str, dest_folder: str) -> str: 
        """
        Move a file to a folder
        """
        os.makedirs(dest_folder, exist_ok=True)
        filename = os.path.basename(src_file_path)
        dest_file_path = os.path.join(dest_folder, filename)
        shutil.move(src_file_path, dest_file_path)
        print(f"Moved file {filename} to {dest_folder}")
        return dest_file_path

    @staticmethod
    def remove_html_spark(df, review_col: str = "review_content"):
        """
        Remove HTML tags and links using a Python UDF with BeautifulSoup.
        """

        def clean_html(text):
            if text is None:
                return None
            soup = BeautifulSoup(text, "lxml")
            # Remove all links
            for a in soup.find_all('a'):
                a.decompose()
            return soup.get_text(separator=" ", strip=True).lower().strip()

        clean_html_udf = udf(clean_html, StringType())
        cleaned = df.withColumn(review_col, clean_html_udf(col(review_col)))
        return cleaned

    @staticmethod
    def map_sentiment_spark(df: DataFrame, rating_col: str = "rating"):
        """
        Map numeric rating to sentiment using Spark SQL when/otherwise, using try_cast for tolerance.
        """
        rating_d = expr(f"try_cast({rating_col} as double)")
        df = df.withColumn(
            "sentiment",
            when(rating_d >= 4.0, "positive")
            .when(rating_d == 3.0, "neutral")
            .when(rating_d <= 2.0, "negative")
            .otherwise("neutral")
        )
        return df

    def ingest_latest_file(self, input_folder, output_folder):
        """
        Ingest the latest CSV file from the input folder and move it to the output folder.
        """
        latest_file = self.get_latest_file_in_folder(input_folder, "*.csv")
        moved_file = self.move_file_to_folder(latest_file, output_folder)
        print(f"Ingested file is now at: {moved_file}")
        return moved_file

    @staticmethod
    def detect_suspicious_reviews_spark(df: DataFrame, review_col: str = "review_content", min_word_len: int = 5):
        """
        Detect suspicious reviews based on word count and repetitive words.
        """

        df = df.withColumn("word_count", size(split(col(review_col), " ")))
        df = df.withColumn("is_suspicious_length", col("word_count") < min_word_len)  # CHANGED: fixed < operator
        df = df.withColumn("distinct_words_count", size(array_distinct(split(col(review_col), " "))))
        df = df.withColumn("is_suspicious_repetitive", col("distinct_words_count") == 1)
        df = df.withColumn("suspicious_review", col("is_suspicious_length") | col("is_suspicious_repetitive"))
        df = df.drop("word_count", "distinct_words_count", "is_suspicious_length", "is_suspicious_repetitive")
        return df

    def explode_zip_columns(self, df, cols_to_zip,
                            sep=",",                       # string or dict: {"colA": ",", "colB": "|", ...}
                            keep_other_cols=True,          # keep non-exploded columns in the output
                            trim_tokens=True,              # trim whitespace around tokens
                            drop_empty_tokens=True,        # drop empty tokens ("")
                            mode="shortest",                # "longest" | "shortest" | "strict"
        ):
        """
        Split multiple string columns by delimiter and explode them *in lockstep*.
        The i-th split value from each column is kept aligned on the same output row.

        modes:
        - "longest": keep rows up to the longest list; missing values become NULLs.
        - "shortest": keep only positions where *all* columns have a value (drop NULLs).
        - "strict":   keep only input rows where all split arrays have *equal length*.
        """
        # Normalize separators
        if isinstance(sep, str):
            sep_map = {c: sep for c in cols_to_zip}
        else:
            # dict provided; default to "," if missing
            sep_map = {c: sep.get(c, ",") for c in cols_to_zip}

        # Build array versions of the columns
        tmp = df
        arr_names = []
        for c in cols_to_zip:
            # Cast to string, split, then clean
            arr = F.split(F.coalesce(F.col(c).cast("string"), F.lit("")), F.lit(sep_map[c]))
            if trim_tokens:
                arr = F.transform(arr, lambda x: F.trim(x))
            if drop_empty_tokens:
                arr = F.filter(arr, lambda x: x != "")
            arr_name = f"__{c}__arr"
            tmp = tmp.withColumn(arr_name, arr)
            arr_names.append(arr_name)

        # In strict mode, keep only rows where all arrays have equal size
        if mode == "strict":
            size0 = F.size(F.col(arr_names[0]))
            cond = F.lit(True)
            for a in arr_names[1:]:
                cond = cond & (F.size(F.col(a)) == size0)
            tmp = tmp.filter(cond)

        # Zip arrays so positions are aligned; explode rows
        zipped = F.arrays_zip(*[F.col(a) for a in arr_names]).alias("__zipped")
        exploded = tmp.withColumn("__z", F.explode(zipped)).drop("__zipped")

        # Select original non-exploded columns (if requested)
        base_cols = [c for c in df.columns if (c not in cols_to_zip)] if keep_other_cols else []

        # Pull aligned values back out of the exploded struct and rename to original col names
        select_exprs = [F.col(c) for c in base_cols]
        for c in cols_to_zip:
            select_exprs.append(F.col(f"__z.__{c}__arr").alias(c))

        out = exploded.select(*select_exprs)

        # Shortest mode: drop rows where any aligned value is NULL
        if mode == "shortest":
            cond = F.lit(True)
            for c in cols_to_zip:
                cond = cond & F.col(c).isNotNull()
                out = out.filter(cond)

        return out

    def clean_data(self, raw_folder) -> DataFrame:
        """
        Clean the raw data by removing HTML tags and links, and exploding the columns.
        """

        latest_file = self.get_latest_file_in_folder(raw_folder, "*.csv")
        print(f"Cleaning latest file: {latest_file}")

        time.sleep(20)
        df = self.spark.read.option("header", True).csv(latest_file)

        # remove all the emoji's
        df = df.select([regexp_replace(col(c), r'[^\x00-\x7F]+', '').alias(c) for c in df.columns])

        # remove columns that mismatch the pattern
        df = df.filter(col("discount_percentage").rlike(r"%$")).filter(~col("user_id").rlike("[a-z]")).filter(length(col("user_id")) > 28).filter(~col("user_name").rlike(r"\d"))
        
        pdf = df.toPandas() # convert to pandas 
        
        # Remove HTML tags and links using BeautifulSoup in Pandas
        def clean_html(text):
            if pd.isnull(text):
                return None
            # Only treat as HTML if it contains HTML tags
            if re.search(r"<.*?>", str(text)):
                soup = BeautifulSoup(text, "lxml")
                for a in soup.find_all('a'):
                    a.decompose()
                return soup.get_text(separator=" ", strip=True).lower().strip()
            else:
                return str(text).lower().strip()

        pdf["review_content"] = pdf["review_content"].apply(clean_html)
        pdf["review_title"] = pdf["review_title"].apply(clean_html)

        # lowercase the columns
        pdf["user_name"] = pdf["user_name"].str.strip().str.lower()
        
        #drop columns with null values
        pdf = pdf.loc[:, ~pdf.isna().any()]

        # # lowercase the columns
        # pdf["review_id"] = pdf["review_id"].str.strip().str.lower()
        # pdf["user_id"] = pdf["user_id"].str.strip().str.lower()
        
        # Drop rows where review_content became null or empty after cleaning
        pdf = pdf[pdf["review_content"].notnull() & (pdf["review_content"].str.strip() != "")]

        # Suspicious review detection in Pandas
        pdf["word_count"] = pdf["review_content"].str.split().str.len()
        pdf["distinct_words_count"] = pdf["review_content"].str.split().apply(lambda x: len(set(x)) if isinstance(x, list) else 0)
        pdf["is_suspicious_length"] = pdf["word_count"] < 5
        pdf["is_suspicious_repetitive"] = pdf["distinct_words_count"] == 1
        pdf["suspicious_review"] = pdf["is_suspicious_length"] | pdf["is_suspicious_repetitive"]
        pdf = pdf.drop(columns=["word_count", "distinct_words_count", "is_suspicious_length", "is_suspicious_repetitive"])

        # Convert back to Spark DataFrame
        df = self.spark.createDataFrame(pdf)

        #  Explode the columns
        exploded_df = self.explode_zip_columns(
            df,
            cols_to_zip=["user_id", "user_name", "review_id", "review_title", "review_content"],
            sep=",",
            mode="longest"
        )

        return exploded_df.dropna(how='any').dropDuplicates()

    def transform(self, df: DataFrame) -> DataFrame:
        """
        Transform the input DataFrame.
        """
        df = self.map_sentiment_spark(df, rating_col="rating")
        print("Transformed data - added sentiment column")
        # df = df.select("review_content", "sentiment")
        return df
    
    def save_transformed_output(self, df, transform_folder, output_filename="training_dataset"):
        output_path = os.path.join(transform_folder, output_filename)
        df.coalesce(1).write.mode("overwrite").option("header", True).option("encoding", "utf-8").csv(output_path)
        print(f"Output saved to {output_path}")

    def save_output(self, df, output_folder, output_filename="training_dataset"):
        output_path = os.path.join(output_folder, output_filename)
        df.coalesce(1).write.mode("overwrite").option("header", True).option("encoding", "utf-8").csv(output_path)
        print(f"Output saved to {output_path}")

    def run_pipeline(self):
        try:
            # Step 1: Ingest latest file from input folder to raw folder
            self.ingest_latest_file(self.input_folder, self.raw_folder)

            time.sleep(10)
            # Step 2: Clean data
            df = self.clean_data(self.raw_folder)
            # df.show(5, truncate=False) # show records
            # display(df)

            # Step 3: Transform data
            df_final = self.transform(df)
            # df_final.show(5, truncate=False)
            # display(df_final)

            # Step 4: Save output
            self.save_output(df_final, self.output_folder)
            display(df_final)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("review_dataset").getOrCreate()
    task = ReviewDataset(spark, input_file_path, raw_file_path, transform_file_path, output_file_path)
    task.run_pipeline()
