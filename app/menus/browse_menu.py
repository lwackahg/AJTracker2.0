# Development Viewpoint: Browse Menu Module
# This module handles all browsing functionality for both movies and books
# Logical Viewpoint: Content Discovery Component
# Manages the discovery and exploration of media content
# Process Viewpoint: Browse Workflow
# Implements the flow of searching, filtering, and selecting content
# Physical Viewpoint: External API Integration
# Interfaces with TMDb and Google Books APIs for content retrieval
# Scenario Viewpoint: User Discovery Experience
# Supports various user scenarios for discovering and interacting with content

from app import db
from app.models import Movie, Book, MovieAdaptation, ReadingList
from app.services.tmdb_service import get_popular_movies, search_movies, create_movie_from_tmdb_data
from app.services.google_books_service import get_popular_books, search_books, create_book_from_google_data
from .utils import clear_screen, display_movie_details, display_book_details, get_yes_no_input
from . import lists_menu, review_menu
from datetime import datetime
import os
import requests
import json

# Scenario Viewpoint: Browse Interface
# Provides the main entry point for content discovery
def browse_menu(current_user=None):
    # Scenario Viewpoint: Main Browse Interface
    # Provides the main entry point for browsing both movies and books
    """Submenu for browsing and filtering content."""
    while True:
        clear_screen()
        print("\n=== Browse & Discover ===")
        print("1. Browse Popular Movies")
        print("2. Browse Popular Books")
        print("3. Filter Movies")
        print("4. Search")
        print("5. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            browse_popular_movies(current_user)
        elif choice == "2":
            browse_popular_books(current_user)
        elif choice == "3":
            filter_movies(current_user)
        elif choice == "4":
            search(current_user)
        elif choice == "5":
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

# Process Viewpoint: Movie Discovery
# Implements the workflow for discovering popular movies
def browse_popular_movies(current_user=None):
    # Process Viewpoint: Movie Search Workflow
    # Implements the movie search and display process using TMDb API
    """Browse popular movies and add to watchlist."""
    movies = get_popular_movies()
    if not movies:
        print("Unable to fetch popular movies at this time.")
        return

    while True:
        clear_screen()
        print("\n=== Popular Movies ===")
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
        print("\n0. Go Back")

        choice = input("\nSelect a movie (number) to see details: ")
        if choice == "0":
            break
        
        try:
            movie = movies[int(choice) - 1]
            # Ensure user is logged in before adding to watchlist
            if current_user:
                handle_movie_selection(movie, current_user)
            else:
                print("\nPlease login to add movies to your watchlist.")
                input("\nPress Enter to continue...")
        except (IndexError, ValueError):
            print("\nInvalid choice. Please enter a number from the list.")
            input("\nPress Enter to continue...")

# Process Viewpoint: Book Discovery
# Implements the workflow for discovering popular books
def browse_popular_books(current_user=None):
    # Process Viewpoint: Book Search Workflow
    # Manages book search and display using Google Books API
    """Browse popular books and add to reading list."""
    clear_screen()
    print("\n=== Popular Books ===\n")
    
    books_data = get_popular_books()
    if not books_data:
        print("No books found.")
        return
    
    while True:
        for i, book in enumerate(books_data, 1):
            title = book.get('volumeInfo', {}).get('title', 'Unknown Title')
            print(f"{i}. {title}")
        
        try:
            choice = input("\nEnter a number to see details (or 0 to go back): ")
            if not choice.isdigit():
                print("\nPlease enter a valid number")
                continue
                
            choice = int(choice)
            if choice == 0:
                return
                
            if 1 <= choice <= len(books_data):
                idx = choice - 1
                book_data = books_data[idx]
                volume_info = book_data.get('volumeInfo', {})
                
                clear_screen()
                print(f"\nTitle: {volume_info.get('title', 'N/A')}")
                print(f"Author(s): {', '.join(volume_info.get('authors', ['Unknown']))}")
                print(f"Published: {volume_info.get('publishedDate', 'N/A')}")
                print(f"Description: {volume_info.get('description', 'No description available')}")
                print("-" * 50)
                
                print("1. Add to Reading List")
                print("2. Go Back")
                choice = input("\nEnter your choice: ")
                if choice == '1':
                    # Only create and save book object when user wants to add it
                    book = Book.query.filter_by(GoogleBooksId=book_data.get('id')).first()
                    if not book:
                        book = create_book_from_google_data(book_data)
                        db.session.add(book)
                        try:
                            db.session.commit()
                        except Exception as e:
                            print(f"Error saving book: {e}")
                            db.session.rollback()
                            continue
                    
                    add_to_reading_list(book, current_user)
                elif choice == '2':
                    return
                else:
                    print("Invalid choice")
            else:
                print("\nInvalid choice. Please try again.")
        except ValueError:
            print("\nPlease enter a valid number")
        
        input("\nPress Enter to continue...")

# Logical Viewpoint: Movie Selection
# Manages the logic for movie selection and interaction
def handle_movie_selection(movie, current_user=None):
    # Physical Viewpoint: Movie Data Presentation
    # Handles the structured display of movie information
    """Handle user selection of a movie."""
    clear_screen()
    display_movie_details(movie)
    
    if current_user:
        print("\nOptions:")
        print("1. Add to Watchlist")
        print("2. Mark as Watched")
        print("3. Write Review")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            lists_menu.add_to_watchlist(current_user.UserId, movie)
        elif choice == "2":
            lists_menu.mark_as_watched(current_user.UserId, movie)
        elif choice == "3":
            movie_obj = create_movie_from_tmdb_data(movie)
            review_menu.add_movie_review(movie_obj, current_user)

# Logical Viewpoint: Book Selection
# Manages the logic for book selection and interaction
def handle_book_selection(book, current_user=None):
    # Physical Viewpoint: Book Data Presentation
    # Manages the structured display of book information
    """Handle user selection of a book."""
    clear_screen()
    display_book_details(book)
    
    if current_user:
        print("\nOptions:")
        print("1. Add to Reading List")
        print("2. Mark as Read")
        print("3. Write Review")
        print("4. Find Movie Adaptations")
        print("5. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            book_obj = create_book_from_google_data(book)
            lists_menu.add_to_reading_list(book_obj, current_user)
        elif choice == "2":
            book_obj = create_book_from_google_data(book)
            lists_menu.add_to_reading_history(book_obj, current_user)
        elif choice == "3":
            book_obj = create_book_from_google_data(book)
            review_menu.add_book_review(book_obj, current_user)
        elif choice == "4":
            find_potential_adaptations(book['volumeInfo'].get('title'), current_user, book)
        elif choice == "5":
            return
        else:
            print("Invalid choice")

# Logical Viewpoint: Local Book Selection
# Handles selection of books from local database
def handle_local_book_selection(book, current_user=None):
    # Physical Viewpoint: Book Data Presentation
    # Manages the structured display of book information
    """Handle user selection of a local book."""
    while True:
        clear_screen()
        print(f"\nTitle: {book.Title}")
        print(f"Author: {book.Author}")
        print(f"Published: {book.PublicationDate}")
        if book.Description:
            print(f"Description: {book.Description}")
        
        # Show existing adaptations
        adaptations = MovieAdaptation.query.filter_by(BookId=book.BookId).all()
        if adaptations:
            print("\nKnown Movie Adaptations:")
            for adaptation in adaptations:
                print(f"- {adaptation.Title} ({adaptation.ReleaseDate.strftime('%Y') if adaptation.ReleaseDate else 'N/A'})")
        
        if current_user:
            print("\nOptions:")
            print("1. Add to Reading List")
            print("2. Mark as Read")
            print("3. Write Review")
            print("4. Find Movie Adaptations")
            print("5. Go Back")
            
            choice = input("\nEnter your choice: ")
            if choice == "1":
                lists_menu.add_to_reading_list(book, current_user)
            elif choice == "2":
                lists_menu.add_to_reading_history(book, current_user)
            elif choice == "3":
                review_menu.add_book_review(book, current_user)
            elif choice == "4":
                find_potential_adaptations(book.Title, current_user, book)
            elif choice == "5":
                break
            else:
                print("Invalid choice")
                input("\nPress Enter to continue...")
        else:
            print("\nPlease login to access more options")
            input("\nPress Enter to continue...")
            break

# Process Viewpoint: Movie Filtering
# Implements the workflow for filtering movies
def filter_movies(current_user=None):
    # Scenario Viewpoint: Movie Filtering Interface
    # Provides the main entry point for filtering movies
    """Filter and browse movies based on different criteria."""
    while True:
        clear_screen()
        print("\n=== Filter Movies ===")
        print("1. Filter by Genre")
        print("2. Filter by Release Year")
        print("3. Filter by Rating")
        print("4. Go Back")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            filter_by_genre(current_user)
        elif choice == '2':
            filter_by_year(current_user)
        elif choice == '3':
            filter_by_rating(current_user)
        elif choice == '4':
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

# Logical Viewpoint: Genre Filtering
# Manages the logic for filtering movies by genre
def filter_by_genre(current_user=None):
    # Process Viewpoint: Movie Genre Filtering Workflow
    # Implements the movie genre filtering process using TMDb API
    """Filter movies by genre."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return

    # First, get the list of available genres
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    try:
        response = requests.get(url)
        if response.ok:
            genres = response.json().get('genres', [])
            
            print("\nAvailable Genres:")
            for i, genre in enumerate(genres, 1):
                print(f"{i}. {genre['name']}")
            
            try:
                choice = int(input("\nSelect a genre (number): "))
                if 1 <= choice <= len(genres):
                    selected_genre = genres[choice - 1]
                    
                    # Get movies in this genre
                    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={selected_genre["id"]}&sort_by=popularity.desc'
                    response = requests.get(url)
                    
                    if response.ok:
                        movies = response.json().get('results', [])
                        display_filtered_movies(movies, current_user)
                    else:
                        print("Error fetching movies")
                else:
                    print("Invalid genre selection")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Error fetching genres")
    except Exception as e:
        print(f"Error: {e}")

# Logical Viewpoint: Year Filtering
# Manages the logic for filtering movies by year
def filter_by_year(current_user=None):
    # Process Viewpoint: Movie Release Year Filtering Workflow
    # Implements the movie release year filtering process using TMDb API
    """Filter movies by release year."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return

    try:
        year = input("\nEnter the release year (e.g., 2023): ")
        if year.isdigit() and 1900 <= int(year) <= datetime.now().year:
            url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_year={year}&sort_by=popularity.desc'
            response = requests.get(url)
            
            if response.ok:
                movies = response.json().get('results', [])
                display_filtered_movies(movies, current_user)
            else:
                print("Error fetching movies")
        else:
            print("Invalid year")
    except Exception as e:
        print(f"Error: {e}")

# Logical Viewpoint: Rating Filtering
# Manages the logic for filtering movies by rating
def filter_by_rating(current_user=None):
    # Process Viewpoint: Movie Rating Filtering Workflow
    # Implements the movie rating filtering process using TMDb API
    """Filter movies by minimum rating."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return

    try:
        min_rating = float(input("\nEnter minimum rating (0-10): "))
        if 0 <= min_rating <= 10:
            url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&vote_average.gte={min_rating}&sort_by=vote_average.desc'
            response = requests.get(url)
            
            if response.ok:
                movies = response.json().get('results', [])
                display_filtered_movies(movies, current_user)
            else:
                print("Error fetching movies")
        else:
            print("Invalid rating. Please enter a number between 0 and 10")
    except ValueError:
        print("Please enter a valid number")
    except Exception as e:
        print(f"Error: {e}")

# Development Viewpoint: Movie Display
# Implements the presentation of filtered movie results
def display_filtered_movies(movies, current_user=None):
    # Physical Viewpoint: Movie Data Presentation
    # Handles the structured display of movie information
    """Display a list of filtered movies with options to interact."""
    if not movies:
        print("\nNo movies found matching your criteria")
        return

    while True:
        clear_screen()
        print("\n=== Filtered Movies ===")
        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
            print(f"   Rating: {movie.get('vote_average', 'N/A')}/10")
            print(f"   Overview: {movie.get('overview', 'No overview available')[:150]}...")
        print("\nOptions:")
        print("1. Select a movie for more details")
        print("2. Go Back")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            try:
                movie_index = int(input("\nEnter movie number: ")) - 1
                if 0 <= movie_index < len(movies):
                    selected_movie = movies[movie_index]
                    clear_screen()
                    print(f"\nTitle: {selected_movie['title']}")
                    print(f"Release Date: {selected_movie.get('release_date', 'N/A')}")
                    print(f"Rating: {selected_movie.get('vote_average', 'N/A')}/10")
                    print(f"Overview: {selected_movie.get('overview', 'No overview available')}")
                    
                    if current_user:
                        print("\nOptions:")
                        print("1. Add to Watchlist")
                        print("2. Mark as Watched")
                        print("3. Go Back")
                        
                        option = input("\nEnter your choice: ")
                        if option == '1':
                            lists_menu.add_to_watchlist(current_user.UserId, selected_movie)
                        elif option == '2':
                            lists_menu.mark_as_watched(current_user.UserId, selected_movie)
                    else:
                        print("\nPlease login to add movies to your watchlist or mark as watched")
                    
                    input("\nPress Enter to continue...")
                else:
                    print("Invalid movie selection")
            except ValueError:
                print("Please enter a valid number")
        elif choice == '2':
            break
        else:
            print("Invalid choice")

# Process Viewpoint: Adaptation Discovery
# Implements the workflow for finding and confirming movie adaptations
# Physical Viewpoint: Integration Layer
# Manages integration between Google Books API, TMDb API, and local database
# Logical Viewpoint: Adaptation Confirmation
# Handles the logic for verifying and saving book-to-movie adaptations
def find_potential_adaptations(book_title=None, current_user=None, book=None):
    # Process Viewpoint: Book Adaptation Search Workflow
    # Implements the book adaptation search process using TMDb API
    """Search for potential movie adaptations of a book."""
    if not book_title:
        book_title = input("\nEnter the book title to search for adaptations: ")
    
    # Search for movies with similar titles
    movies = search_movies(book_title)
    if not movies:
        print(f"No potential adaptations found for '{book_title}'")
        input("\nPress Enter to continue...")
        return

    while True:
        clear_screen()
        print(f"\n=== Potential Movie Adaptations for '{book_title}' ===")
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
        print("\n0. Go Back")

        choice = input("\nSelect a movie (number) to see details: ")
        if choice == "0":
            break
        
        try:
            movie = movies[int(choice) - 1]
            clear_screen()
            print(f"\nMovie Details:")
            print(f"Title: {movie['title']}")
            print(f"Release Date: {movie.get('release_date', 'N/A')}")
            print(f"Overview: {movie.get('overview', 'No overview available')}")
            
            if current_user:
                print("\nOptions:")
                print("1. Confirm this is an adaptation")
                print("2. View movie details")
                print("3. Go back")
                
                action = input("\nEnter your choice: ")
                if action == "1":
                    # If we got a dictionary from Google Books API, create a Book object
                    if isinstance(book, dict):
                        book_obj = create_book_from_google_data(book)
                        if not book_obj:
                            print("\nError: Could not create book record")
                            input("\nPress Enter to continue...")
                            continue
                    else:
                        book_obj = book
                    
                    # Check if adaptation already exists
                    existing = MovieAdaptation.query.filter_by(
                        BookId=book_obj.BookId,
                        TmdbId=str(movie['id'])
                    ).first()
                    
                    if existing:
                        print("\nThis adaptation is already saved in the database!")
                    else:
                        # Create movie record if it doesn't exist
                        movie_record = Movie.query.filter_by(tmdb_id=movie['id']).first()
                        if not movie_record:
                            movie_record = create_movie_from_tmdb_data(movie)
                            if not movie_record:
                                print("\nError: Could not create movie record")
                                input("\nPress Enter to continue...")
                                continue
                        
                        # Create adaptation record
                        adaptation = MovieAdaptation(
                            Title=movie['title'],
                            BookId=book_obj.BookId,
                            movieID=movie_record.movieID,
                            Overview=movie.get('overview'),
                            ReleaseDate=datetime.strptime(movie['release_date'], '%Y-%m-%d') if movie.get('release_date') else None,
                            TmdbId=str(movie['id']),
                            PosterPath=movie.get('poster_path')
                        )
                        db.session.add(adaptation)
                        try:
                            db.session.commit()
                            print("\nAdaptation successfully saved!")
                        except Exception as e:
                            db.session.rollback()
                            print(f"\nError saving adaptation: {e}")
                    input("\nPress Enter to continue...")
                elif action == "2":
                    handle_movie_selection(movie, current_user)
            else:
                handle_movie_selection(movie, current_user)
        except (ValueError, IndexError):
            print("Invalid choice")
            input("\nPress Enter to continue...")

# Physical Viewpoint: Reading List Storage
# Manages the persistent storage of reading list items
def add_to_reading_list(book, current_user):
    # Logical Viewpoint: Reading List Management
    # Handles reading list additions with data consistency checks
    """Add a book to the user's reading list."""
    if not current_user:
        print("\nPlease login to add books to your reading list")
        return

    try:
        # Check if already in reading list
        existing = ReadingList.query.filter_by(userID=current_user.UserId, bookID=book.BookId).first()
        
        if existing:
            print("\nThis book is already in your reading list")
            return
        
        # Add to reading list
        reading_item = ReadingList(
            userID=current_user.UserId,
            bookID=book.BookId,
            added_date=datetime.utcnow()
        )
        db.session.add(reading_item)
        db.session.commit()
        print(f"\nAdded '{book.Title}' to your reading list!")
        
    except Exception as e:
        print(f"\nError adding to reading list: {e}")
        db.session.rollback()

# Process Viewpoint: Content Search
# Implements the workflow for searching movies and books
def search(current_user=None):
    # Scenario Viewpoint: Search Interface
    # Provides the main entry point for searching movies and books
    """Search for movies or books."""
    while True:
        clear_screen()
        print("\n=== Search ===")
        print("1. Search Movies")
        print("2. Search Books")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            query = input("\nEnter movie title to search for: ")
            movies = search_movies(query)
            if movies:
                display_filtered_movies(movies, current_user)
            else:
                print("No movies found matching your search.")
                input("\nPress Enter to continue...")
                
        elif choice == "2":
            query = input("\nEnter book title or author to search for: ")
            books = search_books(query)
            if books:
                while True:
                    clear_screen()
                    print("\n=== Search Results ===")
                    for i, book in enumerate(books, 1):
                        volume_info = book.get('volumeInfo', {})
                        print(f"{i}. {volume_info.get('title')} by {', '.join(volume_info.get('authors', ['Unknown']))}")
                    print("\n0. Go Back")
                    
                    choice = input("\nSelect a book (number) to see details: ")
                    if choice == "0":
                        break
                        
                    try:
                        choice = int(choice)
                        if 1 <= choice <= len(books):
                            handle_book_selection(books[choice - 1], current_user)
                        else:
                            print("Invalid choice")
                    except ValueError:
                        print("Invalid input")
                    
                    input("\nPress Enter to continue...")
            else:
                print("No books found matching your search.")
                input("\nPress Enter to continue...")
                
        elif choice == "3":
            break
            
        else:
            print("Invalid choice")
            input("\nPress Enter to continue...")

# Physical Viewpoint: Saved Adaptations Display
# Manages the display of saved movie adaptations
def view_saved_adaptations(book=None):
    """View saved movie adaptations for a book or all saved adaptations."""
    clear_screen()
    if book:
        adaptations = MovieAdaptation.query.filter_by(BookId=book.BookId).all()
        print(f"\n=== Movie Adaptations for '{book.Title}' ===")
    else:
        adaptations = MovieAdaptation.query.all()
        print("\n=== All Saved Movie Adaptations ===")
    
    if not adaptations:
        print("\nNo saved adaptations found.")
        input("\nPress Enter to continue...")
        return
    
    for i, adaptation in enumerate(adaptations, 1):
        book = Book.query.get(adaptation.BookId)
        print(f"\n{i}. Movie: {adaptation.Title}")
        print(f"   Book: {book.Title}")
        print(f"   Release Date: {adaptation.ReleaseDate.strftime('%Y-%m-%d') if adaptation.ReleaseDate else 'N/A'}")
        if adaptation.Overview:
            print(f"   Overview: {adaptation.Overview[:150]}...")
        print("-" * 50)
    
    input("\nPress Enter to continue...")
