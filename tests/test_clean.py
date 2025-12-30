import inspect
import pytest
from pathlib import Path

import src.clean as clean_mod


def test_clean_module_has_entrypoint_or_functions():
    """
    Guards that clean.py exposes something testable.
    Adjust this if your API differs.
    """
    has_main = hasattr(clean_mod, "main") and callable(clean_mod.main)
    has_funcs = any(callable(v) for k, v in vars(clean_mod).items() if k.startswith(("clean", "remove_", "detect_")))
    assert has_main or has_funcs


@pytest.mark.skipif(not hasattr(clean_mod, "remove_html_spark"), reason="remove_html_spark not found in src.clean")
def test_remove_html_spark_removes_tags_and_links(spark, spark_df):
    df2 = clean_mod.remove_html_spark(spark_df, review_col="review_content")
    rows = [r["review_content"] for r in df2.select("review_content").collect()]
    assert all("<" not in x for x in rows if x is not None)
    assert all("href" not in x for x in rows if x is not None)


@pytest.mark.skipif(not hasattr(clean_mod, "detect_suspicious_reviews_spark"), reason="detect_suspicious_reviews_spark not found in src.clean")
def test_detect_suspicious_reviews_flags_short_and_repetitive(spark, spark_df):
    df2 = clean_mod.detect_suspicious_reviews_spark(spark_df, review_col="review_content", min_word_len=5)
    suspicious = {r["review_id"]: r["suspicious_review"] for r in df2.select("review_id", "suspicious_review").collect()}
    assert suspicious["r3"] is True  # "bad" -> short
    assert suspicious["r2"] is True  # "ok ok ok" -> repetitive/distinct_words_count==1
