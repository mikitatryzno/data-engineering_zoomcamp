import wget
import pandas as pd
import os
from time import time

def download_and_convert_to_parquet():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # URL for Green Taxi Data - October 2019
    url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
    csv_file = "data/green_tripdata_2019-10.csv.gz"
    parquet_file = "data/green_tripdata_2019-10.parquet"

    # Download the file if it doesn't exist
    if not os.path.exists(csv_file):
        print("Downloading data...")
        wget.download(url, csv_file)
        print("\nDownload completed!")

    # Convert to parquet
    print("\nReading CSV file and converting to parquet...")
    t0 = time()
    
    df = pd.read_csv(csv_file)
    
    # Convert datetime columns
    datetime_columns = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']
    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col])

    # Save as parquet
    print("Saving to parquet format...")
    df.to_parquet(parquet_file, index=False)
    
    # Optionally remove the CSV file to save space
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"Removed CSV file: {csv_file}")

    t1 = time()
    took = t1 - t0
    
    print(f"\nConversion completed! Data saved to: {parquet_file}")
    print(f"Total time taken: {took:.2f} seconds")
    
    # Print some basic information about the dataset
    print("\nDataset Info:")
    print(f"Number of records: {len(df)}")
    print(f"File size: {os.path.getsize(parquet_file) / (1024*1024):.2f} MB")
    print("\nColumns:", df.columns.tolist())

if __name__ == "__main__":
    download_and_convert_to_parquet()
