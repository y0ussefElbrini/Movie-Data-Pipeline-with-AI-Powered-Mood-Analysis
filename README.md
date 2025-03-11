# 🎬 Movie Data Pipeline with AI-Powered Mood Analysis

## 🚀 Project Overview

![Project pipeline](docs/pipeline1.png)

This project is a **cloud-based data pipeline** that ingests, processes, and analyzes movie data from The Movie Database (TMDb) API. The workflow automates the extraction, transformation, and loading (ETL) of movie information into Google Cloud Platform (GCP), and enhances it using **AI-powered mood classification** with Vertex AI.

### **🔹 Key Features**
✅ **Automated ETL Pipeline**: Uses **Airflow** to extract movie data from the TMDb API and load it into **Google Cloud Storage (GCS)** and **BigQuery**.  
✅ **Cloud Infrastructure with Terraform**: All cloud resources are provisioned using **Terraform**, ensuring reproducibility and scalability.  
✅ **AI-powered Mood Classification**: **Vertex AI** and **Generative AI** analyze movie overviews to classify their mood (e.g., Happy, Intense, Dark) and store the results in BigQuery.  
✅ **Interactive Streamlit App**: Users can explore movies and receive AI-driven recommendations based on mood.  

---

## 📊 **System Architecture**
The architecture consists of three main layers:
1. **Data Ingestion (ETL Pipeline)**
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
- **Docker & Docker Compose** (for running Airflow locally)
- **Terraform** (for provisioning cloud infrastructure)

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