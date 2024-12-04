import unittest
import os
import sys
from datetime import datetime
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Movie, Book, MovieAdaptation, Watchlist, WatchHistory, ReadHistory
from tests.test_config import TestConfig

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_movie_json_handling(self):
        """Test JSON handling in Movie model"""
        print("\nTesting Movie JSON handling...")
        
        # Create a movie with JSON data
        movie = Movie(
            title="Test Movie",
            releaseDate=datetime.now().date(),
            overview="Test overview",
            tmdb_id=12345,
            genres=["Action", "Adventure"],
            runtime=120,
            average_rating=4.5
        )
        
        db.session.add(movie)
        db.session.commit()
        
        # Retrieve the movie and check JSON handling
        retrieved_movie = Movie.query.filter_by(title="Test Movie").first()
        self.assertIsNotNone(retrieved_movie)
        self.assertEqual(retrieved_movie.genres, ["Action", "Adventure"])
        
        # Update genres
        retrieved_movie.genres = ["Drama", "Thriller"]
        db.session.commit()
        
        # Check updated genres
        updated_movie = Movie.query.get(retrieved_movie.movieID)
        self.assertEqual(updated_movie.genres, ["Drama", "Thriller"])

    def test_watchlist_json_handling(self):
        """Test JSON handling in Watchlist model"""
        print("\nTesting Watchlist JSON handling...")
        
        # Create test user and movie
        user = User(Username="testuser", Email="test@example.com")
        user.set_password("testpass")
        movie = Movie(title="Test Movie", tmdb_id=12345)
        
        db.session.add_all([user, movie])
        db.session.commit()
        
        # Create watchlist entry with JSON preferences
        watchlist = Watchlist(
            userID=user.UserId,
            movieID=movie.movieID,
            notification_preferences={
                "email": True,
                "push": False,
                "frequency": "weekly"
            }
        )
        
        db.session.add(watchlist)
        db.session.commit()
        
        # Retrieve and check JSON handling
        retrieved_watchlist = Watchlist.query.first()
        self.assertIsNotNone(retrieved_watchlist)
        self.assertEqual(
            retrieved_watchlist.notification_preferences,
            {"email": True, "push": False, "frequency": "weekly"}
        )
        
        # Update preferences
        retrieved_watchlist.notification_preferences = {
            "email": False,
            "push": True,
            "frequency": "daily"
        }
        db.session.commit()
        
        # Check updated preferences
        updated_watchlist = Watchlist.query.first()
        self.assertEqual(
            updated_watchlist.notification_preferences,
            {"email": False, "push": True, "frequency": "daily"}
        )

    def test_user_preferences_json_handling(self):
        """Test JSON handling in User preferences"""
        print("\nTesting User preferences JSON handling...")
        
        # Create user with JSON preferences
        user = User(
            Username="testuser",
            Email="test@example.com",
            preferences={
                "theme": "dark",
                "notifications": True,
                "language": "en"
            }
        )
        user.set_password("testpass")
        
        db.session.add(user)
        db.session.commit()
        
        # Retrieve and check JSON handling
        retrieved_user = User.query.filter_by(Username="testuser").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(
            retrieved_user.preferences,
            {"theme": "dark", "notifications": True, "language": "en"}
        )
        
        # Update preferences
        retrieved_user.preferences = {
            "theme": "light",
            "notifications": False,
            "language": "fr"
        }
        db.session.commit()
        
        # Check updated preferences
        updated_user = User.query.get(retrieved_user.UserId)
        self.assertEqual(
            updated_user.preferences,
            {"theme": "light", "notifications": False, "language": "fr"}
        )

    def test_relationships(self):
        """Test database relationships"""
        print("\nTesting database relationships...")
        
        # Create test data
        user = User(Username="testuser", Email="test@example.com")
        user.set_password("testpass")
        
        movie = Movie(
            title="Test Movie",
            tmdb_id=12345,
            genres=["Action"]
        )
        
        book = Book(
            Title="Test Book",
            Author="Test Author",
            GoogleBooksId="test123"
        )
        
        # First add and commit the user, movie, and book
        db.session.add_all([user, movie, book])
        db.session.commit()
        
        # Create movie adaptation linking book and movie
        adaptation = MovieAdaptation(
            Title="Test Adaptation",
            BookId=book.BookId,
            movieID=movie.movieID,
            Overview="Test overview"
        )
        
        # Create watchlist and history entries
        watchlist = Watchlist(
            userID=user.UserId,
            movieID=movie.movieID,
            notification_preferences={"email": True}
        )
        
        watch_history = WatchHistory(
            userID=user.UserId,
            movieID=movie.movieID,
            watched_date=datetime.now()  
        )
        
        read_history = ReadHistory(
            userID=user.UserId,
            bookID=book.BookId,
            read_date=datetime.now()
        )
        
        # Add the relationships and commit
        db.session.add_all([adaptation, watchlist, watch_history, read_history])
        db.session.commit()
        
        # Test relationships
        # Movie-Book relationship through MovieAdaptation
        self.assertEqual(movie.adaptations.first(), adaptation)
        self.assertEqual(book.movie_adaptations.first(), adaptation)
        
        # Test user relationships
        self.assertIn(watchlist, movie.in_watchlists.all())

if __name__ == '__main__':
    unittest.main()
