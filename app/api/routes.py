from flask import jsonify, request, current_app
from flask_login import login_required, current_user
import requests
import os
from . import api
from ..models import db, Movie, Book, MovieAdaptation, Review, WatchHistory, ReadHistory
from ..services.adaptation_service import AdaptationService

# Initialize the adaptation service
adaptation_service = AdaptationService()

@api.route('/search', methods=['GET'])
async def search_adaptations():
    """
    Logical Viewpoint Implementation:
    1. User initiates search
    2. WebApp receives request
    3. Concurrent API calls via AdaptationService
    4. Results returned to user
    """
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    # Use the service to handle the sequence of API calls
    results = await adaptation_service.search_adaptations(query)
    return jsonify(results), 200

@api.route('/adaptations/<movie_id>/<book_id>', methods=['GET'])
async def get_adaptation_details(movie_id, book_id):
    """Get detailed information about a specific adaptation"""
    details = adaptation_service.get_detailed_adaptation(movie_id, book_id)
    return jsonify(details), 200

@api.route('/movies/log', methods=['POST'])
@login_required
def log_movie():
    """
    Process Viewpoint - Log Movie workflow:
    1. Receive movie details
    2. Save to database
    3. Send confirmation
    """
    data = request.get_json()
    if not data or 'movieID' not in data:
        return jsonify({'error': 'Movie ID is required'}), 400

    try:
        # Get movie details from TMDb
        movie_details = Movie.getDetails(data['movieID'])
        if not movie_details:
            return jsonify({'error': 'Movie not found'}), 404

        # Check if movie exists in database, if not create it
        movie = Movie.query.filter_by(tmdb_id=data['movieID']).first()
        if not movie:
            movie = Movie(
                tmdb_id=data['movieID'],
                title=movie_details.get('title'),
                releaseDate=movie_details.get('release_date'),
                overview=movie_details.get('overview')
            )
            db.session.add(movie)
            db.session.commit()

        # Log the watch
        current_user.addMovie(movie)
        
        return jsonify({
            'message': 'Movie logged successfully',
            'movie': {
                'title': movie.title,
                'releaseDate': movie.releaseDate
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/books/log', methods=['POST'])
@login_required
def log_book():
    """
    Process Viewpoint - Log Book workflow:
    1. Receive book details
    2. Save to database
    3. Send confirmation
    """
    data = request.get_json()
    if not data or 'bookID' not in data:
        return jsonify({'error': 'Book ID is required'}), 400

    try:
        # Get book details from Google Books
        book_details = Book.getDetails(data['bookID'])
        if not book_details:
            return jsonify({'error': 'Book not found'}), 404

        # Check if book exists in database, if not create it
        book = Book.query.filter_by(google_books_id=data['bookID']).first()
        if not book:
            book = Book(
                google_books_id=data['bookID'],
                title=book_details.get('volumeInfo', {}).get('title'),
                author=book_details.get('volumeInfo', {}).get('authors', [''])[0],
                publicationDate=book_details.get('volumeInfo', {}).get('publishedDate')
            )
            db.session.add(book)
            db.session.commit()

        # Log the read
        read_entry = ReadHistory(userID=current_user.userID, bookID=book.bookID)
        db.session.add(read_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Book logged successfully',
            'book': {
                'title': book.title,
                'author': book.author
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/adaptations/feedback', methods=['POST'])
@login_required
def leave_adaptation_feedback():
    """
    Process Viewpoint - Leave Feedback workflow:
    1. Receive feedback details
    2. Save review
    3. Send confirmation
    """
    data = request.get_json()
    required_fields = ['movieID', 'rating', 'comment']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        movie = Movie.query.filter_by(movieID=data['movieID']).first()
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        # Create review using the User method
        review = current_user.leaveFeedback(
            movie=movie,
            rating=data['rating'],
            comment=data['comment']
        )
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'review': {
                'movieTitle': movie.title,
                'rating': review.rating,
                'comment': review.comment
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/user/history', methods=['GET'])
@login_required
def get_user_history():
    """
    Process Viewpoint - View History workflow:
    1. Fetch user's watch and read history
    2. Return formatted history
    """
    watch_history = WatchHistory.query.filter_by(userID=current_user.userID).all()
    read_history = ReadHistory.query.filter_by(userID=current_user.userID).all()

    history = {
        'watched_movies': [{
            'title': Movie.query.get(entry.movieID).title,
            'date': entry.watched_date.isoformat()
        } for entry in watch_history],
        'read_books': [{
            'title': Book.query.get(entry.bookID).title,
            'date': entry.read_date.isoformat()
        } for entry in read_history]
    }

    return jsonify(history), 200
