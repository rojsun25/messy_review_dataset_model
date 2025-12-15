import argparse

from .configs.functions import (
    detect_suspicious_reviews_spark,
    get_latest_file_in_folder,
    initialize_spark,
    spark_clean_text_udf,
)


def main(raw_folder):
    spark = initialize_spark("02_clean")
    latest_file = get_latest_file_in_folder(raw_folder, "*.csv")
    print(f"Cleaning latest file: {latest_file}")
    df = spark.read.option("header", True).csv(latest_file)

    clean_text_udf = spark_clean_text_udf()
    df = df.withColumn("review_content", clean_text_udf("review_content"))
    df = df.na.drop(subset=["review_content"])
    df = detect_suspicious_reviews_spark(df, review_col="review_content")
    df.cache()
    return df, spark


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean data from raw folder")
    parser.add_argument("--raw_folder", required=True, help="Folder containing raw CSV files")
    args = parser.parse_args()
    df, spark = main(args.raw_folder)
    df.printSchema()
    df.show(5)

