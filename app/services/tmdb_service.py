import os
import requests
from app.models import Movie
from datetime import datetime
from app import db

def get_popular_movies():
    """Get a list of popular movies from TMDB API."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return []
    
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        return []

def create_movie_from_tmdb_data(movie_data):
    """Create a Movie object from TMDB API data."""
    release_date = None
    if movie_data.get('release_date'):
        try:
            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    return Movie(
        title=movie_data.get('title', ''),
        tmdb_id=movie_data.get('id'),
        releaseDate=release_date,  # Corrected attribute name
        overview=movie_data.get('overview', ''),
        average_rating=movie_data.get('vote_average', 0.0)
    )

def search_movies(query):
    """Search for movies using TMDB API."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return []

    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        print(f"Error searching movies: {e}")
        return []
