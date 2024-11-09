import pandas as pd
from google.cloud import storage
from io import StringIO
import os
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import bigquery
# Load environment variables from .env file
load_dotenv()

print("Init bigquery, storage client")
# Initialize BigQuery and GCS clients
bigquery_client = bigquery.Client()
storage_client = storage.Client()

# Function to upload DataFrame to GCS
def upload_dataframe_to_gcs(bucket_name, dataframe, destination_blob_name):
    """
    Upload a Pandas DataFrame to Google Cloud Storage directly as a CSV.
    :param bucket_name: Google Cloud Storage bucket name
    :param dataframe: The DataFrame to upload
    :param destination_blob_name: The path and file name within the GCS bucket
    """
    # Initialize a Google Cloud Storage client
    storage_client = storage.Client()

    # Get the GCS bucket
    bucket = storage_client.bucket(bucket_name)

    # Convert DataFrame to CSV in-memory (not saving it locally)
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)

    # Create a new blob (file) in GCS and upload the CSV content
    blob = bucket.blob(destination_blob_name)
    
    # Upload the in-memory CSV to GCS
    blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
    
    print(f"DataFrame successfully uploaded to {destination_blob_name} in bucket {bucket_name}.")

# Function to process and upload stock or economic data based on type, timeframe, and date range
def process_and_upload_data(data, data_type, symbol=None, timeframe=None, start_date=None, end_date=None):
    """
    Process and upload stock or economic data to GCS based on specified parameters.
    :param data: DataFrame containing the data
    :param data_type: Either 'stock' or 'economic' indicating the type of data
    :param symbol: Stock symbol (only applicable for stock data)
    :param timeframe: Timeframe of the data (e.g., '1_minute', 'daily') for stock data
    :param start_date: Start date for the data (YYYY-MM-DD format)
    :param end_date: End date for the data (YYYY-MM-DD format)
    """
    # Define GCS bucket name
    bucket_name = f"{os.getenv("BUCKET_STORAGE")}"

    # Generate the destination blob name (file path in GCS)
    if data_type == "stock":
        if not symbol or not timeframe:
            raise ValueError("Stock data requires both symbol and timeframe.")
        destination_blob_name = f"stock_data/{symbol}/{timeframe}/{symbol}_{timeframe}_{start_date}_{end_date}.csv"
    
    elif data_type == "economic":
        destination_blob_name = f"economic_data/{symbol}/{symbol}_{start_date}_{end_date}.csv"

    else:
        raise ValueError("Invalid data_type. Must be 'stock' or 'economic'.")

    # Upload the data to GCS
    upload_dataframe_to_gcs(bucket_name, data, destination_blob_name)

def load_data_to_bigquery(bucket_name, root_folder, dataset_id):
    """Traverse folders and load CSV files into BigQuery."""
    print("call load data to big query")
    bucket = storage_client.get_bucket(bucket_name)
    #print(bigquery_client)
    print(bucket_name)
    print(root_folder)
    print(dataset_id)
    # List all files in the bucket
    blobs = bucket.list_blobs(prefix=root_folder)
    if (blobs):
        for blob in blobs:
            #print(blob.name)
            if blob.name.endswith('.csv'):
                # Parse folder structure
                path_parts = blob.name.split('/')
                if 'economic_data' in path_parts:
                    # Example path: economic_data/UNRATE/file1.csv
                    data_type = path_parts[1]
                    table_name = f"{dataset_id}.{data_type.lower()}"
                    #print(table_name)
                elif 'stock_data' in path_parts:
                    # Example path: stock_data/TLSA/1H/file1.csv
                    stock_symbol = path_parts[1]
                    timeframe = path_parts[2]
                    table_name = f"{dataset_id}.{stock_symbol.lower()}_{timeframe.lower()}"

                print(f"Loading file: {blob.name} into {table_name}")
                
                # Upload to BigQuery
                load_to_bigquery(blob, table_name)
            else:
                print("Cant file .csv")
    else:
        print("No blobs found in bucket")


def load_to_bigquery(blob, table_id):
    """Load a CSV file from GCS to BigQuery table."""
    
    # Configure load job settings
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND  # Append to existing table
    )
    
    uri = f"gs://{blob.bucket.name}/{blob.name}"
    
    # Load data from GCS to BigQuery
    load_job = bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)
    
    # Wait for the job to complete
    load_job.result()
    
    print(f"Loaded {blob.name} into {table_id}")


def create_partitioned_table(table_id):
    """Create a partitioned table in BigQuery based on ingestion time."""
    
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("value", "FLOAT"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date",  # Partitioned on the 'date' column
    )
    
    table = bigquery_client.create_table(table)  # API request
    print(f"Created partitioned table {table_id}")

# Example of calling the functions
"""
if __name__ == "__main__":
    proj_id = os.getenv("PROJ_ID")
    bucket_name = os.getenv("BUCKET_STORAGE")
    dataset_id = os.getenv("ECONOMIC_FOLDER")
"""
    


# Example usage of the function

# 1. Stock Data Example
"""
stock_data = pd.DataFrame({
    'Date': ['2024-01-01', '2024-01-02'],
    'Open': [1800, 1850],
    'Close': [1820, 1865]
})

# Define parameters for stock data
stock_symbol = 'AAPL'
stock_timeframe = 'daily'
start_date_stock = '2024-01-01'
end_date_stock = '2024-01-02'

# Process and upload stock data
process_and_upload_data(
    stock_data, 
    data_type='stock', 
    symbol=stock_symbol, 
    timeframe=stock_timeframe, 
    start_date=start_date_stock, 
    end_date=end_date_stock
)

# 2. Economic Data Example (e.g., CPI)
economic_data = pd.DataFrame({
    'Date': ['2024-01-01', '2024-01-02'],
    'CPI': [250.5, 251.0]
})

# Define parameters for economic data (e.g., CPI)
economic_type = 'CPI'
start_date_economic = '2024-01-01'
end_date_economic = '2024-01-02'

# Process and upload economic data
process_and_upload_data(
    economic_data, 
    data_type='economic', 
    symbol=economic_type, 
    start_date=start_date_economic, 
    end_date=end_date_economic
)
"""