from .configs.functions import spark_map_sentiment_udf


def transform(df):
    map_sent_udf = spark_map_sentiment_udf()
    df = df.withColumn("sentiment", map_sent_udf("rating"))
    df_final = df.select("review_content", "sentiment")
    return df_final
