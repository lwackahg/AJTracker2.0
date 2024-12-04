import requests
from datetime import datetime

class GoogleBooksClient:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        
    def search_books(self, query):
        """Search for books using Google Books API"""
        params = {
            'q': query,
            'maxResults': 10
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json().get('items', [])
    
    def get_book_details(self, book_id):
        """Get detailed information about a specific book"""
        url = f"{self.base_url}/{book_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_similar_books(self, book_id):
        """Get a list of similar books based on the given book"""
        # Get book details first
        book = self.get_book_details(book_id)
        
        # Use relevant info from the book to find similar ones
        if 'volumeInfo' in book:
            authors = book['volumeInfo'].get('authors', [])
            categories = book['volumeInfo'].get('categories', [])
            
            # Build a query based on author and category
            query = []
            if authors:
                query.append(f'inauthor:{authors[0]}')
            if categories:
                query.append(f'subject:{categories[0]}')
                
            if query:
                return self.search_books(' '.join(query))
        
        return []
    
    def get_book_by_isbn(self, isbn):
        """Search for a book by ISBN"""
        return self.search_books(f'isbn:{isbn}')
