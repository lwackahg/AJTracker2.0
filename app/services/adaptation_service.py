"""
Adaptation Service: Implements the Logical Viewpoint sequence diagram
for handling adaptation searches and API interactions.
"""
from concurrent.futures import ThreadPoolExecutor
import os
import requests
from typing import Dict, Any, Optional
from ..models import Movie, Book

class AdaptationService:
    """
    Service class implementing the sequence diagram for adaptation searches.
    Follows the sequence:
    User -> WebApp -> (MovieAPI, BookAPI) -> WebApp -> User
    """

    def __init__(self):
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        self.google_books_api_key = os.getenv('GOOGLE_BOOKS_API_KEY')

    async def _fetch_movie_details(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch movie details from TMDb API"""
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': self.tmdb_api_key,
            'query': query,
            'language': 'en-US'
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching movie details: {str(e)}")
            return None

    async def _fetch_book_details(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch book details from Google Books API"""
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': query,
            'key': self.google_books_api_key
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching book details: {str(e)}")
            return None

    async def search_adaptations(self, query: str) -> Dict[str, Any]:
        """
        Main sequence implementation:
        1. Receive search query
        2. Concurrent API calls
        3. Process and combine results
        4. Return formatted response
        """
        # Execute API calls concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            movie_future = executor.submit(self._fetch_movie_details, query)
            book_future = executor.submit(self._fetch_book_details, query)

            # Wait for both calls to complete
            movie_results = movie_future.result()
            book_results = book_future.result()

        # Process and format results
        adaptations = []
        if movie_results and book_results:
            movie_list = movie_results.get('results', [])
            book_list = book_results.get('items', [])

            # Match potential adaptations
            for movie in movie_list:
                movie_title = movie.get('title', '').lower()
                for book in book_list:
                    book_info = book.get('volumeInfo', {})
                    book_title = book_info.get('title', '').lower()
                    
                    # Simple title matching (can be enhanced)
                    if movie_title in book_title or book_title in movie_title:
                        adaptations.append({
                            'movie': {
                                'id': movie.get('id'),
                                'title': movie.get('title'),
                                'release_date': movie.get('release_date'),
                                'overview': movie.get('overview')
                            },
                            'book': {
                                'id': book.get('id'),
                                'title': book_info.get('title'),
                                'author': book_info.get('authors', ['Unknown'])[0],
                                'publication_date': book_info.get('publishedDate')
                            }
                        })

        return {
            'adaptations': adaptations,
            'total_found': len(adaptations)
        }

    def get_detailed_adaptation(self, movie_id: str, book_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific adaptation
        """
        movie_details = Movie.getDetails(movie_id)
        book_details = Book.getDetails(book_id)

        return {
            'movie': movie_details,
            'book': book_details,
            'comparison': {
                'release_gap': self._calculate_release_gap(
                    movie_details.get('release_date'),
                    book_details.get('volumeInfo', {}).get('publishedDate')
                )
            }
        }

    @staticmethod
    def _calculate_release_gap(movie_date: str, book_date: str) -> Optional[int]:
        """Calculate the time gap between book publication and movie release"""
        try:
            from datetime import datetime
            movie_year = datetime.strptime(movie_date, '%Y-%m-%d').year
            book_year = datetime.strptime(book_date, '%Y-%m-%d').year
            return movie_year - book_year
        except:
            return None
