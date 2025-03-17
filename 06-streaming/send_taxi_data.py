import pandas as pd
from time import time
import json
from kafka import KafkaProducer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_taxi_data(file_path):
    """Read and prepare taxi data"""
    try:
        columns_to_keep = [
            'lpep_pickup_datetime',
            'lpep_dropoff_datetime',
            'PULocationID',
            'DOLocationID',
            'passenger_count',
            'trip_distance',
            'tip_amount'
        ]
        
        df = pd.read_parquet(file_path)[columns_to_keep]
        
        # Convert datetime columns to string format
        df['lpep_pickup_datetime'] = df['lpep_pickup_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['lpep_dropoff_datetime'] = df['lpep_dropoff_datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return df
    
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        return None

def send_to_kafka(df):
    """Send data to Kafka topic"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            retries=5,
            acks='all'
        )

        topic_name = 'green-trips'
        total_records = len(df)
        
        logger.info(f"Starting to send {total_records} records to Kafka")
        
        t0 = time()
        
        # Send each record to Kafka
        for i, record in enumerate(df.to_dict('records')):
            producer.send(topic_name, value=record)
            
            # Log progress every 10000 records
            if (i + 1) % 10000 == 0:
                logger.info(f"Sent {i + 1}/{total_records} records")

        # Ensure all messages are sent
        producer.flush()
        
        t1 = time()
        took = t1 - t0
        
        logger.info(f"Finished sending {total_records} records in {took:.2f} seconds")
        logger.info(f"Average speed: {total_records/took:.2f} records/second")
        
        return took
        
    except Exception as e:
        logger.error(f"Error sending data to Kafka: {str(e)}")
        return None

if __name__ == "__main__":
    # File path
    file_path = "data/green_tripdata_2019-10.parquet"
    
    # Prepare data
    logger.info("Preparing taxi data...")
    df = prepare_taxi_data(file_path)
    
    if df is not None:
        # Send data to Kafka
        took = send_to_kafka(df)
        if took:
            print(f"\nTotal time taken: {took:.2f} seconds")
