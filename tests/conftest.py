import os
import pytest

from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """
    Local Spark session for unit tests.
    Works in CI and local runs.
    """
    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("messy_review_dataset_model_tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture()
def sample_review_rows():
    """
    Small, deterministic dataset for Spark/Pandas tests.
    """
    return [
        {
            "rating": "5",
            "review_content": "<p>Amazing product! <a href='x'>link</a> 😀</p>",
            "review_title": "<b>Great</b>",
            "discount_percentage": "60%",
            "user_id": "1234567890123456789012345678901",
            "user_name": "Alice",
            "review_id": "r1",
        },
        {
            "rating": "3",
            "review_content": "ok ok ok",
            "review_title": "OK",
            "discount_percentage": "10%",
            "user_id": "1234567890123456789012345678902",
            "user_name": "Bob",
            "review_id": "r2",
        },
        {
            "rating": "1",
            "review_content": "bad",
            "review_title": "Bad",
            "discount_percentage": "5%",
            "user_id": "1234567890123456789012345678903",
            "user_name": "Charlie",
            "review_id": "r3",
        },
    ]


@pytest.fixture()
def spark_df(spark, sample_review_rows):
    return spark.createDataFrame(sample_review_rows)
