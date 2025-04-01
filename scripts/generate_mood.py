import re
import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import bigquery

# 🔐 Auth GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path-to/my-creds.json"  # ← Update path

# 🔹 CONFIGURATION GCP
PROJECT_ID = "name_of_your_project" #change to your project name
LOCATION = "europe-west9" #change to your location name
MODEL_NAME = "gemini-pro"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

#  Ensure the columns exist in BigQuery
def ensure_columns_exist():
    """Checks and adds 'mood' and 'mood_score' columns if missing."""
    client = bigquery.Client(project=PROJECT_ID)

    query = """
        SELECT column_name 
        FROM `movies.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'raw_movies_cleaned'
        AND column_name IN ('mood', 'mood_score')
    """

    existing_columns = {row["column_name"] for row in client.query(query).result()}

    if "mood" not in existing_columns or "mood_score" not in existing_columns:
        print("⚠️ Missing columns detected! Adding 'mood' and 'mood_score'...")

        alter_query = """
            ALTER TABLE `movies.raw_movies_cleaned`
            ADD COLUMN IF NOT EXISTS mood STRING,
            ADD COLUMN IF NOT EXISTS mood_score INT64;
        """
        client.query(alter_query).result()
        print("✅ Columns 'mood' and 'mood_score' added successfully!")
    else:
        print("✅ Columns already exist. No changes needed.")

# Fetch movies from BigQuery that need mood analysis
def get_movies_from_bigquery():
    """Retrieve movies without mood analysis from BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)
    query = """
        SELECT movie_id, title, genres, overview
        FROM `movies.raw_movies_cleaned`
        WHERE overview IS NOT NULL AND overview != ''
        AND (mood IS NULL OR mood_score IS NULL)  -- Ignore already processed movies
        LIMIT 10
    """
    return client.query(query).result()

# Analyze movie mood using Gemini-Pro
def analyze_movie_mood(overview):
    """Analyzes the emotional tone of a movie overview using Vertex AI."""
    model = GenerativeModel(model_name=MODEL_NAME)

    prompt = f"""
    Analyze the emotional tone of the following movie description and classify its predominant mood.

    Description: "{overview}"

    Return only one mood classification among: Happy, Sad, Intense, Dark, Nostalgic, Uplifting.
    Give a mood score from 0 to 100, where 100 represents extreme intensity.

    Format the response strictly as:
    Mood: <mood>, Score: <score>
    """

    response = model.generate_content(prompt)

    if response.text:
        response_text = response.text.strip()
        print(f"🔹 AI Response: {response_text}")  # Debugging

        # Extract mood and score using regex
        mood_match = re.search(r"Mood:\s*(\w+)", response_text)
        score_match = re.search(r"Score:\s*(\d+)", response_text)

        if mood_match and score_match:
            mood = mood_match.group(1)
            score = int(score_match.group(1))
            return mood, score
        else:
            print("⚠️ Unexpected AI response format. Assigning default values.")
            return "Neutral", 50

    print("⚠️ No valid AI response. Assigning default values.")
    return "Neutral", 50  # Fallback values

# Update BigQuery with mood scores
def update_movie_mood_in_bigquery(movie_id, mood, score):
    """Updates the mood and mood_score of a movie in BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)

    query = """
        UPDATE `movies.raw_movies_cleaned`
        SET mood = @mood, mood_score = @score
        WHERE movie_id = @movie_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("movie_id", "INT64", movie_id),
            bigquery.ScalarQueryParameter("mood", "STRING", mood),
            bigquery.ScalarQueryParameter("score", "INT64", score),
        ]
    )

    client.query(query, job_config=job_config).result()
    print(f"✅ Updated movie {movie_id} with Mood: {mood} (Score: {score})")

# Run the full pipeline
if __name__ == "__main__":
    # Step 1️⃣: Ensure mood columns exist in BigQuery
    ensure_columns_exist()

    # Step 2️⃣: Fetch movies needing analysis
    print("🚀 Fetching movies from BigQuery...")
    movies = get_movies_from_bigquery()

    for movie in movies:
        movie_id = movie["movie_id"]
        title = movie["title"]
        overview = movie["overview"]

        print(f"\n🎬 **{title}**")
        mood, mood_score = analyze_movie_mood(overview)
        print(f"🧠 Mood: {mood} | 🎚️ Score: {mood_score}")

        # Step 3️⃣: Update BigQuery
        update_movie_mood_in_bigquery(movie_id, mood, mood_score)

    print("\n🎉 All moods have been updated in BigQuery!")
