import streamlit as st
from google.cloud import bigquery
import pandas as pd
import os

# 🔐 Auth GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path-to/my-creds.json"  # ← Update path


# 🔹 CONFIGURATION GCP
PROJECT_ID = "name_of_your_project"   #change to your project name
DATASET_NAME = "movies"
TABLE_NAME = "raw_movies_cleaned"

# 🔹 Fonction pour récupérer les films depuis BigQuery
def get_movies():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT movie_id, title, overview, mood, mood_score
        FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
        WHERE mood IS NOT NULL AND mood_score IS NOT NULL
        ORDER BY mood_score DESC
    """
    query_job = client.query(query)
    df = query_job.to_dataframe()
    return df

# 🔹 Interface Streamlit
st.set_page_config(page_title="🎬 Movie Mood Recommender", layout="wide")

# 🎨 En-tête de l'application
st.title("🎭 Movie Mood Recommender")
st.markdown("🔍 **Trouvez un film en fonction de votre humeur !**")

# 📊 Charger les films
movies_df = get_movies()

# 📌 Sélection du "Mood"
moods = movies_df["mood"].unique().tolist()
selected_mood = st.selectbox("💡 Choisissez votre humeur :", moods)

# 🎯 Filtrer les films correspondant au mood sélectionné
filtered_movies = movies_df[movies_df["mood"] == selected_mood].sort_values(by="mood_score", ascending=False).head(10)

# 📌 Affichage des films recommandés
st.subheader(f"📽️ Films recommandés pour un mood **{selected_mood}**")

if not filtered_movies.empty:
    for index, row in filtered_movies.iterrows():
        st.markdown(f"### 🎬 **{row['title']}**")
        st.markdown(f"📝 {row['overview']}")
        st.markdown(f"🧠 Mood: {row['mood']} | 🎚️ Score: {row['mood_score']}/100")
        st.markdown("---")
else:
    st.warning("😢 Aucun film trouvé pour ce mood.")

# 🎉 Footer
st.markdown("🚀 *Développé avec ❤️ par Youssef EL BRINI*")
