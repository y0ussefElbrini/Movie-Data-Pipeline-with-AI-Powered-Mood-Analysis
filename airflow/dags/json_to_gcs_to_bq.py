from datetime import datetime, timedelta
import requests
import json
from airflow.models import Variable
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow import DAG
from airflow.operators.python import PythonOperator



GCS_CONN_ID = 'google_cloud_default'
BUCKET = 'unique_name_of_your_bucket' #change to the name of the bucket specified in variables.tf
DATASET_NAME = 'movies' #change to the name of the dataset specified in variables.tf
TABLE_NAME = 'raw_movies'

def fetch_genres(**kwargs):
    
    
    if Variable.get("genres_dict", default_var=None):
        print("Genres already stored in Airflow Variable!!")
        return
    
    api_key = Variable.get('API_key')
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        genres_data = response.json()
        genres_dict = {genre['id']:genre['name'] for genre in genres_data['genres']}
        
        Variable.set("genres_dict", json.dumps(genres_dict))
        print("Genres successfully stored in Airflow Variable!!")

    else:
        print(f"ERROR: Failed to fetch genres! Status Code: {response.status_code}")
        

def get_movies(**kwargs):
    api_key = Variable.get('API_key')
    if not api_key:
        raise ValueError("❌ ERROR: API Key is missing in Airflow Variables!")

    base_url = "https://api.themoviedb.org/3/discover/movie"
    page = 1
    transformed_data = []
    
    year = kwargs.get('ds', '2000').split('-')[0]  # Ensure ds exists
    genres_dict = Variable.get("genres_dict", default_var=None)
    
    if not genres_dict:
        raise ValueError("❌ ERROR: Genres dictionary is missing! Ensure `fetch_genres` task runs first.")
    
    genres_dict = json.loads(genres_dict)  # Convert to dictionary

    # First request to get `total_pages`
    response = requests.get(f"{base_url}?api_key={api_key}&primary_release_year={year}&page={page}")
    
    if response.status_code != 200:
        print(f"❌ ERROR: Failed to fetch movies for {year}! Status Code: {response.status_code}")
        return None  # Stop execution if API call fails

    movies_data = response.json()
    total_pages = min(movies_data.get("total_pages", 1), 500)  # Prevent exceeding 500 pages

    while page <= total_pages:
        response = requests.get(f"{base_url}?api_key={api_key}&primary_release_year={year}&page={page}")

        if response.status_code != 200:
            print(f"❌ ERROR: Page {page} failed for {year}, stopping pagination.")
            break  # Stop if API returns an error

        movies_data = response.json()

        for movie in movies_data.get("results", []):
            transformed_data.append({
                "movie_id": movie["id"],
                "title": movie["title"],
                "release_year": int(year),
                "release_date": movie.get("release_date", ""),
                "original_language": movie.get("original_language", ""),
                "overview": movie.get("overview", ""),
                "budget": movie.get("budget", 0),
                "revenue": movie.get("revenue", 0),
                "popularity": movie["popularity"],
                "vote_average": movie["vote_average"],
                "vote_count": movie["vote_count"],
                "adult": movie["adult"],
                "genres": [genres_dict.get(str(genre_id), "Unknown") for genre_id in movie.get("genre_ids", [])]
            })

        page += 1

    if not transformed_data:
        print(f"⚠️ WARNING: No movies found for {year}!")
        return None  # Prevent Airflow from proceeding with empty data

    # ✅ Afficher uniquement un résumé propre
    print(f"✅ {len(transformed_data)} movies fetched for {year}")

    return transformed_data

def upload_to_gcs(**kwargs):
    year = kwargs['ds'].split('-')[0]
    ti = kwargs['ti']
    data_to_upload = ti.xcom_pull(task_ids='get_movies')
        
    json_to_upload = "\n".join(json.dumps(record) for record in data_to_upload)# this transform a python dictionary to json
    
    gcs_hook = GCSHook(gcp_conn_id=GCS_CONN_ID)
    gcs_hook.upload(
        bucket_name=BUCKET,
        data=json_to_upload,
        object_name=f"movies_{year}.json"
    )
    print(f"Successfully uploaded movies_{year}.json to GCS.")


with DAG(
    dag_id="upload_to_gcs_dag",
    start_date=datetime(2000, 1, 1),
    schedule_interval='@yearly',
    catchup=True,
    max_active_runs=1
) as dag:
    

    fetch_genres_task = PythonOperator(
        task_id="fetch_genres",
        python_callable=fetch_genres
    )

    get_movies_task = PythonOperator(
        task_id="get_movies",
        python_callable=get_movies,
        provide_context=True,
    )
    upload_task = PythonOperator(
        task_id='upload_to_gcs',
        python_callable=upload_to_gcs,

    )
    load_to_bq_task = GCSToBigQueryOperator(
        task_id="gcs_to_bigquery_temp",
        bucket=BUCKET,
        source_objects=["movies_{{ ds.split('-')[0] }}.json"],
        destination_project_dataset_table=f"{DATASET_NAME}.raw_movies_temp",  # ✅ Table temporaire
        schema_fields=[
            {"name": "movie_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "release_year", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "release_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "original_language", "type": "STRING", "mode": "NULLABLE"},
            {"name": "overview", "type": "STRING", "mode": "NULLABLE"},
            {"name": "budget", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "revenue", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "popularity", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "vote_average", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "vote_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "adult", "type": "BOOLEAN", "mode": "NULLABLE"},
            {"name": "genres", "type": "STRING", "mode": "REPEATED"}
        ],
        write_disposition="WRITE_TRUNCATE",  # ✅ Écrase uniquement les données temporaires
        gcp_conn_id=GCS_CONN_ID,
        source_format="NEWLINE_DELIMITED_JSON"
)
    merge_task = BigQueryInsertJobOperator(
    task_id="merge_movies",
    gcp_conn_id=GCS_CONN_ID,
    configuration={
        "query": {
            "query": """
                MERGE INTO `terraform-demo-448809.movies.raw_movies` AS target
                USING `terraform-demo-448809.movies.raw_movies_temp` AS source
                ON target.movie_id = source.movie_id
                WHEN MATCHED THEN
                    UPDATE SET
                        target.title = source.title,
                        target.release_date = source.release_date,
                        target.budget = source.budget,
                        target.revenue = source.revenue,
                        target.popularity = source.popularity,
                        target.vote_average = source.vote_average,
                        target.vote_count = source.vote_count,
                        target.genres = source.genres
                WHEN NOT MATCHED THEN
                    INSERT (movie_id, title, release_date, budget, revenue, popularity, vote_average, vote_count, genres)
                    VALUES (source.movie_id, source.title, source.release_date, source.budget, source.revenue, source.popularity, source.vote_average, source.vote_count, source.genres);
            """,
            "useLegacySql": False,
        }
    },
)
    
    fetch_genres_task >> get_movies_task >> upload_task >> load_to_bq_task >> merge_task