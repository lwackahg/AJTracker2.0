"""
System test script for verifying core functionality while minimizing database connections.
"""
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Movie, Book, MovieAdaptation, Review
from app.services.adaptation_service import AdaptationService
from app.utils.backup import DatabaseBackup

class TestSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.app = create_app()
        
        # Use the actual Azure SQL Database for testing
        cls.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-key'
        })
        cls.client = cls.app.test_client()
        
        # Create test data in a proper app context
        with cls.app.app_context():
            # Create test user
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('testpass')
            db.session.add(test_user)
            db.session.commit()
    
    def setUp(self):
        """Set up before each test"""
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            # Clean up test data
            User.query.filter_by(username='testuser').delete()
            db.session.commit()
        self.app_context.pop()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        with cls.app.app_context():
            db.session.remove()
    
    def test_response_time_requirement(self):
        """Test R4: Response time under 2 seconds"""
        print("\nTesting response time requirement (R4)...")
        
        endpoints = [
            ('/api/search?query=test', 'GET'),
            ('/api/adaptations/1', 'GET'),
            ('/api/feedback', 'POST')
        ]
        
        for endpoint, method in endpoints:
            start_time = time.time()
            if method == 'GET':
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint, json={'rating': 5, 'comment': 'test'})
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"{method} {endpoint} response time: {response_time:.2f} seconds")
            self.assertLess(response_time, 2.0, f"{endpoint} response time exceeds 2 seconds requirement")

    def test_security_configurations(self):
        """Test R5: Security configurations"""
        print("\nTesting security configurations (R5)...")
        
        # Test session configuration
        with self.client as c:
            c.get('/')
            cookie = next((cookie for cookie in c.cookie_jar), None)
            if cookie:
                self.assertTrue(cookie.secure, "Session cookie should be secure")
                self.assertTrue(cookie.http_only, "Session cookie should be HTTP-only")
                self.assertEqual(cookie.samesite, 'Lax', "Session cookie should have SameSite=Lax")

        # Test password hashing
        user = User.query.filter_by(username='testuser').first()
        self.assertNotEqual(user.password_hash, 'testpass', "Password should be hashed")
        self.assertTrue(user.check_password('testpass'), "Password verification should work")

    @patch('app.services.adaptation_service.requests.get')
    def test_adaptation_search(self, mock_get):
        """Test adaptation search functionality"""
        print("\nTesting adaptation search...")
        
        # Mock TMDb API response
        mock_tmdb_response = {
            'results': [
                {
                    'id': 1,
                    'title': 'Test Movie',
                    'overview': 'Test overview',
                    'release_date': '2023-01-01'
                }
            ]
        }
        
        # Mock Google Books API response
        mock_books_response = {
            'items': [
                {
                    'id': 'book1',
                    'volumeInfo': {
                        'title': 'Test Book',
                        'authors': ['Test Author'],
                        'description': 'Test description',
                        'publishedDate': '2023'
                    }
                }
            ]
        }
        
        mock_get.side_effect = [
            MagicMock(ok=True, json=lambda: mock_tmdb_response),
            MagicMock(ok=True, json=lambda: mock_books_response)
        ]
        
        response = self.client.get('/api/search?query=test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('adaptations', data)
        self.assertTrue(len(data['adaptations']) > 0)

    @patch('azure.storage.blob.BlobServiceClient')
    def test_backup_system(self, mock_blob_service):
        """Test R9: Backup functionality"""
        print("\nTesting backup system (R9)...")
        
        # Mock Azure Blob Storage
        mock_blob_service.from_connection_string.return_value = MagicMock()
        
        backup = DatabaseBackup()
        success = backup.create_backup()
        self.assertTrue(success, "Backup creation should succeed")
        
        # Verify backup file creation
        mock_blob_service.from_connection_string.assert_called_once()
        
    def test_user_feedback(self):
        """Test user feedback submission functionality"""
        # Login as test user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Submit a review
        review_data = {
            'movieID': 1,
            'rating': 5,
            'comment': 'Great movie!'
        }
        response = self.client.post('/api/reviews', json=review_data)
        self.assertEqual(response.status_code, 201)
        
        # Verify review was saved
        review = Review.query.filter_by(movieID=1).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great movie!')

    def test_movie_review(self):
        """Test movie review functionality"""
        print("\nTesting movie review functionality...")
        
        # Get test user and movie
        user = User.query.filter_by(username='testuser').first()
        movie = Movie.query.filter_by(title='Test Movie').first()
        
        # Create a review
        review = Review(
            userID=user.userID,
            movieID=movie.movieID,
            rating=4.5,
            comment='Great adaptation!'
        )
        db.session.add(review)
        db.session.commit()
        
        # Verify review was created
        saved_review = Review.query.filter_by(userID=user.userID, movieID=movie.movieID).first()
        self.assertIsNotNone(saved_review)
        self.assertEqual(saved_review.rating, 4.5)
        self.assertEqual(saved_review.comment, 'Great adaptation!')
        
        # Verify movie's average rating is updated
        movie.update_average_rating()
        self.assertEqual(movie.average_rating, 4.5)
        
        # Test review modification
        saved_review.rating = 5.0
        saved_review.comment = 'Even better on second watch!'
        db.session.commit()
        
        # Verify changes
        updated_review = Review.query.filter_by(userID=user.userID, movieID=movie.movieID).first()
        self.assertEqual(updated_review.rating, 5.0)
        self.assertEqual(updated_review.comment, 'Even better on second watch!')
        
        # Verify average rating update
        movie.update_average_rating()
        self.assertEqual(movie.average_rating, 5.0)

    def test_error_handling(self):
        """Test error handling"""
        print("\nTesting error handling...")
        
        # Test 404 handling
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        # Test invalid adaptation ID
        response = self.client.get('/api/adaptations/999999')
        self.assertEqual(response.status_code, 404)
        
        # Test invalid feedback submission
        response = self.client.post('/api/feedback', json={})
        self.assertEqual(response.status_code, 400)

    def test_tmdb_api(self):
        """Test TMDB API connectivity and response"""
        print("\nTesting TMDB API...")
        
        # Test movie search
        response = self.client.get('/api/movies/search?query=Dune')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('results', data)
        
        # Test movie details
        if data['results']:
            movie_id = data['results'][0]['id']
            response = self.client.get(f'/api/movies/{movie_id}')
            self.assertEqual(response.status_code, 200)
            movie_data = response.get_json()
            self.assertIn('title', movie_data)
            self.assertIn('overview', movie_data)
    
    def test_google_books_api(self):
        """Test Google Books API connectivity and response"""
        print("\nTesting Google Books API...")
        
        # Test book search
        response = self.client.get('/api/books/search?query=Dune')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        
        # Test book details
        if data['items']:
            book_id = data['items'][0]['id']
            response = self.client.get(f'/api/books/{book_id}')
            self.assertEqual(response.status_code, 200)
            book_data = response.get_json()
            self.assertIn('title', book_data)
            self.assertIn('authors', book_data)

def run_tests():
    unittest.main(argv=[''], verbosity=2)

if __name__ == '__main__':
    run_tests()
