import os
from datetime import datetime
from tmdbv3api import TMDb, Movie, Search

class TMDBClient:
    def __init__(self):
        self.tmdb = TMDb()
        self.tmdb.api_key = os.getenv('TMDB_API_KEY')
        self.movie = Movie()
        self.search = Search()
        
    def search_movies(self, query):
        """Search for movies using TMDB API"""
        results = self.search.movies(query)
        return [movie.__dict__ for movie in results]
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a specific movie"""
        movie = self.movie.details(movie_id)
        return movie.__dict__
    
    def get_movie_credits(self, movie_id):
        """Get cast and crew information for a movie"""
        credits = self.movie.credits(movie_id)
        return credits.__dict__
    
    def get_similar_movies(self, movie_id):
        """Get a list of similar movies"""
        similar = self.movie.similar(movie_id)
        return [movie.__dict__ for movie in similar]
