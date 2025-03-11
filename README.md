# 🎬 Movie Data Pipeline with AI-Powered Mood Analysis

## 🚀 Project Overview

![Project pipeline](docs/pipeline1.png)

This project is a **cloud-based data pipeline** that ingests, processes, and analyzes movie data from The Movie Database (TMDb) API. The workflow automates the extraction, transformation, and loading (ETL) of movie information into Google Cloud Platform (GCP), and enhances it using **AI-powered mood classification** with Vertex AI.

### **🔹 Key Features**
✅ **Automated ETL Pipeline**: Uses **Airflow** to extract movie data from the *TMDb API* and load it into **Google Cloud Storage (GCS)** and **BigQuery**.  
✅ **Cloud Infrastructure with Terraform**: All cloud resources are provisioned using **Terraform**, ensuring reproducibility and scalability.  
✅ **AI-powered Mood Classification**: **Vertex AI** and **Generative AI** analyze movie overviews to classify their mood (e.g., Happy, Intense, Dark) and store the results in BigQuery.  
✅ **Interactive Streamlit App**: Users can explore movies and receive AI-driven recommendations based on mood.  

---

## 📊 **System Architecture**
The architecture consists of three main layers:
1. **Data Ingestion (ETL Pipeline) : orchestrated by Airflow**
   - Airflow fetches movie data from TMDb API.
   - Data is stored in **Google Cloud Storage (GCS)** as JSON files.
   - The data is loaded into **BigQuery** for further processing.

2. **AI Processing**
   - **Vertex AI** analyzes movie overviews using a **Large Language Model (LLM)**.
   - Each movie receives a **mood classification** (e.g., Happy, Intense, Nostalgic).
   - The processed data is updated in BigQuery.

3. **Frontend - Movie Recommendation App**
   - A **Streamlit app** allows users to search for movies.
   - Users receive **AI-powered movie recommendations** based on mood classification.
   - Data is fetched in real-time from BigQuery.

---

## 🛠️ **Prerequisites**
Before setting up the project, ensure you have the following:

### **1️⃣ Install Required Tools**
#### 🔹  **Python**
Make sure you have **Python 3.8+** installed. You can download it from the official website: [Download Python](https://www.python.org/downloads/)
#### 🔹  **Docker & Docker Compose**
Docker is required to run **Airflow** and other services locally. Install **Docker** and **Docker Compose** from the official website:[Install Docker & Docker Compose](https://docs.docker.com/get-docker/)
After installation, verify that Docker is running:

```sh
docker --version
docker compose version
```
#### 🔹  **Terraform**
Terraform is used for cloud **infrastructure provisioning**. You can install it using `pip`:
```sh
pip install terraform
```
Alternatively, you can download Terraform from the official website: [Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
After installation, verify Terraform:
```sh
terraform --version
```


### **2️⃣ Create a TMDb API Key**
- Sign up at **[TMDb Developers](https://developer.themoviedb.org/docs/getting-started)**
- Generate an **API Key** to access the movie database.
- Save the API key for later use in **Airflow variables**.

### **3️⃣ Set Up Google Cloud Platform (GCP)**
1. **Create a GCP Project**:  
   - Go to **[Google Cloud Console](https://console.cloud.google.com/)** and create a new project.

2. **Create a Service Account**:  
   - Navigate to **IAM & Admin > Service Accounts**.
   - Create a service account and assign the following roles:
     - **BigQuery Admin**
     - **Storage Admin**
     - **Vertex AI User**
   - Generate a **JSON key file** for authentication.

3. **Enable Required APIs**:  
   - Go to **APIs & Services** in GCP and enable:
     - **BigQuery API**
     - **Cloud Storage API**
     - **Vertex AI API**

4. **Store Credentials in the Project**:
   - Copy the **JSON key file content** into:
     - `airflow/keys/my-creds.json`
     - `infrastructure/keys/my-creds.json`
   - This allows both **Airflow and Terraform** to authenticate with GCP.


---

## 🚀 **Getting Started**
### **1️⃣ Clone the Repository**
```sh
git clone  
cd movie-recommendation-project
```

## **2️⃣ Setting Up Cloud Infrastructure with Terraform**

This project uses **Terraform** to provision the necessary cloud resources, including:

- **Google Cloud Storage (GCS)** for data storage
- **BigQuery** for data warehousing and processing
- **Vertex AI** for machine learning models

### **🔹 Step 1: Navigate to the Infrastructure Folder**
First, navigate to the **infrastructure** directory:

```sh
cd infrastructure
```
### **🔹 Step 2: Navigate to the Infrastructure Folder**
Before initializing Terraform, you need to edit the `variables.tf` file to customize the settings for your Google Cloud Platform (GCP) project.
Make sure to replace:
- `name_of_your_project` with your GCP project ID.
- `unique_name_of_your_bucket` with a unique name for your GCS bucket.
- `name_of_your_dataset` with a unique name for your BigQuery dataset.
- `./keys/my-creds.json` Ensure the service account key exists in the correct path.

### **🔹 Step 3: Initialize and Deploy Infrastructure**
Run the following Terraform commands inside the infrastructure folder to deploy the resources:

1️⃣ Initialize Terraform
```sh
terraform init
```
This command downloads necessary Terraform providers and dependencies.

2️⃣ Plan the Deployment
```sh
terraform plan
```
This step previews the resources Terraform will create.

3️⃣ Apply Changes and Create Resources
```sh
terraform apply
```
Terraform will prompt for confirmation. Type yes to proceed.

4️⃣ Verify the Infrastructure After deployment, you can verify that the resources are created by running:

```sh
terraform show
```
You can also check your GCP Cloud Storage (GCS) and BigQuery console to confirm the setup.


### **3️⃣ Setting Up Airflow for Data Orchestration**

This project uses **Apache Airflow** to orchestrate the data pipeline, ensuring smooth ingestion from **TMDB API** to **Google Cloud Storage (GCS)** and **BigQuery**.

### **🔹 Step 1: Navigate to the Airflow Folder**
First, move to the **Airflow directory**:

```sh
cd airflow
```
### **🔹 Step 2: Configure Airflow Variables**

Airflow requires Google Cloud credentials to interact with GCS, BigQuery, and Vertex AI.

1️⃣ Ensure that the service account key is available at:

- `airflow/keys/my-creds.json`

2️⃣ Set the environment variable in Airflow containers: Open the docker-compose.yaml file and add the following line inside environment for each container that needs access:

```yaml
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/my-creds.json
```

3️⃣ Mount the keys/ directory in Docker volumes: Ensure the following line is in docker-compose.yaml:

```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/keys:/opt/airflow/keys
```

### **🔹 Step 3: Start Airflow Services**

Run the following commands inside the airflow/ directory:

1️⃣ **Initialize the Airflow database**

```sh
docker-compose up airflow-init
```

2️⃣ **Start all Airflow services**

```sh
docker-compose up -d
```

3️⃣ **Verify that all services are running**

```sh
docker ps
```

You should see the following containers running:

`airflow-webserver`
`airflow-scheduler`
`airflow-worker`
`airflow-triggerer`
`airflow-postgres`
`airflow-redis`

4️⃣ **Access the Airflow UI Open your browser and navigate to:**

```arduino
http://localhost:8080
```

Login with:

Username: `airflow`
Password: `airflow`

### **🔹 Step 4: Install Required Python Libraries in Airflow
Since Airflow runs in Docker containers, you need to install additional dependencies inside the running containers.

1️⃣ **Attach to the airflow-worker container (or any other relevant container):**

```sh
docker exec -it airflow-airflow-worker-1 /bin/bash
```

2️⃣ **Install required Python libraries:**

```sh
pip install google-cloud-bigquery google-cloud-storage google-cloud-aiplatform requests pandas
```

3️⃣ **Exit the container:**

```sh
exit
```

### **🔹 Step 5: Deploy the Airflow DAG
Your DAG (Directed Acyclic Graph) is responsible for:

- Extracting movie data from TMDB API.
- Storing it in Google Cloud Storage (GCS).
- Loading data into BigQuery for further processing.

1️⃣ **Copy your DAG file into the dags/ directory: Ensure your DAG is inside:**

```bash
airflow/dags/upload_to_gcs_dag.py
```
2️⃣ Trigger the DAG manually Go to Airflow UI (http://localhost:8080), navigate to the upload_to_gcs_dag DAG, and click "Trigger DAG".


### **🔹 Step 6: Stop and Restart Airflow
To stop all running services:

```bash
docker-compose down
```

To restart:

```bash
docker-compose up -d
```