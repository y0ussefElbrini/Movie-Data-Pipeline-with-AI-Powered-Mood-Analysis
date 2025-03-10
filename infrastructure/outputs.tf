output "bigquery_dataset" {
  value = google_bigquery_dataset.movies_dataset.dataset_id
}

output "gcs_bucket_name" {
  value = google_storage_bucket.movie_data_lake.name
}
