## Module 3 Homework

<b><u>Important Note:</b></u> <p> For this homework we will be using the Yellow Taxi Trip Records for **January 2024 - June 2024 NOT the entire year of data** 
Parquet Files from the New York
City Taxi Data found here: </br> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page </br>

<b>BIG QUERY SETUP:</b></br>
Create an external table using the Yellow Taxi Trip Records. </br>
Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). </br>
<u>NOTE:</u> You will need to use the PARQUET option files when creating an External Table</br>

## Question 1:
*What is count of records for the 2024 Yellow Taxi Data?*

In order to get the result we need to execure the following query on created external table
```sql
select count (*)
from gcp_project_name.gcp_bq_dataset_name.external_table_name
```
And we are getting **20,332,093**

## Question 2:
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.</br> 
*What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?*

In order to get the `Bytes processed` for the query we need to look at `Job information` section in `Query results`. 

While running the query 

```sql
select count (distinct PULocationID)
from gcp_project_name.gcp_bq_dataset_name.external_table_name
```

```sql
select count (distinct PULocationID)
from gcp_project_name.gcp_bq_dataset_name.regular_table_name
```

We get  **0 MB for the External Table and 155.12 MB for the Materialized Table**

## Question 3:
Write a query to retrieve the PULocationID form the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. *Why are the estimated number of Bytes different?*

In a columnar storage system like BigQuery, the cost and data processed are directly tier to the number and nature of columns being accessed. That's why correct exlanation for why quering two columns (`PULocationID` and `DOLocationID `) results in a higher estimated number of bytes processed compared to quering one column (`PULocationID`) is

**BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.**

## Question 4:
*How many records have a fare_amount of 0?*

In order to answer this question we need to execute the query

```sql
select count (*)
from gcp_project_name.gcp_bq_dataset_name.regular_table_name
where fare_amount = 0
```

We do get the following result **8,333**

## Question 5:
*What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)?*</br>

When we need to optimize a table in BQ, especially when you know the common filters and sorting mechanisms of your queries, partiotioning and clustering can significally improve performance and reduce costs.
Given that query will always filter based on `tpep_dropoff_datetime` and order results by `VendorID`, the best strategy is to **Partition by tpep_dropoff_timedate and Cluster on VendorID**</br>

Below is SQL DDL query</br>
```sql
CREATE TABLE gcp_project_name.gcp_bq_dataset_name.optimized_table_name
PARTITION BY DATE(tpep_dropoff_timedate)
CLUSTER BY VendorID AS
SELECT *
FROM gcp_project_name.gcp_bq_dataset_name.regular_table_name
```

## Question 6:
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_timedate
03/01/2024 and 03/15/2024 (inclusive)</br>

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. *What are these values?* </br>

Choose the answer which most closely matches.</br> 

Below is the queries on partitioned table</br> 
```sql
select distinct VendorID
from gcp_project_name.gcp_bq_dataset_name.optimized_table_name
where tpep_dropoff_datetime BETWEEN '2024-03-01 00:00:00' and '2014-03-15 23:59:59'
```
and non-partitioned one</br> 
```sql
select distinct VendorID
from gcp_project_name.gcp_bq_dataset_name.regular_table_name
where tpep_dropoff_datetime BETWEEN '2024-03-01 00:00:00' and '2014-03-15 23:59:59'
```

We get **310.24 MB for non-partitioned table and 26.84 MB for the partitioned table**

## Question 7: 
*Where is the data stored in the External Table you created?*

When we create an external table in BQ, the data itself is not stored in BQ. BQ accesses data directly from its original location, since we put Parquet files for Yellow Taxi Trips for Jan-Jun 2024 period in GCP Bucket, the correct answer is **GCP Bucket**

## Question 8:
*Is it the best practice in Big Query to always cluster your data?*: **False**

Clustering improves query performance and reduce costs by properly organizing data, however it is not always necessary and beneficial.

## Question 9:
No Points: Write a `SELECT count(*)` query FROM the materialized table you created. *How many bytes does it estimate will be read? Why?*

Since materialized view is precomputed, it stores results based on underlying base table and picks up result from cache of previous queries, total bytes will be 0.