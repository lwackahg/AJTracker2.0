import argparse
import sys
from app import create_app, db
from app.models import Movie, Book
from app.tmdb_client import TMDBClient
from app.google_books_client import GoogleBooksClient


def run_tests():
    """Run all tests."""
    print("Running tests...")
    # Here you can call the unittest framework to run tests


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully.")


def test_tmdb_search():
    """Test TMDB search functionality."""
    tmdb = TMDBClient()
    results = tmdb.search_movies("Inception")
    if results:
        print(f"Found movie: {results[0]['title']}")
    else:
        print("No movie found.")


def test_google_books_search():
    """Test Google Books search functionality."""
    google_books = GoogleBooksClient()
    results = google_books.search_books("Dune")
    if results:
        print(f"Found book: {results[0]['volumeInfo']['title']}")
    else:
        print("No book found.")


def main():
    parser = argparse.ArgumentParser(description="CLI tool for testing application features.")
    parser.add_argument('command', choices=['run_tests', 'reset_db', 'test_tmdb', 'test_books'],
                        help="Command to run.")

    args = parser.parse_args()

    if args.command == 'run_tests':
        run_tests()
    elif args.command == 'reset_db':
        reset_database()
    elif args.command == 'test_tmdb':
        test_tmdb_search()
    elif args.command == 'test_books':
        test_google_books_search()
    else:
        print("Unknown command.")
        sys.exit(1)


if __name__ == '__main__':
    main()
