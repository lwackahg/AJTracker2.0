import os
import requests
from app.models import Book
from datetime import datetime
from app import db

def get_popular_books():
    """Get a list of popular books from Google Books API."""
    try:
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': 'subject:fiction',  # Search for fiction books
            'orderBy': 'newest',     # Get newest books
            'maxResults': 10,        # Limit to 10 results
            'langRestrict': 'en'     # English books only
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.RequestException as e:
        print(f"Error fetching popular books: {e}")
        return []

def create_book_from_google_data(book_data):
    """Create or retrieve a Book object from Google Books API data."""
    volume_info = book_data.get('volumeInfo', {})
    google_books_id = book_data.get('id')
    
    # Check if book already exists
    existing_book = Book.query.filter_by(GoogleBooksId=google_books_id).first()
    if existing_book:
        return existing_book
    
    # Convert the publication date to a date object
    pub_date = None
    if 'publishedDate' in volume_info:
        try:
            pub_date = datetime.strptime(volume_info['publishedDate'], '%Y-%m-%d').date()
        except ValueError:
            try:
                pub_date = datetime.strptime(volume_info['publishedDate'], '%Y-%m').date()
            except ValueError:
                try:
                    pub_date = datetime.strptime(volume_info['publishedDate'], '%Y').date()
                except ValueError:
                    pub_date = None

    # Create new book object
    book = Book(
        Title=volume_info.get('title', 'Unknown Title'),
        Author=', '.join(volume_info.get('authors', ['Unknown'])),
        ISBN=volume_info.get('industryIdentifiers', [{}])[0].get('identifier', ''),
        GoogleBooksId=google_books_id,
        Description=volume_info.get('description', ''),
        PublicationDate=pub_date,
        CoverImageUrl=volume_info.get('imageLinks', {}).get('thumbnail', ''),
        PageCount=volume_info.get('pageCount', 0),
        Rating=volume_info.get('averageRating', 0)
    )
    
    try:
        db.session.add(book)
        db.session.commit()
        return book
    except Exception as e:
        print(f"\nError saving book: {e}")
        db.session.rollback()
        return None

def search_books(query):
    """Search for books using Google Books API."""
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    if not api_key:
        print("Error: Google Books API key not found")
        return []
    
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    try:
        response = requests.get(url)
        if response.ok:
            return response.json().get('items', [])
    except Exception as e:
        print(f"Error searching Google Books: {e}")
    return []
