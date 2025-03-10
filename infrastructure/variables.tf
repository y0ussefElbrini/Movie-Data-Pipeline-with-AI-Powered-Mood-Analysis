variable "credentials" {
  description = "My Credentials"
  default     = "./keys/my-creds.json" # the path to your service account credentials
}


variable "project" {
  description = "Project"
  default     = "name_of_your_project" # Choose the name of your project
}

variable "region" {
  description = "Resources Region"
  default     = "europe-west9" # you can choose another region
}

variable "location" {
  description = "Project Location"
  default     = "EU" # You can choose another location
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "demo_dataset" # Choose the name of your dataset

}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "unique_name_of_your_bucket" # You need to specify a globally unique name for your bucket

}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"

}