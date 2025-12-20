Messy Review Dataset - Data Cleaning & Sentiment Annotation Pipeline
====================================================================

Overview
--------

   
This project provides an end-to-end data pipeline to clean and annotate a raw, messy Amazon Customer Reviews dataset for downstream usage in a sentiment analysis model training. The pipeline ingests the latest raw CSV file with product reviews, performs data cleaning and transformation, adds a sentiment label derived from star ratings, and outputs a polished CSV file ready for machine learning.  

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Table of Contents
-----------------

*   [Project Goals](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#project-goals)
*   [Pipeline Components](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#pipeline-components)
*   [Data Cleaning & Quality](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#data-cleaning--quality)
*   [Sentiment Annotation](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#sentiment-annotation)
*   [Running the Pipeline](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#running-the-pipeline)
*   [Output](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#output)
*   [Technologies Used](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#technologies-used)
*   [Trade-offs & Decisions](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#trade-offs--decisions)
*   [Next Steps](https://ai.azure.com/resource/assistants?wsid=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai&tid=f9daae82-4727-4163-93b9-2214828e3dba&assistantId=asst_enD4ONcbf9kNGChrqnj8RKqy&deploymentId=/subscriptions/432abe53-030d-48cd-b495-fa58e4957824/resourceGroups/rlg-dev-gdo-uks-rg-cog/providers/Microsoft.CognitiveServices/accounts/rlg-dev-gdo-uks-cogacc-oai/deployments/gpt35turbo&reloadCount=1#next-steps)  
    

* * *

Project Goals
-------------

*   Ingest the latest subset of the Amazon Customer Reviews dataset.
*   Clean raw review text by removing HTML elements, links, and emojis.
*   Standardize text (lowercase, strip whitespace).
*   Detect and document data quality issues in the dataset.
*   Annotate each review with a sentiment label (negative, neutral, positive) based on star ratings.
*   Output an easy-to-use CSV labeled dataset for model training.
*   Provide a reusable, parameterized pipeline implemented in Python & Spark (Ran in databricks notebooks)  
    

* * *

Repository Structure
--------------------

```
amazon_reviews_pipeline/
├── cicd/                           # configuration for devops pipeline
├── cicd_DAB/                       # configuration for Devops/DAB pipeline
│   └── DAB_deployment-pipeline.yml # Azure devops build pipeline
├── requirements.txt                # Python dependencies
├── .gitignore                      # Ignore Python caches, output files, etc.
├── README.md                       # Documentation and usage instructions
├── project_requirements/ 					# provided documents
├── pre_raw/                        # Input file directory (unprocessed/raw uploads)
│   └── amazon.csv                  # Example or actual input CSV file
│
├── raw/                            # Raw data directory (after ingestion)
│   └── amazon.csv                  # Latest ingested raw CSV file
│
├── output/                         # Output directory for processed datasets
│   └── training_dataset.csv        # Final cleaned and annotated CSV output
│
├── src/                            # Source code for pipeline components
│   ├── configs/
│   │   └── functions.py            # Reusable utility functions for all pipeline steps
│   ├── notebooks/
│   │   └── end_to_end_pipeline.py  # Databricks notebook script with reusable pipeline code
│   ├── ingest.py                   # Ingest raw files: move from input (pre_raw) to raw folder
│   ├── clean.py                    # Load latest raw file, clean text, perform quality checks using Spark
│   ├── transform.py                # Create sentiment labels from ratings in the dataset
│   ├── load.py                     # Save cleaned and labelled data to output folder
│   ├── visualise.py                # Scripts for basic visualisation of the processed data
│
└── run_pipeline.py                 # deploy script for running end-to-end pipeeline
```



Pipeline Components and steps
---------------------------

   
The pipeline is encapsulated in the `ReviewDataset` class, which performs the following steps:  

1.  **Ingestion:** Finds the latest CSV file from the specified input folder and moves it to the raw data folder.
2.  **Cleaning:**
    *   Reads the CSV into Spark DataFrame.
    *   Removes emojis (non-ASCII characters) and filters out inconsistent rows based on column format rules.
    *   Removes HTML tags and links from `review_content` and `review_title` using BeautifulSoup in Pandas.
    *   Converts text columns to lowercase and trims whitespace.
    *   Drops rows with missing or empty reviews post-cleaning.
    *   Detects suspicious reviews based on short length (<5 words) or repetitive single-word content.
    *   Explodes array-like columns to ensure clean row alignment.
3.  **Transformation:** Maps the numeric star ratings (1–5) to sentiment labels:
    *   1-2 stars → negative
    *   3 stars → neutral
    *   4-5 stars → positive
4.  **Saving:** Writes the cleaned and labeled data to a CSV file `training_dataset` in the output folder.  
    

* * *

Data Cleaning & Quality Issues
------------------------------

   
During cleaning, the following quality issues were identified and addressed:  

*   **Missing or Empty Reviews:** Some reviews contain null or empty strings after cleaning HTML, so those were removed to avoid noise in model training.
*   **HTML & Link Noise:** Raw review text contained HTML tags and embedded links that were stripped to maintain only natural language content.
*   **Non-ASCII Characters (Emojis):** Removed to avoid encoding issues downstream.
*   **Suspicious Reviews:**
    *   Reviews with very short text (<5 words) are flagged as suspicious since they may not provide enough sentiment context.
    *   Reviews with repetitive single-word content are also flagged as suspicious, e.g., `"good good good"`, as these may be spam or low-quality inputs.
*   **Data Format Anomalies:**
    *   Filtered out rows where discount percentages did not end with `%`.
    *   Filtered out user IDs containing alphabetic characters or with length under 29 to maintain consistent user ID quality.
    *   Filtered out user names containing numeric characters.  
          
        These cleaning steps improve data quality, reducing noise and potential bias in learning.  
        

* * *

**Sentiment Annotation Logic**

   
The `star_rating` column is mapped to sentiment labels as follows:  

Labeling Logic classified
  
| Star Rating | Sentiment |  
|-------------|-----------|  
| 1 or 2      | negative  |  
| 3           | neutral   |  
| 4 or 5      | positive  |  
  
This mapping supports a clear, three-class sentiment classification for training models.  
      
    This mapping captures the intuitive sentiment polarity based on star ratings commonly used in customer reviews.  
    

* * *

Running the Pipeline
--------------------

   
The script supports parameterized folder paths using Databricks widgets for flexibility:  

*   `input_file_path`: Folder containing raw input CSV files to ingest.
*   `raw_file_path`: Folder where the ingested file is moved and cleaned.
*   `output_file_path`: Folder where the final training dataset CSV is saved.  
      
    Example usage in Databricks or local Spark environment:  
    

`spark-submit review_dataset.py --input_file_path /path/to/input --raw_file_path /path/to/raw --output_file_path /path/to/output`  

  
The pipeline automatically detects the latest CSV, cleans, annotates, and writes the output. Logging feature can be added for tracking the files later.

## How to Use  
  
1. **Install Dependencies:**
  
`pip install -r requirements.txt`

2. **Run pipeline steps sequentially:**

`python src/01_ingest.py --input_folder /path/to/pre_raw --output_folder /path/to/raw
python src/02_clean.py --raw_folder /path/to/raw
python src/03_transform.py --input_path /path/to/raw/cleaned_latest.csv --output_path /path/to/transform/annotated.csv
python src/04_load.py --input_path /path/to/transform/annotated.csv --output_folder /path/to/output`

   
Alternatively, use the deploy script for one-step execution:  

`python src/run_pipeline.py --pre_raw_folder /path/to/pre_raw --raw_folder /path/to/raw --output_folder /path/to/output`  

   
3. **Final output:**  
  
`training_dataset.csv` will be available in your output folder containing clean review texts and sentiment labels ready for model training.  

Dependencies
------------

*   Python 3.x
*   PySpark
*   pandas
*   beautifulsoup4
*   lxml
See `requirements.txt` for exact versions.  


---------------------------------------------------------------------------------------------------

Output
------

*   The final output is a CSV file named `training_dataset` in the output folder.
*   This CSV contains the cleaned `review_content` text and the new `sentiment` label columns.
*   The dataset is ready for downstream sentiment analysis model training.  
    

* * *

Technologies Used
-----------------

*   Python 3.x
*   Apache Spark (PySpark) for scalable dataframe operations.
*   Pandas for convenient text cleaning with BeautifulSoup.
*   BeautifulSoup for parsing and stripping HTML content.
*   Glob, OS, shutil Python standard libraries for file handling.
*   Databricks Utilities (`dbutils.widgets`) for parameterization.  
    

* * *

Trade-offs & Decisions
----------------------

*   **Mixed Pandas and Spark:** The cleaning step toggles between Spark and Pandas for convenience in HTML cleaning via BeautifulSoup, favoring processing ease over full Spark-native solutions.
*   **Suspicious Review Filtering:** Rather than removing suspicious reviews outright, they are flagged, allowing for downstream filtering if needed.
*   **Strict Filtering Rules:** The filters applied on discount formatting, user_id, and user_name maintain data quality but may exclude some edge cases or legit data.
*   **Exploding Columns:** Separate multi-value fields split and exploded in lockstep ensures row integrity but assumes consistent delimiter usage.  
    

* * *

Next Steps
----------

*   Integrate the pipeline with orchestration tools like Airflow or Mage for scheduled runs.
*   Implement data quality checks and monitoring to track dataset health.
*   Extend cleaning to handle additional noise patterns or non-English text.
*   Add basic visualization for EDA to inform feature engineering.
*   Tune suspicious review logic based on model feedback.
