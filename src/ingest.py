import argparse

from .configs.functions import get_latest_file_in_folder, move_file_to_folder


def main(input_folder, output_folder):
    latest_file = get_latest_file_in_folder(input_folder, "*.csv")
    moved_file = move_file_to_folder(latest_file, output_folder)
    print(f"Ingested file is now at: {moved_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest files from pre_raw to raw")
    parser.add_argument("--input_folder", required=True, help="Folder to pick raw input files from (pre_raw)")
    parser.add_argument("--output_folder", required=True, help="Folder to move ingested files into (raw)")
    args = parser.parse_args()

    main(args.input_folder, args.output_folder)
