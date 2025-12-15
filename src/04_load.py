import os


def save_output(df, output_folder, output_filename="training_dataset.csv"):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_filename)
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)
    print(f"Output saved to {output_path}")

