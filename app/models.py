"""
Database models for the Film Adaptation Tracker application.
This module defines the database schema and relationships between different entities.
It also implements the Observer pattern for notifications and the Adapter pattern for
standardized data retrieval from external APIs.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import requests
import os
import json
from concurrent.futures import ThreadPoolExecutor
from typing import List
from datetime import timezone

# Observer Pattern Implementation
class Observer:
    """Base Observer class for implementing the Observer pattern."""
    def update(self, subject):
        """Called when the subject's state changes."""
        pass

class Subject:
    """Base Subject class for implementing the Observer pattern."""
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        self._observers.remove(observer)

    def notify(self):
        """Notify all observers about state changes."""
        for observer in self._observers:
            observer.update(self)

# Key Viewpoints: Development Viewpoint
# This class represents the User entity in the system, managing user data and interactions.
# Attributes include userID, username, email, watchHistory, and readHistory.
# Methods like addMovie() and leaveFeedback() are conceptualized here.
class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'Users'
    UserId = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String)
    Email = db.Column(db.String)
    password_hash = db.Column(db.String(512))
    _preferences = db.Column('preferences', db.String)  # Store JSON as string
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return the user's ID as a string."""
        return str(self.UserId)

    @property
    def preferences(self):
        """Get preferences as a Python object."""
        return json.loads(self._preferences) if self._preferences else None

    @preferences.setter
    def preferences(self, value):
        """Set preferences by converting Python object to JSON string."""
        self._preferences = json.dumps(value) if value is not None else None

# Logical Viewpoint: Sequence Diagram
# This class interacts with the TMDb API to fetch movie details.
# It represents the sequence of operations for retrieving movie data.
class Movie(db.Model, Subject):
    """Movie model for storing movie information."""
    __tablename__ = 'movies'
    movieID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    tmdb_id = db.Column(db.Integer, unique=True)
    releaseDate = db.Column(db.Date)
    overview = db.Column(db.Text)
    average_rating = db.Column(db.Float)
    reviews = db.relationship('Review', backref='movie', lazy=True)

    def __init__(self, *args, **kwargs):
        super(Movie, self).__init__(*args, **kwargs)
        Subject.__init__(self)

    def update_details(self, **kwargs):
        """Update movie details and notify observers."""
        changed = False
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed = True
        if changed:
            self.notify()

    def __repr__(self):
        return f'<Movie {self.title}>'

# Key Viewpoints: Development Viewpoint
# This class contains information about books, including attributes like bookID, title, author, and publicationDate.
# Methods like getDetails() are conceptualized here.
class Book(db.Model, Subject):
    """Book model representing literary works in the database."""
    __tablename__ = 'Books'
    BookId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String)
    Author = db.Column(db.String)
    PublicationDate = db.Column(db.Date)  # Changed from DateTime to Date
    ISBN = db.Column(db.String)
    GoogleBooksId = db.Column(db.String)
    Description = db.Column(db.String)
    CoverImageUrl = db.Column(db.String)
    PageCount = db.Column(db.Integer)
    Rating = db.Column(db.Integer)
    Review = db.Column(db.String)
    movie_adaptations = db.relationship('MovieAdaptation', backref='book', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Book, self).__init__(*args, **kwargs)
        Subject.__init__(self)

    def update_details(self, **kwargs):
        """Update book details and notify observers."""
        changed = False
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed = True
        if changed:
            self.notify()

    @staticmethod
    def getDetails(book_id):
        """Fetch book details from Google Books API."""
        api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}?key={api_key}'
        response = requests.get(url)
        return response.json() if response.ok else None

# Key Viewpoints: Development Viewpoint
# This class stores user reviews for adaptations, including attributes like reviewID, user, rating, and comment.
class Review(db.Model):
    """Review model for book and movie reviews and ratings."""
    __tablename__ = 'Reviews'
    ReviewId = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.UserId'))
    MovieAdaptationId = db.Column(db.Integer, db.ForeignKey('MovieAdaptations.MovieAdaptationId'), nullable=True)
    movieID = db.Column(db.Integer, db.ForeignKey('movies.movieID'), nullable=True)
    BookId = db.Column(db.Integer, db.ForeignKey('Books.BookId'), nullable=True)  # New field for book reviews
    Rating = db.Column(db.Float)
    Comment = db.Column(db.String)
    CreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, UserId, Rating, Comment, MovieAdaptationId=None, movieID=None, BookId=None):
        self.UserId = UserId
        self.Rating = Rating
        self.Comment = Comment
        self.MovieAdaptationId = MovieAdaptationId
        self.movieID = movieID
        self.BookId = BookId

# Key Viewpoints: Development Viewpoint
# This class represents the relationship between films and their source materials.
class MovieAdaptation(db.Model):
    """Movie adaptation model."""
    __tablename__ = 'MovieAdaptations'
    MovieAdaptationId = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String)
    BookId = db.Column(db.Integer, db.ForeignKey('Books.BookId'))
    movieID = db.Column(db.Integer, db.ForeignKey('movies.movieID'))
    Overview = db.Column(db.String)
    ReleaseDate = db.Column(db.DateTime)
    TmdbId = db.Column(db.String)
    PosterPath = db.Column(db.String)
    reviews = db.relationship('Review', backref='movie_adaptation', lazy='dynamic')

# Process Viewpoint: Activity Diagram
# This class is part of the workflow for logging movies and books.
# It demonstrates the steps involved in saving and confirming data entries.
class WatchHistory(db.Model):
    """WatchHistory model for tracking watched movies."""
    __tablename__ = 'watch_history'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('Users.UserId'), nullable=False)
    movieID = db.Column(db.Integer, db.ForeignKey('movies.movieID'), nullable=False)
    watched_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<WatchHistory {self.id}>'

# Key Viewpoints: Development Viewpoint
# This class logs books that users have read, with attributes like userID and bookID.
class ReadHistory(db.Model):
    """ReadHistory model for tracking read books."""
    __tablename__ = 'read_history'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('Users.UserId'), nullable=False)
    bookID = db.Column(db.Integer, db.ForeignKey('Books.BookId'), nullable=False)
    read_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ReadHistory {self.id}>'

# Scenario Viewpoint: User Interaction Flow
# This class facilitates user interactions for managing watchlists.
# It outlines the functionalities available for users to track desired movies.
class Watchlist(db.Model, Observer):
    """Watchlist model for tracking movies users want to watch."""
    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('Users.UserId'), nullable=False)
    movieID = db.Column(db.Integer, db.ForeignKey('movies.movieID'), nullable=False)
    added_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    _notification_preferences = db.Column('notification_preferences', db.String)
    movie = db.relationship('Movie', backref='watchlist_items', lazy=True)

    def __init__(self, *args, **kwargs):
        super(Watchlist, self).__init__(*args, **kwargs)
        if 'movie' in kwargs:
            kwargs['movie'].attach(self)

    def update(self, subject):
        """Called when the movie's details are updated."""
        from app.services.notification_service import NotificationService
        if isinstance(subject, Movie) and subject.movieID == self.movieID:
            notification_service = NotificationService()
            notification_service.notify_watchlist_updates(subject)

    def __repr__(self):
        return f'<Watchlist {self.id}>'

# Physical Viewpoint: Technological Layout
# This class integrates with the Flask server and MySQL database.
# It manages data storage and retrieval operations for reading lists.
class ReadingList(db.Model, Observer):
    """ReadingList model for tracking books users want to read."""
    __tablename__ = 'readinglist'
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('Users.UserId'), nullable=False)
    bookID = db.Column(db.Integer, db.ForeignKey('Books.BookId'), nullable=False)
    added_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user = db.relationship('User', backref=db.backref('reading_list_items', lazy=True))
    book = db.relationship('Book', backref=db.backref('reading_list_entries', lazy=True))

    def __init__(self, *args, **kwargs):
        super(ReadingList, self).__init__(*args, **kwargs)
        if 'book' in kwargs:
            kwargs['book'].attach(self)

    def update(self, subject):
        """Called when the book's details are updated."""
        from app.services.notification_service import NotificationService
        if isinstance(subject, Book) and subject.BookId == self.bookID:
            notification_service = NotificationService()
            if hasattr(subject, 'movie_adaptations') and subject.movie_adaptations.count() > 0:
                notification_service.notify_new_adaptation(subject.Title, subject.movie_adaptations[-1])

    def __repr__(self):
        return f'<ReadingList {self.id}>'
