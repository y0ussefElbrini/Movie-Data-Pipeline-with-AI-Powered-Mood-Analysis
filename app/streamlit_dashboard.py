import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import os

# 🔐 Auth GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path-to/my-creds.json"  # ← Update path

# 🎯 GCP Config
PROJECT_ID = "terraform-demo-448809"
DATASET_NAME = "movies"
TABLE_NAME = "raw_movies"

# 📥 Load data
@st.cache_data(ttl=3600)
def load_data():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT 
            movie_id, title, release_year, release_date,
            original_language, genres
        FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
        WHERE title IS NOT NULL
    """
    return client.query(query).to_dataframe()

# 🖥️ UI Layout
st.set_page_config(page_title="🎬 Movie Data Visualizations", layout="wide")
st.title("🎞️ Movie Data Visual Insights")
st.markdown("Visual exploration of movie metadata from BigQuery.")

df = load_data()
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

# ✅ First row: number of movies by release_year and release_date
col1, col2 = st.columns(2)

with col1:
    st.subheader("📆 Number of Movies by Release Year")
    year_counts = df["release_year"].value_counts().sort_index()
    fig1 = px.bar(
        x=year_counts.index,
        y=year_counts.values,
        labels={"x": "Release Year", "y": "Number of Movies"},
        title="Movies Released per Year"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🗓️ Number of Movies by Month")
    df["release_month"] = df["release_date"].dt.month
    month_counts = df["release_month"].value_counts().sort_index()
    fig2 = px.bar(
        x=month_counts.index,
        y=month_counts.values,
        labels={"x": "Month", "y": "Number of Movies"},
        title="Release Month Distribution"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ✅ Second row: genre and language distributions
col3, col4 = st.columns(2)

with col3:
    st.subheader("🎭 Most Common Genres")
    genre_counts = df.explode("genres")["genres"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    fig3 = px.bar(genre_counts.head(10), x="genre", y="count", title="Top 10 Genres")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🌍 Languages Distribution")
    lang_counts = df["original_language"].value_counts().reset_index()
    lang_counts.columns = ["language", "count"]
    fig4 = px.pie(lang_counts.head(10), names="language", values="count", title="Top Languages")
    st.plotly_chart(fig4, use_container_width=True)

# ✅ Footer
st.markdown("📊 *Powered by Streamlit, BigQuery & Google Cloud*")
