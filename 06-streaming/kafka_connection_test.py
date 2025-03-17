# Create a new file: kafka_connection_test.py
import json
from kafka import KafkaProducer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_kafka_producer():
    try:
        # JSON serializer function
        def json_serializer(data):
            return json.dumps(data).encode('utf-8')

        # Kafka server configuration
        server = 'localhost:9092'

        # Create producer instance
        producer = KafkaProducer(
            bootstrap_servers=[server],
            value_serializer=json_serializer,
            # Add additional configurations for reliability
            retries=5,
            acks='all'
        )

        # Test connection
        connected = producer.bootstrap_connected()
        
        if connected:
            logger.info("Successfully connected to Kafka!")
        else:
            logger.error("Failed to connect to Kafka")
            
        return producer, connected

    except Exception as e:
        logger.error(f"Error creating Kafka producer: {str(e)}")
        return None, False

if __name__ == "__main__":
    producer, connected = create_kafka_producer()
    print(f"Connection status: {connected}")