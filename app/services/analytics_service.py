"""
Analytics Service: Provides viewing habits visualization and analytics.

This service implements the analytics functionality for the Film Adaptation Tracker,
providing insights into user viewing habits, preferences, and trends. It uses pandas
for data analysis and visualization.

Features:
- User viewing statistics
- Genre distribution analysis
- Temporal viewing patterns
- Rating distribution
- Recent activity tracking
- Performance monitoring
- Weekly report generation
"""

from typing import Dict, Any, List, Optional
from ..models import User, WatchHistory, Movie, Review, db
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

class AnalyticsService:
    """Service class for analyzing user viewing habits and preferences."""
    
    def get_user_analytics(self, user: User) -> Dict[str, Any]:
        """
        Get comprehensive analytics about user's viewing habits.
        
        Args:
            user (User): The user to analyze
            
        Returns:
            Dict containing various analytics metrics
            
        Raises:
            SQLAlchemyError: If database operations fail
            ValueError: If data processing fails
        """
        try:
            # Collect all necessary data
            watch_history = WatchHistory.query.filter_by(userID=user.userID).all()
            reviews = Review.query.filter_by(userID=user.userID).all()
            
            return {
                'viewing_habits': self._analyze_viewing_habits(watch_history),
                'genre_preferences': self._analyze_genre_preferences(watch_history),
                'rating_distribution': self._analyze_ratings(reviews),
                'recent_activity': self._get_recent_activity(user)
            }
            
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in analytics: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Error processing analytics: {str(e)}")
            raise ValueError(f"Failed to process analytics: {str(e)}")

    def _analyze_viewing_habits(self, watch_history: List[WatchHistory]) -> Dict[str, Any]:
        """
        Analyze temporal patterns in user's viewing habits.
        
        Args:
            watch_history: List of user's watch history entries
            
        Returns:
            Dict containing viewing pattern metrics
        """
        if not watch_history:
            return {
                'total_watched': 0,
                'average_per_week': 0,
                'peak_viewing_time': None,
                'viewing_trend': []
            }

        try:
            # Convert to pandas DataFrame for analysis
            df = pd.DataFrame([{
                'date': wh.watched_date,
                'movie_id': wh.movieID,
                'hour': wh.watched_date.hour
            } for wh in watch_history])
            
            # Calculate metrics
            total_watched = len(watch_history)
            date_range = (df['date'].max() - df['date'].min()).days
            weeks = max(1, date_range / 7)
            avg_per_week = round(total_watched / weeks, 2)
            
            # Find peak viewing time
            peak_hour = df['hour'].mode().iloc[0] if not df.empty else None
            
            # Create viewing trend
            df['date'] = pd.to_datetime(df['date'])
            trend = df.groupby(df['date'].dt.date).size()
            
            return {
                'total_watched': total_watched,
                'average_per_week': avg_per_week,
                'peak_viewing_time': f"{peak_hour}:00" if peak_hour is not None else None,
                'viewing_trend': trend.to_dict()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing viewing habits: {str(e)}")
            return {
                'total_watched': len(watch_history),
                'error': 'Failed to analyze viewing patterns'
            }

    def _analyze_genre_preferences(self, watch_history: List[WatchHistory]) -> Dict[str, Any]:
        """
        Analyze user's genre preferences based on watch history.
        
        Args:
            watch_history: List of user's watch history entries
            
        Returns:
            Dict containing genre preference metrics
        """
        try:
            genre_counts = {}
            total_movies = len(watch_history)
            
            for wh in watch_history:
                movie = Movie.query.get(wh.movieID)
                if movie and movie.genres:
                    for genre in movie.genres:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Calculate percentages
            genre_preferences = {
                genre: {
                    'count': count,
                    'percentage': round((count / total_movies) * 100, 2)
                }
                for genre, count in genre_counts.items()
            }
            
            return {
                'total_movies': total_movies,
                'genre_distribution': genre_preferences,
                'top_genres': sorted(
                    genre_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing genre preferences: {str(e)}")
            return {'error': 'Failed to analyze genre preferences'}

    def _analyze_ratings(self, reviews: List[Review]) -> Dict[str, Any]:
        """
        Analyze user's rating distribution and patterns.
        
        Args:
            reviews: List of user's reviews
            
        Returns:
            Dict containing rating metrics
        """
        try:
            if not reviews:
                return {
                    'average_rating': 0,
                    'total_reviews': 0,
                    'rating_distribution': {}
                }
            
            ratings = [review.rating for review in reviews]
            rating_counts = pd.Series(ratings).value_counts().to_dict()
            
            return {
                'average_rating': round(sum(ratings) / len(ratings), 2),
                'total_reviews': len(reviews),
                'rating_distribution': rating_counts,
                'highest_rated_movies': self._get_highest_rated_movies(reviews)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing ratings: {str(e)}")
            return {'error': 'Failed to analyze ratings'}

    def _get_highest_rated_movies(self, reviews: List[Review], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get user's highest rated movies.
        
        Args:
            reviews: List of user's reviews
            limit: Maximum number of movies to return
            
        Returns:
            List of highest rated movies with details
        """
        try:
            sorted_reviews = sorted(reviews, key=lambda x: x.rating, reverse=True)[:limit]
            return [{
                'movie_id': review.movieID,
                'title': Movie.query.get(review.movieID).title,
                'rating': review.rating,
                'review_date': review.created_at
            } for review in sorted_reviews]
        except Exception as e:
            current_app.logger.error(f"Error getting highest rated movies: {str(e)}")
            return []

    def _get_recent_activity(self, user: User, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get user's recent activity across all interactions.
        
        Args:
            user: User to get activity for
            days: Number of days of history to return
            
        Returns:
            List of recent activity items
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent watches
            recent_watches = WatchHistory.query.filter(
                WatchHistory.userID == user.userID,
                WatchHistory.watched_date >= cutoff_date
            ).all()
            
            # Get recent reviews
            recent_reviews = Review.query.filter(
                Review.userID == user.userID,
                Review.created_at >= cutoff_date
            ).all()
            
            # Combine and sort activities
            activities = []
            
            for watch in recent_watches:
                movie = Movie.query.get(watch.movieID)
                activities.append({
                    'type': 'watch',
                    'movie_title': movie.title if movie else 'Unknown Movie',
                    'date': watch.watched_date,
                    'details': None
                })
            
            for review in recent_reviews:
                movie = Movie.query.get(review.movieID)
                activities.append({
                    'type': 'review',
                    'movie_title': movie.title if movie else 'Unknown Movie',
                    'date': review.created_at,
                    'details': {
                        'rating': review.rating,
                        'comment': review.comment
                    }
                })
            
            # Sort by date
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return activities
            
        except Exception as e:
            current_app.logger.error(f"Error getting recent activity: {str(e)}")
            return []

    def collect_performance_metrics(self) -> Dict[str, Any]:
        """
        Collect system performance metrics.
        
        Returns:
            Dict containing performance metrics
        """
        try:
            # Database performance metrics
            db_stats = self._get_database_metrics()
            
            # API response metrics
            api_stats = self._get_api_metrics()
            
            # System load metrics
            system_stats = self._get_system_metrics()
            
            return {
                'timestamp': datetime.utcnow(),
                'database': db_stats,
                'api': api_stats,
                'system': system_stats
            }
        except Exception as e:
            current_app.logger.error(f"Error collecting performance metrics: {str(e)}")
            return {'error': str(e)}

    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            # Query execution times
            start_time = datetime.utcnow()
            Movie.query.count()
            query_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Connection pool stats
            pool_stats = {
                'size': db.engine.pool.size(),
                'checked_in': db.engine.pool.checkedin(),
                'overflow': db.engine.pool.overflow()
            }
            
            return {
                'query_response_time': query_time,
                'connection_pool': pool_stats
            }
        except Exception as e:
            current_app.logger.error(f"Error getting database metrics: {str(e)}")
            return {'error': str(e)}

    def _get_api_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics."""
        try:
            from flask import request
            from ..utils.api_monitor import APIMonitor
            
            return {
                'average_response_time': APIMonitor.get_average_response_time(),
                'requests_per_minute': APIMonitor.get_requests_per_minute(),
                'error_rate': APIMonitor.get_error_rate()
            }
        except Exception as e:
            current_app.logger.error(f"Error getting API metrics: {str(e)}")
            return {'error': str(e)}

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        except Exception as e:
            current_app.logger.error(f"Error getting system metrics: {str(e)}")
            return {'error': str(e)}

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly performance and analytics report."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            # Collect metrics
            performance_data = self.collect_performance_metrics()
            
            # Get user activity stats
            total_users = User.query.count()
            active_users = WatchHistory.query.filter(
                WatchHistory.watched_date >= start_date
            ).distinct(WatchHistory.userID).count()
            
            # Get content stats
            total_movies = Movie.query.count()
            new_reviews = Review.query.filter(
                Review.created_at >= start_date
            ).count()
            
            return {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'user_metrics': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'engagement_rate': round(active_users / total_users * 100, 2) if total_users > 0 else 0
                },
                'content_metrics': {
                    'total_movies': total_movies,
                    'new_reviews': new_reviews
                },
                'performance_metrics': performance_data
            }
        except Exception as e:
            current_app.logger.error(f"Error generating weekly report: {str(e)}")
            return {'error': str(e)}
