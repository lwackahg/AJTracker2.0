import unittest
import os
from app import create_app, db
from app.models import Movie, Book, User, Review
from app.tmdb_client import TMDBClient
from app.google_books_client import GoogleBooksClient
from datetime import datetime
from tests.test_config import TestConfig
import sqlalchemy as sa
from dateutil import tz

class TestAPIs(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Drop all tables first
        self.drop_all_tables()
        
        # Create tables
        db.create_all()
        
        self.client = self.app.test_client()
        
        # Initialize API clients
        self.tmdb = TMDBClient()
        self.google_books = GoogleBooksClient()

    def drop_all_tables(self):
        """Drop all tables in the correct order to handle foreign key constraints"""
        try:
            # Disable foreign key checks (SQL Server compatible)
            db.session.execute(sa.text('ALTER TABLE Reviews NOCHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE MovieAdaptations NOCHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE Watchlist NOCHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE WatchHistory NOCHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE ReadHistory NOCHECK CONSTRAINT ALL'))

            # Drop tables in specific order
            tables = [
                'Reviews',
                'MovieAdaptations',
                'Watchlist',
                'WatchHistory',
                'ReadHistory',
                'Books',
                'Movies',
                'Users'
            ]

            for table in tables:
                try:
                    db.session.execute(sa.text(f'DROP TABLE IF EXISTS {table}'))
                except Exception as e:
                    print(f"Error dropping table {table}: {str(e)}")

            db.session.commit()

            # Re-enable foreign key checks (SQL Server compatible)
            db.session.execute(sa.text('ALTER TABLE Reviews CHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE MovieAdaptations CHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE Watchlist CHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE WatchHistory CHECK CONSTRAINT ALL'))
            db.session.execute(sa.text('ALTER TABLE ReadHistory CHECK CONSTRAINT ALL'))

        except Exception as e:
            print(f"Error in drop_all_tables: {str(e)}")
            db.session.rollback()

    def tearDown(self):
        self.drop_all_tables()
        db.session.remove()
        self.app_context.pop()

    def test_tmdb_search(self):
        """Test TMDB API search functionality"""
        print("\nTesting TMDB Search...")
        
        # Search for a known movie
        search_query = "The Dark Knight"
        results = self.tmdb.search_movies(search_query)
        
        # Verify we got results
        self.assertTrue(len(results) > 0, "No results found for TMDB search")
        
        # Get the first result
        movie = results[0]
        print(f"Found movie: {movie.get('title')}")
        
        # Verify essential fields
        self.assertIn('title', movie)
        self.assertIn('id', movie)
        self.assertIn('release_date', movie)
        
        # Test detailed movie info
        movie_id = movie['id']
        details = self.tmdb.get_movie_details(movie_id)
        
        print(f"Movie details: Title={details.get('title')}, Runtime={details.get('runtime')}, Rating={details.get('vote_average')}")
        
        # Verify detailed fields
        self.assertIn('runtime', details)
        self.assertIn('vote_average', details)
        self.assertIn('genres', details)

    def test_google_books_search(self):
        """Test Google Books API search functionality"""
        print("\nTesting Google Books Search...")
        
        # Search for a known book
        search_query = "The Lord of the Rings"
        results = self.google_books.search_books(search_query)
        
        # Verify we got results
        self.assertTrue(len(results) > 0, "No results found for Google Books search")
        
        # Get the first result
        book = results[0]
        print(f"Found book: {book.get('volumeInfo', {}).get('title')}")
        
        # Verify essential fields
        self.assertIn('volumeInfo', book)
        volume_info = book['volumeInfo']
        self.assertIn('title', volume_info)
        self.assertIn('authors', volume_info)
        
        # Test detailed book info
        book_id = book['id']
        details = self.google_books.get_book_details(book_id)
        
        print(f"Book details: Title={details.get('volumeInfo', {}).get('title')}, "
              f"Author={', '.join(details.get('volumeInfo', {}).get('authors', []))}")
        
        # Verify detailed fields
        self.assertIn('volumeInfo', details)
        volume_info = details['volumeInfo']
        self.assertIn('title', volume_info)
        self.assertIn('authors', volume_info)

    def test_database_integration(self):
        """Test storing API data in our database"""
        print("\nTesting Database Integration...")
        
        # Search and store a movie
        movie_results = self.tmdb.search_movies("Inception")
        movie_data = movie_results[0]
        movie_details = self.tmdb.get_movie_details(movie_data['id'])
        
        movie = Movie(
            title=movie_details['title'],
            tmdb_id=str(movie_details['id']),
            overview=movie_details.get('overview', ''),
            releaseDate=datetime.strptime(movie_details['release_date'], '%Y-%m-%d').date(),
            runtime=movie_details.get('runtime'),
            average_rating=movie_details.get('vote_average')
        )
        
        # Search and store a book
        book_results = self.google_books.search_books("Dune")
        book_data = book_results[0]
        book_info = book_data['volumeInfo']
        
        # Convert to timezone-aware datetime if publication date is available
        publication_date_str = book_info.get('publishedDate', '2000')
        if publication_date_str:
            publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
            publication_date = datetime.combine(publication_date, datetime.min.time())
            publication_date = publication_date.replace(tzinfo=tz.tzutc())
        else:
            publication_date = None
        
        book = Book(
            Title=book_info['title'],
            Author=', '.join(book_info.get('authors', [])),
            GoogleBooksId=book_data['id'],
            PublicationDate=publication_date
        )
        
        # Store in database
        try:
            db.session.add(movie)
            db.session.add(book)
            db.session.commit()
            print(f"Successfully stored movie: {movie.title}")
            print(f"Successfully stored book: {book.Title}")
        except Exception as e:
            db.session.rollback()
            print(f"Error storing in database: {str(e)}")
            raise
        
        # Verify retrieval
        stored_movie = Movie.query.filter_by(tmdb_id=str(movie_details['id'])).first()
        stored_book = Book.query.filter_by(GoogleBooksId=book_data['id']).first()
        
        self.assertIsNotNone(stored_movie)
        self.assertIsNotNone(stored_book)
        self.assertEqual(stored_movie.title, movie_details['title'])
        self.assertEqual(stored_book.Title, book_info['title'])

    def test_tmdb_search_comprehensive(self):
        """Test TMDB movie search"""
        results = self.tmdb.search_movies("Inception")
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertTrue(any('Inception' in movie.get('title', '') for movie in results))

    def test_tmdb_movie_details_comprehensive(self):
        """Test TMDB movie details retrieval"""
        # Inception movie ID
        movie_id = 27205
        details = self.tmdb.get_movie_details(movie_id)
        self.assertIsNotNone(details)
        self.assertEqual(details.get('title'), 'Inception')

    def test_tmdb_movie_credits_comprehensive(self):
        """Test TMDB movie credits retrieval"""
        # Inception movie ID
        movie_id = 27205
        credits = self.tmdb.get_movie_credits(movie_id)
        self.assertIsNotNone(credits)
        self.assertTrue('cast' in credits or 'crew' in credits)

    def test_tmdb_similar_movies_comprehensive(self):
        """Test TMDB similar movies retrieval"""
        # Inception movie ID
        movie_id = 27205
        similar = self.tmdb.get_similar_movies(movie_id)
        self.assertIsInstance(similar, list)
        self.assertTrue(len(similar) > 0)

    def test_google_books_search_comprehensive(self):
        """Test Google Books search"""
        results = self.google_books.search_books("The Great Gatsby")
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertTrue(any('Great Gatsby' in book.get('volumeInfo', {}).get('title', '') 
                          for book in results))

    def test_google_books_details_comprehensive(self):
        """Test Google Books details retrieval"""
        # First search for a book to get its ID
        results = self.google_books.search_books("1984 George Orwell")
        self.assertTrue(len(results) > 0)
        book_id = results[0]['id']
        
        details = self.google_books.get_book_details(book_id)
        self.assertIsNotNone(details)
        self.assertTrue('volumeInfo' in details)
        self.assertTrue('1984' in details['volumeInfo'].get('title', ''))

    def test_google_books_similar_comprehensive(self):
        """Test Google Books similar books retrieval"""
        # First search for a book to get its ID
        results = self.google_books.search_books("1984 George Orwell")
        self.assertTrue(len(results) > 0)
        book_id = results[0]['id']
        
        similar = self.google_books.get_similar_books(book_id)
        self.assertIsInstance(similar, list)
        self.assertTrue(len(similar) > 0)

if __name__ == '__main__':
    unittest.main()
