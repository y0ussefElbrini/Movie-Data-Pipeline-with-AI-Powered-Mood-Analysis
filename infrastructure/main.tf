terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  # Configuration options
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "movie_data_lake" {
  name          = var.gcs_bucket_name
  location      = var.location

}

resource "google_bigquery_dataset" "movies_dataset" {
  dataset_id = "movies"
  project    = var.project
  location   = var.location
}

resource "google_bigquery_table" "raw_movies" {
  dataset_id = google_bigquery_dataset.movies_dataset.dataset_id
  table_id   = "raw_movies"

  schema = file("${path.module}/schemas/raw_movies.json")

  time_partitioning {
    type = "DAY"
    field= "release_date"
  }
}


resource "google_bigquery_table" "raw_movies_temp" {
  dataset_id = google_bigquery_dataset.movies_dataset.dataset_id
  table_id   = "raw_movies_temp"
  schema     = file("${path.module}/schemas/raw_movies.json")

  deletion_protection = false
}
