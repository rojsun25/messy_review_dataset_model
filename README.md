# Amazon Customer Reviews Cleaning and Sentiment Annotation Pipeline

## Overview

This project implements a data pipeline to clean and prepare Amazon product reviews for sentiment analysis model training. The pipeline processes an input raw review dataset, cleans text data, performs data quality checks, and annotates reviews with sentiment labels derived from star ratings.

## Repository Structure

```
messy_review_dataset_model/
│
├── requirements.txt
├── .gitignore
├── README.md
└── data/
    └── amazon.csv                        # Raw example dataset
├── src/
│   ├── configs/
│   │   └── functions.py                  # Reusable helper functions
│   ├── 01_ingest.py                      # Dataset ingestion step
│   ├── 02_clean.py                       # Cleaning & quality checks
│   ├── 03_transform.py                   # Sentiment annotation
│   ├── 04_load.py                        # Output generation
└── output/
    └──training_dataset.csv                  # Final output
```

## Pipeline Steps

### 1. Data Ingestion

- Load raw CSV from provided path with pandas.
- Inspect columns and dataset size.

### 2. Data Cleaning

- Remove rows with missing or empty `review_content`.
- Standardize text by converting to lowercase and stripping any HTML tags.
- Detect duplicate reviews via review IDs and identical text.
- Identify suspicious reviews that are extremely short or contain repetitive words.
- Documented data quality issues.

### 3. Data Annotation

- Map `rating` (1-5 stars) to sentiment labels:
  - 1-2 stars → `negative`
  - 3 stars → `neutral`
  - 4-5 stars → `positive`
- Output dataset includes only cleaned review text and sentiment label.

### 4. Output

- Final dataset saved as `training_dataset.csv`
- File contains two columns: `review_content` and `sentiment`.

## Data Quality Issues Found

1. **Duplicate Entries**: Identified duplicates by `review_id` and identical review texts.  
2. **Suspicious Reviews**: Detected very short or repetitive reviews, likely low-quality or spam.  
3. **Missing or Empty Text**: Removed reviews with missing/empty content.

## Labeling Logic

- Ratings mapped to sentiment as:
  - 1-2 → negative  
  - 3 → neutral  
  - 4-5 → positive  

## Usage

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run pipeline steps sequentially:

```bash
python src/01_ingest.py --input_folder pre_raw --output_folder raw
python src/02_clean.py --raw_folder raw
python src/03_transform.py 
python src/04_load.py --input_path transformed.parquet --output_folder output
```

3. Use `training_dataset.csv` for model training.

## Dependencies

- pandas
- beautifulsoup4
- lxml
- pyspark
