from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, TableEnvironment, StreamTableEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.time import Duration
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_events_aggregated_sink(t_env):
    """Create PostgreSQL sink table"""
    table_name = 'taxi_sessions'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            PULocationID INTEGER,
            DOLocationID INTEGER,
            num_trips BIGINT,
            total_distance DOUBLE,
            avg_tips DOUBLE
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)
    return table_name

def create_events_source_kafka(t_env):
    """Create Kafka source table"""
    table_name = "green_trips"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            lpep_pickup_datetime TIMESTAMP(3),
            lpep_dropoff_datetime TIMESTAMP(3),
            PULocationID INTEGER,
            DOLocationID INTEGER,
            passenger_count INTEGER,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            WATERMARK FOR lpep_dropoff_datetime AS lpep_dropoff_datetime - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda-1:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        )
    """
    t_env.execute_sql(source_ddl)
    return table_name

def log_aggregation():
    try:
        # Set up the execution environment
        env = StreamExecutionEnvironment.get_execution_environment()
        env.enable_checkpointing(10 * 1000)
        
        # Set up the table environment
        settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
        t_env = StreamTableEnvironment.create(env, environment_settings=settings)

        # Create source and sink tables
        logger.info("Creating Kafka source table...")
        source_table = create_events_source_kafka(t_env)
        
        logger.info("Creating PostgreSQL sink table...")
        sink_table = create_events_aggregated_sink(t_env)

        # Execute session window query
        logger.info("Executing session window query...")
        t_env.execute_sql(f"""
            INSERT INTO {sink_table}
            SELECT 
                SESSION_START(lpep_dropoff_datetime, INTERVAL '5' MINUTE) AS window_start,
                SESSION_END(lpep_dropoff_datetime, INTERVAL '5' MINUTE) AS window_end,
                PULocationID,
                DOLocationID,
                COUNT(*) AS num_trips,
                SUM(trip_distance) as total_distance,
                AVG(tip_amount) as avg_tips
            FROM {source_table}
            GROUP BY 
                SESSION(lpep_dropoff_datetime, INTERVAL '5' MINUTE),
                PULocationID,
                DOLocationID
        """).wait()

    except Exception as e:
        logger.error(f"Error in Flink job: {str(e)}")
        raise

if __name__ == '__main__':
    log_aggregation()
