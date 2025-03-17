# Homework

For this homework we will be using the Taxi data:
- Green 2019-10 data from [here](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz)


## Setup

We need:

- Red Panda
- Flink Job Manager
- Flink Task Manager
- Postgres

It's the same setup as in the [pyflink module](../../../06-streaming/pyflink/), so go there and start docker-compose:

```bash
cd ../../../06-streaming/pyflink/
docker-compose up
```

(Add `-d` if you want to run in detached mode)

Visit http://localhost:8081 to see the Flink Job Manager

Connect to Postgres with pgcli, pg-admin, [DBeaver](https://dbeaver.io/) or any other tool.

The connection credentials are:

- Username `postgres`
- Password `postgres`
- Database `postgres`
- Host `localhost`
- Port `5432`

With pgcli, you'll need to run this to connect:

```bash
pgcli -h localhost -p 5432 -u postgres -d postgres
```

Run these query to create the Postgres landing zone for the first events and windows:

```sql 
CREATE TABLE processed_events (
    test_data INTEGER,
    event_timestamp TIMESTAMP
);

CREATE TABLE processed_events_aggregated (
    event_hour TIMESTAMP,
    test_data INTEGER,
    num_hits INTEGER 
);
```

## Question 1: Redpanda version

Now let's find out the version of redpandas. 

For that, check the output of the command `rpk help` _inside the container_. The name of the container is `redpanda-1`.

Find out what you need to execute based on the `help` output.

## Solution

To get inside the container we need to execute

```bash
docker exec -it redpanda-1 bash
```
then we execute

```bash
rpk version
```
The output is **v24.2.18**


## Question 2. Creating a topic

Before we can send data to the redpanda server, we
need to create a topic. We do it also with the `rpk`
command we used previously for figuring out the version of 
redpandas.

Read the output of `help` and based on it, create a topic with name `green-trips` 

## Solution

In redpanda container we need to execute

```bash
rpk topic create green-trips
```
The output is 
TOPIC        STATUS
green-trips  OK


## Question 3. Connecting to the Kafka server

We need to make sure we can connect to the server, so
later we can send some data to its topics

First, let's install the kafka connector (up to you if you
want to have a separate virtual environment for that)

```bash
pip install kafka-python
```

You can start a jupyter notebook in your solution folder or
create a script

Let's try to connect to our server, please see `kafka_connection_test.py`

The output of the 

```bash
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=bootstrap-0 host=localhost:9092 <connecting> [IPv6 ('::1', 9092, 0, 0)]>: connecting to localhost:9092 [('::1', 9092, 0, 0) IPv6]
INFO:kafka.conn:Broker version identified as 2.6
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=bootstrap-0 host=localhost:9092 <checking_api_versions_recv> [IPv6 ('::1', 9092, 0, 0)]>: Connection complete.
INFO:__main__:Successfully connected to Kafka!
Connection status: True
```
Last command is **Connection status: True** 

## Question 4: Sending the Trip Data

Now we need to send the data to the `green-trips` topic

Read the data, and keep only these columns:

* `'lpep_pickup_datetime',`
* `'lpep_dropoff_datetime',`
* `'PULocationID',`
* `'DOLocationID',`
* `'passenger_count',`
* `'trip_distance',`
* `'tip_amount'`

Now send all the data using `send_taxi_data.py`

The full output

```log
INFO:__main__:Preparing taxi data...
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=bootstrap-0 host=localhost:9092 <connecting> [IPv6 ('::1', 9092, 0, 0)]>: connecting to localhost:9092 [('::1', 9092, 0, 0) IPv6]
INFO:kafka.conn:Broker version identified as 2.6
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=bootstrap-0 host=localhost:9092 <checking_api_versions_recv> [IPv6 ('::1', 9092, 0, 0)]>: Connection complete.
INFO:__main__:Starting to send 476386 records to Kafka
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=1 host=localhost:9092 <connecting> [IPv6 ('::1', 9092, 0, 0)]>: connecting to localhost:9092 [('::1', 9092, 0, 0) IPv6]
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=1 host=localhost:9092 <checking_api_versions_send> [IPv6 ('::1', 9092, 0, 0)]>: Connection complete.
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=bootstrap-0 host=localhost:9092 <connected> [IPv6 ('::1', 9092, 0, 0)]>: Closing connection. 
INFO:__main__:Sent 10000/476386 records
INFO:__main__:Sent 20000/476386 records
INFO:__main__:Sent 30000/476386 records
INFO:__main__:Sent 40000/476386 records
INFO:__main__:Sent 50000/476386 records
INFO:__main__:Sent 60000/476386 records
INFO:__main__:Sent 70000/476386 records
INFO:__main__:Sent 80000/476386 records
INFO:__main__:Sent 90000/476386 records
INFO:__main__:Sent 100000/476386 records
INFO:__main__:Sent 110000/476386 records
INFO:__main__:Sent 120000/476386 records
INFO:__main__:Sent 130000/476386 records
INFO:__main__:Sent 140000/476386 records
INFO:__main__:Sent 150000/476386 records
INFO:__main__:Sent 160000/476386 records
INFO:__main__:Sent 170000/476386 records
INFO:__main__:Sent 180000/476386 records
INFO:__main__:Sent 190000/476386 records
INFO:__main__:Sent 200000/476386 records
INFO:__main__:Sent 210000/476386 records
INFO:__main__:Sent 220000/476386 records
INFO:__main__:Sent 230000/476386 records
INFO:__main__:Sent 240000/476386 records
INFO:__main__:Sent 250000/476386 records
INFO:__main__:Sent 260000/476386 records
INFO:__main__:Sent 270000/476386 records
INFO:__main__:Sent 280000/476386 records
INFO:__main__:Sent 290000/476386 records
INFO:__main__:Sent 300000/476386 records
INFO:__main__:Sent 310000/476386 records
INFO:__main__:Sent 320000/476386 records
INFO:__main__:Sent 330000/476386 records
INFO:__main__:Sent 340000/476386 records
INFO:__main__:Sent 350000/476386 records
INFO:__main__:Sent 360000/476386 records
INFO:__main__:Sent 370000/476386 records
INFO:__main__:Sent 380000/476386 records
INFO:__main__:Sent 390000/476386 records
INFO:__main__:Sent 400000/476386 records
INFO:__main__:Sent 410000/476386 records
INFO:__main__:Sent 420000/476386 records
INFO:__main__:Sent 430000/476386 records
INFO:__main__:Sent 440000/476386 records
INFO:__main__:Sent 450000/476386 records
INFO:__main__:Sent 460000/476386 records
INFO:__main__:Sent 470000/476386 records
INFO:__main__:Finished sending 476386 records in 84.16 seconds
INFO:__main__:Average speed: 5660.38 records/second
INFO:kafka.conn:<BrokerConnection client_id=kafka-python-producer-1, node_id=1 host=localhost:9092 <connected> [IPv6 ('::1', 9092, 0, 0)]>: Closing connection. 
Total time taken: 84.16 seconds
```

It took **84.16 seconds** to send the entire dataset and flush.


## Question 5: Build a Sessionization Window (2 points)

Now we have the data in the Kafka stream. It's time to process it.

* Copy `aggregation_job.py` and rename it to `session_job.py`
* Have it read from `green-trips` fixing the schema
* Use a [session window](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/datastream/operators/windows/) with a gap of 5 minutes
* Use `lpep_dropoff_datetime` time as your watermark with a 5 second tolerance

At first we need to add our script to docker container

```bash
docker cp session_job.py flink-jobmanager:/tmp/session_job.py
```

Then we should execute this script inside docker container

```bash
sudo docker exec -it flink-jobmanager flink run -py /tmp/session_job.py
```

In order to get pickup and drop off locations that have the longest unbroken streak of taxi trips we
will execute the query

```sql
with streak_analysis as (
	select
		PULocationID,
		DOLocationID,
		window_start,
		window_end,
		num_trips,
		EXTRACT(EPOCH from (window_end - window_start)) as session_duration
	from taxi_sessions
)
select
	PULocationID,
	DOLocationID,
	window_start,
	window_end,
	num_trips,
	session_duration / 60 as duration_minutes
from streak_analysis
order by session_duration desc
limit 10;
```

We got that **74,75** id's are the answer.
