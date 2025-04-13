import pandas as pd
import streamlit as st
import pickle
import requests


# Fetch movie poster using TMDb API
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3edc5d8eedff611f32541ef5f7f9c8ee&language=en-US"
        response = requests.get(url)
        data = response.json()

        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        pass

    # Fallback if poster not found or error occurs
    return "https://via.placeholder.com/300x450?text=No+Image"


# Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']  # ✅ Ensure movie_id is from DataFrame
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)  # Should contain 'title' and 'movie_id' columns
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get similar recommendations:",
    movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx in range(5):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{names[idx]}">
                    <p style="font-weight: bold; color: white; margin-bottom: 0.5rem; max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
                        {names[idx]}
                    </p>
                    <img src="{posters[idx]}" style="width:100%; border-radius: 10px;" />
                </div>
                """,
                unsafe_allow_html=True
            )


