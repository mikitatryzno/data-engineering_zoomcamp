# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL

## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`. What's the version of `pip` in the image?

## Solution Steps

Modify the Dockerfile with the following code
```bash
FROM python:3.12.8

RUN pip install pandas

ENTRYPOINT ["bash"]
```

Run the following commands in VS Code Terminal with bash selected

```bash
$ docker build -t test:pandas . 
$ docker run -it test:pandas
```

When running the created Container we will see the following

```bash
root@a29cada48356:/# python
Python 3.12.8 (main, Jan 14 2025, 05:32:36) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pip
>>> pip.__version__
'24.3.1'
>>> 
root@a29cada48356:/# exit
exit
```

## Answer

**24.3.1**

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

If there are more than one answers, select only one of them

## Solution Steps

Since pgAdmin needs to connect to PostgreSQL database and both are defined within the same Docker Compose file, pgAdmin can use **db** as the host name to connect to the PostgreSQL.

pgAdmin should use port **5432**, which is the internal port that PostgreSQL listens on within container.

## Answer

**db:5432**


##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

## Solution Steps

We need run the following sql script

```sql
SELECT 
  SUM(CASE WHEN trip_distance <= 1 THEN 1 ELSE 0 END) AS "Up to 1 mile",
  SUM(CASE WHEN trip_distance > 1 AND trip_distance <= 3 THEN 1 ELSE 0 END) AS "Between 1 and 3 miles",
  SUM(CASE WHEN trip_distance > 3 AND trip_distance <= 7 THEN 1 ELSE 0 END) AS "Between 3 and 7 miles",
  SUM(CASE WHEN trip_distance > 7 AND trip_distance <= 10 THEN 1 ELSE 0 END) AS "Between 7 and 10 miles",
  SUM(CASE WHEN trip_distance > 10 THEN 1 ELSE 0 END) AS "Over 10 miles"
FROM "green_tripdata_201910"
WHERE lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01';
```

## Answer

I am getting the following answers

"Up to 1 mile" - 104830
"Between 1 and 3 miles" - 198995
"Between 3 and 7 miles" - 109642
"Between 7 and 10 miles" - 27686	
"Over 10 miles" - 35201

These results are closer to those ones

**104,838;  199,013;  109,645;  27,688;  35,202**


## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

## Solution Steps

We need run the following sql script

```sql
SELECT lpep_pickup_datetime::date AS pickup_date
FROM (
  SELECT lpep_pickup_datetime, trip_distance,
         ROW_NUMBER() OVER (PARTITION BY lpep_pickup_datetime::date ORDER BY trip_distance DESC) AS row_num
  FROM green_tripdata_201910
) AS subquery
WHERE row_num = 1
ORDER BY trip_distance DESC
LIMIT 1;
```

## Answer

**2019-10-31**


## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
## Solution Steps

We need run the following sql script

```sql
SELECT z."Zone", SUM(gtd.total_amount) AS total_amount
FROM green_tripdata_201910 gtd
JOIN zones z ON gtd."PULocationID" = z."LocationID"
WHERE gtd.lpep_pickup_datetime::date = '2019-10-18'
GROUP BY z."Zone"
HAVING SUM(gtd.total_amount) > 13000
ORDER BY total_amount DESC
LIMIT 3;
```

## Answer

"East Harlem North" - 18686.68000000009
"East Harlem South" - 16797.260000000075
"Morningside Heights" - 13029.79000000003

**East Harlem North, East Harlem South, Morningside Heights**


## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
named "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

## Solution Steps

We need run the following sql script

```sql
SELECT z2."Zone" AS dropoff_zone, 
MAX(gtd.tip_amount) AS largest_tip
FROM green_tripdata_201910 gtd
JOIN zones z1 ON gtd."PULocationID" = z1."LocationID"
JOIN zones z2 ON gtd."DOLocationID" = z2."LocationID"
WHERE z1."Zone" = 'East Harlem North' AND gtd.lpep_pickup_datetime::date >= '2019-10-01' AND gtd.lpep_pickup_datetime::date < '2019-11-01'
GROUP BY z2."Zone"
ORDER BY "largest_tip" DESC
LIMIT 1;
```

## Answer

"JFK Airport" - 87.3

**JFK Airport**


## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`


## Solution Steps

`terraform init` is used to initialize a working directory containing terraform configuration, downloads necessary provider plugins, and sets up the backend configation.

`terraform apply -auto-approve` is used to apply the changes required to reach the desired state of the configuration, or the pre-determined set of actions generated by Terraform plan. The `auto-approve` flag skips interactive approval of plan before applying.

`terraform destroy` is used to destroy the Terraform-managed infrastructure. It terminates resources managed by Terraform project.

## Answer

**terraform init, terraform apply -auto-approve, terraform destroy**

