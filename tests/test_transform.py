import pytest
import src.transform as transform_mod


def test_transform_module_has_sentiment_mapper():
    assert hasattr(transform_mod, "map_sentiment_spark"), "Expected map_sentiment_spark in src/transform.py"
    assert callable(transform_mod.map_sentiment_spark)


def test_map_sentiment_spark(spark_df):
    df2 = transform_mod.map_sentiment_spark(spark_df, rating_col="rating")
    sentiments = {r["review_id"]: r["sentiment"] for r in df2.select("review_id", "sentiment").collect()}

    assert sentiments["r1"] == "positive"
    assert sentiments["r2"] == "neutral"
    assert sentiments["r3"] == "negative"
