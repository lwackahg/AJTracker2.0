import os
import requests
from datetime import datetime

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_movie_details(movie):
    """Display detailed information about a movie."""
    print(f"\nTitle: {movie['title']}")
    print(f"Release Date: {movie.get('release_date', 'N/A')}")
    print(f"Overview: {movie.get('overview', 'No overview available')}")
    print(f"Rating: {movie.get('vote_average', 'N/A')}/10")
    print(f"Genres: {', '.join(genre['name'] for genre in movie.get('genres', []))}")

def display_book_details(book):
    """Display detailed information about a book."""
    # Handle both Google Books API response and our database Book objects
    if isinstance(book, dict):
        # Google Books API response
        volume_info = book.get('volumeInfo', {})
        print(f"\nTitle: {volume_info.get('title', 'N/A')}")
        print(f"Author(s): {', '.join(volume_info.get('authors', ['Unknown']))}")
        print(f"Published: {volume_info.get('publishedDate', 'N/A')}")
        print(f"Categories: {', '.join(volume_info.get('categories', ['N/A']))}")
        print(f"Description: {volume_info.get('description', 'No description available')}")
    else:
        # Database Book object
        print(f"\nTitle: {book.Title}")
        print(f"Author: {book.Author}")
        print(f"Published: {book.PublicationDate if book.PublicationDate else 'N/A'}")
        print(f"Description: {book.Description if book.Description else 'No description available'}")

def get_yes_no_input(prompt):
    """Get a yes/no input from the user."""
    while True:
        response = input(prompt).lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def search_google_books(query):
    """Search Google Books API for a book."""
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    if not api_key:
        print("Error: Google Books API key not found")
        return []

    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.RequestException as e:
        print(f"Error searching for books: {e}")
        return []

def get_book_details(movie_title):
    """Try to find book details from Google Books API based on movie title."""
    books = search_google_books(movie_title)
    if not books:
        print(f"No books found for movie title '{movie_title}'")
        return

    book = books[0]  # Assume the first result is the most relevant
    volume_info = book.get('volumeInfo', {})
    print(f"\nTitle: {volume_info.get('title', 'N/A')}")
    print(f"Author(s): {', '.join(volume_info.get('authors', ['Unknown']))}")
    print(f"Published: {volume_info.get('publishedDate', 'N/A')}")
    print(f"Description: {volume_info.get('description', 'No description available')}")

def add_book_from_google(book_data):
    """Add a book to the database from Google Books data."""
    from app import db
    from app.models import Book
    
    try:
        # Extract volume info
        volume_info = book_data.get('volumeInfo', {})
        
        # Create new book object
        book = Book(
            title=volume_info.get('title', 'Unknown Title'),
            author=', '.join(volume_info.get('authors', ['Unknown'])),
            description=volume_info.get('description', ''),
            published_date=volume_info.get('publishedDate', ''),
            categories=', '.join(volume_info.get('categories', [])),
            page_count=volume_info.get('pageCount', 0),
            average_rating=volume_info.get('averageRating', 0.0),
            ratings_count=volume_info.get('ratingsCount', 0),
            google_books_id=book_data.get('id', '')
        )
        
        # Add and commit to database
        db.session.add(book)
        db.session.commit()
        return book
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding book to database: {str(e)}")
        return None
