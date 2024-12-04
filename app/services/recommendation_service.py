"""
Recommendation Service: Implements personalized movie suggestions based on user preferences
and viewing history.
"""
from typing import List, Dict, Any
from ..models import User, Movie, WatchHistory, Review
from sqlalchemy import func
import numpy as np
from collections import defaultdict

class RecommendationService:
    """
    Singleton pattern implementation for recommendation service
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecommendationService, cls).__new__(cls)
        return cls._instance

    def get_recommendations(self, user: User) -> List[Dict[str, Any]]:
        """Generate personalized movie recommendations"""
        # Get user's watch history
        watched_movies = WatchHistory.query.filter_by(userID=user.userID).all()
        watched_ids = [wh.movieID for wh in watched_movies]

        # Get user's ratings
        user_ratings = Review.query.filter_by(userID=user.userID).all()
        
        # Calculate genre preferences
        genre_scores = self._calculate_genre_preferences(watched_movies, user_ratings)
        
        # Get recommendations based on genre preferences
        recommendations = self._get_genre_based_recommendations(
            genre_scores, 
            watched_ids, 
            limit=10
        )
        
        return recommendations

    def _calculate_genre_preferences(self, watch_history: List[WatchHistory], 
                                  ratings: List[Review]) -> Dict[str, float]:
        """Calculate user's genre preferences based on watch history and ratings"""
        genre_scores = defaultdict(float)
        genre_counts = defaultdict(int)

        # Weight genres based on watch history and ratings
        for wh in watch_history:
            movie = Movie.query.get(wh.movieID)
            if movie and movie.genres:
                for genre in movie.genres:
                    # Find corresponding rating if exists
                    rating = next((r.rating for r in ratings if r.movieID == movie.movieID), 3.0)
                    genre_scores[genre] += rating
                    genre_counts[genre] += 1

        # Normalize scores
        for genre in genre_scores:
            if genre_counts[genre] > 0:
                genre_scores[genre] /= genre_counts[genre]

        return dict(genre_scores)

    def _get_genre_based_recommendations(self, genre_preferences: Dict[str, float], 
                                       excluded_ids: List[int], 
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """Get movie recommendations based on genre preferences"""
        # Get all movies not in watch history
        available_movies = Movie.query.filter(
            ~Movie.movieID.in_(excluded_ids)
        ).all()

        # Score movies based on genre preferences
        movie_scores = []
        for movie in available_movies:
            if movie.genres:
                score = sum(genre_preferences.get(genre, 0) for genre in movie.genres)
                movie_scores.append((movie, score))

        # Sort by score and return top recommendations
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = []
        
        for movie, score in movie_scores[:limit]:
            recommendations.append({
                'movie_id': movie.movieID,
                'title': movie.title,
                'score': score,
                'genres': movie.genres,
                'average_rating': movie.average_rating
            })

        return recommendations
