import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
import duckdb

@dlt.resource(name="ny_taxi_db")
def ny_taxi_api():
    base_url = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
    
    client = RESTClient(
        base_url=base_url,
        paginator=PageNumberPaginator(
            base_page=1,
            total_path=None
        )
    )

    
    for page in client.paginate("data_engineering_zoomcamp_api"): # Pass page_size here
        yield page

# Create and run the pipeline
pipeline = dlt.pipeline(
    pipeline_name="ny_taxi_pipe",
    destination="duckdb",
    dataset_name="ny_taxi_dt"
)

#load_info = pipeline.run(ny_taxi_api(), table_name="rides", write_disposition="replace")
#print(load_info)

# Query the data
conn = duckdb.connect(database='ny_taxi_pipe.duckdb', read_only=True)
#result = conn.execute("SELECT COUNT(*) FROM ny_taxi_data.ny_taxi_data").fetchdf()
#print(result)

# Set search path to the dataset
conn.sql(f"SET search_path = '{pipeline.dataset_name}'")

# Describe the dataset
conn.sql("DESCRIBE").df()

df = pipeline.dataset(dataset_type="default").rides.df()
df

with pipeline.sql_client() as client:
    res = client.execute_sql(
            """
            SELECT
            AVG(date_diff('minute', trip_pickup_date_time, trip_dropoff_date_time))
            FROM rides;
            """
        )
    # Prints column values of the first row
    print(res)

conn.close()