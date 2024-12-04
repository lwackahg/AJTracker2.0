"""
Main routes for the Film Adaptation Tracker application.
This module handles all the main API endpoints for the application.
"""

from flask import render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from . import main
from ..models import Movie, Book, MovieAdaptation, Review, Watchlist, db
from ..services.adaptation_service import AdaptationService
from ..services.recommendation_service import RecommendationService
from ..services.analytics_service import AnalyticsService
from ..services.notification_service import NotificationService
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

@main.route('/')
def index():
    """Landing page endpoint."""
    return jsonify({'message': 'Welcome to Film Adaptation App'}), 200

@main.route('/api/search')
def search():
    """Search for adaptations based on query."""
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    try:
        service = AdaptationService()
        results = service.search_adaptations(query)
        return jsonify({'adaptations': results}), 200
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@main.route('/api/adaptations/<int:id>')
def get_adaptation(id):
    """Get details of a specific adaptation."""
    try:
        adaptation = MovieAdaptation.query.get_or_404(id)
        return jsonify({
            'movie': {
                'title': adaptation.movie.title,
                'release_date': adaptation.movie.releaseDate,
                'overview': adaptation.movie.overview,
                'average_rating': adaptation.movie.average_rating
            },
            'book': {
                'title': adaptation.book.title,
                'author': adaptation.book.author,
                'publication_date': adaptation.book.publicationDate,
                'genres': adaptation.book.genres
            },
            'adaptation_type': adaptation.adaptation_type
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving adaptation {id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve adaptation'}), 500

@main.route('/api/movies/filter')
def filter_movies():
    """Filter movies by genre, year, or rating (R7)."""
    genre = request.args.get('genre')
    year = request.args.get('year', type=int)
    min_rating = request.args.get('min_rating', type=float)
    
    try:
        query = Movie.query
        
        if genre:
            query = query.filter(Movie.genres.contains([genre]))
        if year:
            query = query.filter(db.extract('year', Movie.releaseDate) == year)
        if min_rating:
            query = query.filter(Movie.average_rating >= min_rating)
        
        movies = query.all()
        return jsonify({
            'movies': [{
                'id': movie.movieID,
                'title': movie.title,
                'release_date': movie.releaseDate,
                'average_rating': movie.average_rating,
                'genres': movie.genres
            } for movie in movies]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error filtering movies: {str(e)}")
        return jsonify({'error': 'Failed to filter movies'}), 500

@main.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_watchlist():
    """Manage user's watchlist (R8)."""
    try:
        if request.method == 'GET':
            watchlist = Watchlist.query.filter_by(userID=current_user.userID).all()
            return jsonify({
                'watchlist': [{
                    'movie_id': item.movieID,
                    'title': item.movie.title,
                    'added_date': item.added_date
                } for item in watchlist]
            }), 200
            
        elif request.method == 'POST':
            data = request.get_json()
            movie_id = data.get('movie_id')
            if not movie_id:
                return jsonify({'error': 'Movie ID is required'}), 400
                
            movie = Movie.query.get_or_404(movie_id)
            watchlist_entry = Watchlist(
                userID=current_user.userID,
                movieID=movie_id,
                notification_preferences=data.get('notification_preferences', {})
            )
            db.session.add(watchlist_entry)
            db.session.commit()
            return jsonify({'message': 'Added to watchlist'}), 201
            
        elif request.method == 'DELETE':
            movie_id = request.args.get('movie_id')
            if not movie_id:
                return jsonify({'error': 'Movie ID is required'}), 400
                
            Watchlist.query.filter_by(
                userID=current_user.userID,
                movieID=movie_id
            ).delete()
            db.session.commit()
            return jsonify({'message': 'Removed from watchlist'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in watchlist: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500
    except Exception as e:
        current_app.logger.error(f"Error in watchlist: {str(e)}")
        return jsonify({'error': 'Operation failed'}), 500

@main.route('/api/recommendations')
@login_required
def get_recommendations():
    """Get personalized movie recommendations based on user preferences and history."""
    try:
        service = RecommendationService()
        recommendations = service.get_recommendations(current_user)
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        current_app.logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@main.route('/api/analytics')
@login_required
def get_analytics():
    """Get user's viewing habits analytics (R2)."""
    try:
        service = AnalyticsService()
        analytics = service.get_user_analytics(current_user)
        return jsonify({
            'viewing_habits': analytics.get('viewing_habits'),
            'genre_preferences': analytics.get('genre_preferences'),
            'rating_distribution': analytics.get('rating_distribution')
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@main.route('/api/notifications')
@login_required
def get_notifications():
    """Get user's notifications for watchlist updates and new adaptations."""
    try:
        service = NotificationService()
        notifications = service.get_user_notifications(current_user)
        return jsonify({'notifications': notifications}), 200
    except Exception as e:
        current_app.logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({'error': 'Failed to get notifications'}), 500

@main.route('/api/reviews', methods=['POST'])
@login_required
def create_review():
    """Create a new review for a movie (R3)."""
    try:
        data = request.get_json()
        if not all(k in data for k in ('movie_id', 'rating')):
            return jsonify({'error': 'Missing required fields'}), 400
            
        movie = Movie.query.get_or_404(data['movie_id'])
        review = Review(
            userID=current_user.userID,
            movieID=data['movie_id'],
            rating=data['rating'],
            comment=data.get('comment', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(review)
        movie.update_average_rating()
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review_id': review.reviewID
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in review creation: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500
    except Exception as e:
        current_app.logger.error(f"Error creating review: {str(e)}")
        return jsonify({'error': 'Failed to create review'}), 500

@main.route('/api/movies/<int:movie_id>/reviews')
def get_reviews(movie_id):
    """Get all reviews for a specific movie."""
    try:
        movie = Movie.query.get_or_404(movie_id)
        reviews = Review.query.filter_by(movieID=movie_id).all()
        return jsonify({
            'movie_title': movie.title,
            'average_rating': movie.average_rating,
            'reviews': [{
                'user': review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at
            } for review in reviews]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting reviews for movie {movie_id}: {str(e)}")
        return jsonify({'error': 'Failed to get reviews'}), 500
