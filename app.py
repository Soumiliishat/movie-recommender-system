import pandas as pd
import streamlit as st
import pickle
import requests

# Wide layout for full-screen app
st.set_page_config(page_title="Movie Recommender", layout="wide")

API_KEY = "3edc5d8eedff611f32541ef5f7f9c8ee"  # Replace with your TMDb API key

# Fetch movie poster & rating from TMDb
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path'] if data.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Image"
        rating = data.get("vote_average", "N/A")
        return poster, rating
    except:
        return "https://via.placeholder.com/300x450?text=No+Image", "N/A"

# Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    posters = []
    ratings = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        title = movies.iloc[i[0]]['title']
        poster, rating = fetch_movie_details(movie_id)

        recommended_movies.append(title)
        posters.append(poster)
        ratings.append(rating)

    return recommended_movies, posters, ratings

# Load saved data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Fetch trending movies from TMDb
def get_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    trending = data.get("results", [])[:10]
    titles = [movie['title'] for movie in trending]
    posters = ["https://image.tmdb.org/t/p/w500/" + movie['poster_path'] if movie.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Image" for movie in trending]
    ratings = [movie.get('vote_average', 'N/A') for movie in trending]
    return titles, posters, ratings

# UI
st.title("📽️ Movie Recommender System")

# --- Movie Selection
selected_movie = st.selectbox(
    "Select a movie to get similar recommendations:",
    movies['title'].values
)

if st.button("Recommend"):
    st.subheader("🔁 Similar Movies")
    names, posters, ratings = recommend(selected_movie)

    for i in range(0, len(names), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(names):
                with cols[j]:
                    st.image(posters[i + j])

                    # Display the movie name with ellipsis and tooltip for the full title
                    truncated_name = names[i + j]
                    if len(truncated_name) > 20:  # Set a limit for truncation
                        truncated_name = truncated_name[:20] + "..."
                    st.markdown(f'<p style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap; cursor: pointer;" title="{names[i + j]}"><b>{truncated_name}</b></p>', unsafe_allow_html=True)

                    st.markdown(f"⭐ {ratings[i + j]}")

# --- Trending Section
st.markdown("---")
st.subheader("📈 Trending This Week")

trending_titles, trending_posters, trending_ratings = get_trending_movies()
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        st.image(trending_posters[i])

        # Display the movie name with ellipsis and tooltip for the full title
        truncated_name = trending_titles[i]
        if len(truncated_name) > 20:  # Set a limit for truncation
            truncated_name = truncated_name[:20] + "..."
        st.markdown(f'<p style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap; cursor: pointer;" title="{trending_titles[i]}"><b>{truncated_name}</b></p>', unsafe_allow_html=True)

        st.markdown(f"⭐ {trending_ratings[i]}")
