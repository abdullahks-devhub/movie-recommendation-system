import streamlit as st
import pickle
import pandas as pd
import requests

import gdown
import os

# Download similarity.pkl from Google Drive if not present
if not os.path.exists("similarity.pkl"):
    gdown.download(
        "https://drive.google.com/uc?id=YOUR_FILE_ID_HERE",
        "similarity.pkl",
        quiet=False
    )
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown("""
    <style>
        body { background-color: #0f0f0f; }
        .main { background-color: #141414; }

        .movie-card {
            background: linear-gradient(145deg, #1f1f1f, #2a2a2a);
            border-radius: 16px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
        }
        .movie-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 40px rgba(229, 9, 9, 0.4);
        }
        .movie-card img {
            width: 100%;
            border-radius: 12px;
            object-fit: cover;
            height: 280px;
        }
        .movie-title {
            color: #ffffff;
            font-size: 15px;
            font-weight: 700;
            margin-top: 10px;
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.3;
            min-height: 40px;
        }
        .movie-year {
            color: #e50914;
            font-size: 13px;
            font-weight: 500;
            margin-top: 4px;
            font-family: 'Segoe UI', sans-serif;
        }
        .section-title {
            color: #e50914;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 20px;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 1px;
        }
        .stSelectbox label {
            color: #aaaaaa !important;
            font-size: 15px;
        }
        div[data-testid="stSelectbox"] > div {
            background-color: #1f1f1f;
            border: 1px solid #e50914;
            border-radius: 8px;
            color: white;
        }
        .stButton > button {
            background: linear-gradient(135deg, #e50914, #b00610);
            color: white;
            font-weight: 700;
            font-size: 16px;
            padding: 10px 36px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #ff1a1a, #cc0000);
            transform: scale(1.04);
        }
        h1 {
            color: white !important;
            font-family: 'Segoe UI', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)


def fetch_poster_and_year(movie_id):
    """Fetch poster and release year using the TMDB movie ID."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": "594119c49605aab1692ba95bf4d36d66"}

    response = requests.get(url, params=params)
    data = response.json()

    # Poster
    poster_path = data.get("poster_path")
    poster_url = (
        "https://image.tmdb.org/t/p/w500/" + poster_path
        if poster_path
        else "https://via.placeholder.com/500x750?text=No+Image"
    )

    # Release year — safely extract from "release_date" e.g. "2009-12-18"
    release_date = data.get("release_date", "")
    year = release_date[:4] if release_date else "N/A"

    return poster_url, year


def recommend(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    movies_list_ext = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    for i in movies_list_ext:
        row = movies.iloc[i[0]]
        movie_id = row['movie_id']       # ← uses ID instead of title
        title = row['title']
        poster_url, year = fetch_poster_and_year(movie_id)
        recommended_movies.append({
            "title": title,
            "poster": poster_url,
            "year": year
        })

    return recommended_movies


# ── Load data ──────────────────────────────────────────────────────────────────
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("🎬 Movie Recommendation System")
st.markdown("##### Discover movies you'll love based on your favorites")
st.markdown("---")

selected_movie_name = st.selectbox("🎥 Select a movie you like:", movies['title'].values)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("✨ Get Recommendations"):
    with st.spinner("Finding the best movies for you..."):
        recommendations = recommend(selected_movie_name)

    st.markdown('<div class="section-title">🍿 Recommended For You</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            movie = recommendations[idx]
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie['poster']}" alt="{movie['title']}"/>
                    <div class="movie-title">{movie['title']}</div>
                    <div class="movie-year">📅 {movie['year']}</div>
                </div>
            """, unsafe_allow_html=True)