from pyflink.common import Time
from pyflink.table import (
    EnvironmentSettings,
    TableEnvironment,
    TableDescriptor,
    Schema,
    DataTypes
)
from pyflink.table.window import Session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_kafka_source_table(t_env):
    """Create Kafka source table"""
    source_ddl = """
        CREATE TABLE green_trips (
            lpep_pickup_datetime TIMESTAMP(3),
            lpep_dropoff_datetime TIMESTAMP(3),
            PULocationID INT,
            DOLocationID INT,
            passenger_count INT,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            WATERMARK FOR lpep_dropoff_datetime AS lpep_dropoff_datetime - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:9092',
            'properties.group.id' = 'taxi-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json',
            'json.fail-on-missing-field' = 'false',
            'json.ignore-parse-errors' = 'true'
        )
    """
    t_env.execute_sql(source_ddl)

def create_postgres_sink_table(t_env):
    """Create PostgreSQL sink table"""
    sink_ddl = """
        CREATE TABLE taxi_sessions (
            pu_location INT,
            do_location INT,
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            trip_count BIGINT,
            total_distance DOUBLE,
            avg_tips DOUBLE,
            PRIMARY KEY (pu_location, do_location, session_start) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'taxi_sessions',
            'username' = 'postgres',
            'password' = 'postgres'
        )
    """
    t_env.execute_sql(sink_ddl)

def create_session_window_query():
    """Create session window query"""
    return """
        INSERT INTO taxi_sessions
        SELECT 
            PULocationID as pu_location,
            DOLocationID as do_location,
            SESSION_START(lpep_dropoff_datetime, INTERVAL '5' MINUTES) as session_start,
            SESSION_END(lpep_dropoff_datetime, INTERVAL '5' MINUTES) as session_end,
            COUNT(*) as trip_count,
            SUM(trip_distance) as total_distance,
            AVG(tip_amount) as avg_tips
        FROM green_trips
        GROUP BY 
            PULocationID,
            DOLocationID,
            SESSION(lpep_dropoff_datetime, INTERVAL '5' MINUTES)
    """

def main():
    try:
        # Create Table Environment
        env_settings = EnvironmentSettings.in_streaming_mode()
        t_env = TableEnvironment.create(env_settings)

        # Set checkpointing interval
        t_env.get_config().get_configuration().set_string(
            "execution.checkpointing.interval", "10s"
        )

        # Create source and sink tables
        logger.info("Creating Kafka source table...")
        create_kafka_source_table(t_env)

        logger.info("Creating PostgreSQL sink table...")
        create_postgres_sink_table(t_env)

        # Execute session window query
        logger.info("Executing session window query...")
        session_query = create_session_window_query()
        t_env.execute_sql(session_query)

    except Exception as e:
        logger.error(f"Error in Flink job: {str(e)}")
        raise

if __name__ == '__main__':
    main()
