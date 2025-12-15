import argparse
from pathlib import Path

from src import clean, 01_ingest, load, transform
from src.configs.functions import initialize_spark


def run_pipeline(pre_raw_folder, raw_folder, output_folder):
    ingest.main(pre_raw_folder, raw_folder)

    spark = initialize_spark()
    df, spark = clean.main(raw_folder)

    transformed_df = transform.transform(df)

    load.save_output(transformed_df, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre_raw_folder", required=True)
    parser.add_argument("--raw_folder", required=True)
    parser.add_argument("--output_folder", required=True)
    args = parser.parse_args()

    # Resolve provided folders relative to the repository root (where this file lives).
    repo_root = Path(__file__).parent.resolve()
    pre_raw = (repo_root / args.pre_raw_folder).resolve()
    raw = (repo_root / args.raw_folder).resolve()
    output = (repo_root / args.output_folder).resolve()

    run_pipeline(str(pre_raw), str(raw), str(output))
