import glob
import os
import shutil

from bs4 import BeautifulSoup
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType


def get_latest_file_in_folder(folder_path: str, pattern: str = "*.csv") -> str:
    files = glob.glob(os.path.join(folder_path, pattern))
    if not files:
        raise FileNotFoundError(f"No files found in {folder_path} with pattern {pattern}")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def move_file_to_folder(src_file_path: str, dest_folder: str) -> str:
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(src_file_path)
    dest_file_path = os.path.join(dest_folder, filename)
    shutil.move(src_file_path, dest_file_path)
    print(f"Moved file {filename} to {dest_folder}")
    return dest_file_path


def remove_html(text: str):
    if text is None:
        return None
    return BeautifulSoup(text, "lxml").get_text()


def spark_clean_text_udf():
    def clean_text(text):
        if text is None or text.strip() == "":
            return None
        cleaned = remove_html(text)
        if cleaned is not None:
            return cleaned.lower().strip()
        else:
            return None

    return udf(clean_text, StringType())


def spark_map_sentiment_udf():
    def map_sentiment(rating):
        try:
            r = float(rating)
        except Exception:
            return "neutral"

        if r >= 4.0:
            return "positive"
        elif r == 3.0:
            return "neutral"
        elif r <= 2.0:
            return "negative"
        else:
            return "neutral"

    return udf(map_sentiment, StringType())


def initialize_spark(app_name: str = "ReviewProcessingApp"):
    spark = SparkSession.builder.appName(app_name).getOrCreate()
    return spark


def detect_suspicious_reviews_spark(df, review_col: str = "review_content", min_word_len: int = 5):
    from pyspark.sql.functions import array_distinct, size, split

    df = df.withColumn("word_count", size(split(col(review_col), " ")))
    df = df.withColumn("is_suspicious_length", col("word_count") < min_word_len)
    df = df.withColumn("distinct_words_count", size(array_distinct(split(col(review_col), " "))))
    df = df.withColumn("is_suspicious_repetitive", col("distinct_words_count") == 1)
    df = df.withColumn("suspicious_review", col("is_suspicious_length") | col("is_suspicious_repetitive"))
    df = df.drop("word_count", "distinct_words_count", "is_suspicious_length", "is_suspicious_repetitive")
    return df
