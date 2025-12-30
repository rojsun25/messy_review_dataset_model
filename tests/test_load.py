import os
import pytest
from pathlib import Path

import src.load as load_mod


def test_load_module_has_save_output():
    assert hasattr(load_mod, "save_output"), "Expected save_output in src/load.py"
    assert callable(load_mod.save_output)


def test_save_output_writes_csv_folder(tmp_path: Path, spark, spark_df):
    out_dir = tmp_path / "output"
    out_dir.mkdir()

    load_mod.save_output(spark_df, str(out_dir), output_filename="training_dataset")

    written = out_dir / "training_dataset"
    assert written.exists()
    # Spark writes part files:
    part_files = list(written.glob("part-*"))
    assert len(part_files) >= 1
