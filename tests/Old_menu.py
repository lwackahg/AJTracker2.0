from app import create_app, db
from app.models import User, Book, MovieAdaptation, Review, Movie, Watchlist, ReadHistory, WatchHistory, ReadingList
from datetime import datetime
import requests
import os
import json

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu(current_user=None):
    print("\n=== Book to Movie Adaptation Tracker ===")
    if not current_user:
        print("1. Register")
        print("2. Login")
        print("3. Browse")
        print("4. Exit")
    else:
        print("1. Browse & Discover")
        print("2. My Lists")
        print("3. Discover Movie Adaptations")
        print("4. Logout")
        print("5. Exit")

def browse_menu(current_user=None):
    """Submenu for browsing and filtering content."""
    while True:
        clear_screen()
        print("\n=== Browse & Discover ===")
        print("1. Browse Popular Movies")
        print("2. Browse Popular Books")
        print("3. Filter Movies")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            browse_popular_movies(current_user)
        elif choice == "2":
            browse_popular_books(current_user)
        elif choice == "3":
            filter_movies()
        elif choice == "4":
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

def my_lists_menu(current_user):
    """Submenu for managing personal lists."""
    while True:
        clear_screen()
        print("\n=== My Lists ===")
        print("1. Watchlist")
        print("2. Reading List")
        print("3. Reviews")
        print("4. Reading History")
        print("5. Watch History")
        print("6. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            view_watchlist(current_user)
        elif choice == "2":
            view_reading_list(current_user)
        elif choice == "3":
            view_user_reviews(current_user)
        elif choice == "4":
            view_reading_history(current_user)
        elif choice == "5":
            view_watch_history(current_user)
        elif choice == "6":
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

def get_popular_movies():
    """Get a list of popular movies from TMDB API."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return []
    
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        return []

def create_movie_from_tmdb_data(movie_data):
    """Create a Movie object from TMDB API data."""
    release_date = None
    if movie_data.get('release_date'):
        try:
            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    return Movie(
        title=movie_data.get('title', ''),
        tmdb_id=movie_data.get('id'),
        releaseDate=release_date,  # Corrected attribute name
        overview=movie_data.get('overview', ''),
        average_rating=movie_data.get('vote_average', 0.0)
    )

def browse_popular_movies(current_user=None):
    """Browse popular movies and add to watchlist."""
    clear_screen()
    print("\n=== Popular Movies ===\n")
    
    movies_data = get_popular_movies()
    if not movies_data:
        print("No movies found.")
        return
    
    while True:
        for i, movie in enumerate(movies_data, 1):
            print(f"{i}. {movie.get('title', 'Unknown Title')}")
        
        try:
            choice = input("\nEnter a number to see details (or 0 to go back): ")
            if not choice.isdigit():
                print("\nPlease enter a valid number")
                continue
            
            choice = int(choice)
            if choice == 0:
                return
            
            if 1 <= choice <= len(movies_data):
                idx = choice - 1
                movie_data = movies_data[idx]
                
                clear_screen()
                print(f"\nTitle: {movie_data.get('title', 'N/A')}")
                print(f"Release Date: {movie_data.get('release_date', 'N/A')}")
                print(f"Rating: {movie_data.get('vote_average', 'N/A')}/10")
                print(f"Overview: {movie_data.get('overview', 'No overview available')}")
                
                if current_user:
                    print("\nOptions:")
                    print("1. Add to Watchlist")
                    print("2. Mark as Watched")
                    print("3. Go Back")
                    
                    action = input("\nEnter your choice: ")
                    if action == '1':
                        # Only create and save movie object when user wants to add it
                        movie = Movie.query.filter_by(tmdb_id=movie_data.get('id')).first()
                        if not movie:
                            movie = create_movie_from_tmdb_data(movie_data)
                            db.session.add(movie)
                            try:
                                db.session.commit()
                            except Exception as e:
                                print(f"Error saving movie: {e}")
                                db.session.rollback()
                                continue
                        
                        add_to_watchlist(current_user.UserId, movie_data)
                    elif action == '2':
                        # Only create and save movie object when user wants to add it
                        movie = Movie.query.filter_by(tmdb_id=movie_data.get('id')).first()
                        if not movie:
                            movie = create_movie_from_tmdb_data(movie_data)
                            db.session.add(movie)
                            try:
                                db.session.commit()
                            except Exception as e:
                                print(f"Error saving movie: {e}")
                                db.session.rollback()
                                continue
                        
                        mark_as_watched(current_user.UserId, movie_data)
                    elif action not in ['1', '2', '3']:
                        print("\nInvalid choice")
            else:
                print("\nInvalid choice. Please try again.")
        except ValueError:
            print("\nPlease enter a valid number")
        
        input("\nPress Enter to continue...")

def add_to_watchlist(user_id, movie_data):
    """Add a movie to user's watchlist."""
    try:
        # Check if movie exists in database
        movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
        if not movie:
            movie = create_movie_from_tmdb_data(movie_data)
            db.session.add(movie)
            db.session.commit()

        # Check if already in watchlist
        existing = Watchlist.query.filter_by(userID=user_id, movieID=movie.movieID).first()
        if existing:
            print("\nThis movie is already in your watchlist!")
            return

        # Add to watchlist
        watchlist_entry = Watchlist(userID=user_id, movieID=movie.movieID)
        db.session.add(watchlist_entry)
        db.session.commit()
        print("\nAdded to your watchlist!")

    except Exception as e:
        db.session.rollback()
        print(f"\nError adding to watchlist: {str(e)}")

def mark_as_watched(user_id, movie_data):
    """Mark a movie as watched."""
    print(f"Debug: Marking movie as watched with movie_data: {movie_data}")
    try:
        # Check if movie exists in database, create if not
        movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
        if not movie:
            print("Debug: Movie not found in database, creating new entry")
            movie = create_movie_from_tmdb_data(movie_data)
            db.session.add(movie)
            db.session.commit()

        # Check if already marked as watched
        existing = WatchHistory.query.filter_by(userID=user_id, movieID=movie.movieID).first()
        if existing:
            print("\nYou've already marked this movie as watched!")
            return

        # Add to watch history
        watch_history = WatchHistory(userID=user_id, movieID=movie.movieID)
        db.session.add(watch_history)
        
        # Remove from watchlist if present
        watchlist_entry = Watchlist.query.filter_by(userID=user_id, movieID=movie.movieID).first()
        if watchlist_entry:
            db.session.delete(watchlist_entry)
        
        db.session.commit()
        print(f"\nMarked '{movie.title}' as watched!")

    except Exception as e:
        db.session.rollback()
        print(f"\nError adding to watch history: {str(e)}")

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
    """Create a Book object from Google Books API data."""
    volume_info = book_data.get('volumeInfo', {})
    
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

    return Book(
        Title=volume_info.get('title'),
        Author=', '.join(volume_info.get('authors', ['Unknown'])),
        ISBN=volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
        GoogleBooksId=book_data.get('id'),
        Description=volume_info.get('description'),
        PublicationDate=pub_date,
        CoverImageUrl=volume_info.get('imageLinks', {}).get('thumbnail'),
        PageCount=volume_info.get('pageCount'),
        Rating=volume_info.get('averageRating', 0)
    )

def display_movie_details(movie):
    print(f"\nTitle: {movie['title']}")
    print(f"Release Date: {movie.get('release_date', 'N/A')}")
    print(f"Overview: {movie.get('overview', 'No overview available')}")
    print(f"Rating: {movie.get('vote_average', 'N/A')}/10")
    print("-" * 50)

def display_book_details(book):
    volume_info = book.get('volumeInfo', {})
    print(f"\nTitle: {volume_info.get('title', 'N/A')}")
    print(f"Author(s): {', '.join(volume_info.get('authors', ['Unknown']))}")
    print(f"Published: {volume_info.get('publishedDate', 'N/A')}")
    print(f"Description: {volume_info.get('description', 'No description available')[:200]}...")
    print("-" * 50)

def browse_popular_books(current_user=None):
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

def search():
    """Search for movies or books."""
    while True:
        clear_screen()
        print("\n=== Search ===")
        print("1. Search Movies")
        print("2. Search Books")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            query = input("\nEnter movie title to search: ")
            search_movies(query)
        elif choice == "2":
            query = input("\nEnter book title to search: ")
            search_books(query)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

def search_movies(query):
    """Search for movies using TMDB API."""
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return

    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get('results', [])

        if not movies:
            print("\nNo movies found")
            return

        print(f"\nFound {len(movies)} movies:")
        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
            print(f"   Rating: {movie.get('vote_average', 'N/A')}/10")
            print(f"   Overview: {movie.get('overview', 'No overview available')[:200]}...")

        input("\nPress Enter to continue...")

    except requests.RequestException as e:
        print(f"Error searching movies: {e}")

def search_books(query):
    """Search for books using Google Books API."""
    try:
        books = search_google_books(query)
        if not books:
            print("\nNo books found")
            return

        print(f"\nFound {len(books)} books:")
        for i, book in enumerate(books, 1):
            print(f"\n{i}. {book.get('volumeInfo', {}).get('title', 'Unknown Title')}")
            authors = book.get('volumeInfo', {}).get('authors', ['Unknown Author'])
            print(f"   Author(s): {', '.join(authors)}")
            print(f"   Published: {book.get('volumeInfo', {}).get('publishedDate', 'N/A')[:4]}")
            description = book.get('volumeInfo', {}).get('description', 'No description available')
            print(f"   Description: {description[:200]}...")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f"Error searching books: {e}")

def find_potential_adaptations(book_title=None, current_user=None):
    """Search for potential movie adaptations of a book."""
    clear_screen()
    if not book_title:
        book_title = input("\nEnter the book title to search for adaptations: ")
    print(f"\n=== Searching for Movie Adaptations of '{book_title}' ===")
    
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("Error: TMDB API key not found")
        return []

    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={book_title}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        movies = response.json().get('results', [])

        if not movies:
            print("No movie adaptations found.")
            return []

        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
            print(f"   Rating: {movie.get('vote_average', 'N/A')}/10")
            print(f"   Overview: {movie.get('overview', 'No overview available')[:200]}...")

        print("\nOptions:")
        print("1. View Movie Details")
        print("2. Add to Watchlist")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == '1':
            movie_num = int(input("\nEnter the movie number: "))
            if 1 <= movie_num <= len(movies):
                selected_movie = movies[movie_num - 1]
                clear_screen()
                print(f"\nTitle: {selected_movie['title']}")
                print(f"Release Date: {selected_movie.get('release_date', 'N/A')}")
                print(f"Rating: {selected_movie.get('vote_average', 'N/A')}/10")
                print(f"Overview: {selected_movie.get('overview', 'No overview available')}")
                
                if current_user:
                    print("\n1. Add to Watchlist")
                    print("2. Go Back")
                    sub_choice = input("\nEnter your choice: ")
                    if sub_choice == '1':
                        add_to_watchlist(current_user.UserId, selected_movie)
            else:
                print("Invalid movie number.")
        elif choice == '2':
            if current_user:
                movie_num = int(input("\nEnter the movie number: "))
                if 1 <= movie_num <= len(movies):
                    add_to_watchlist(current_user.UserId, movies[movie_num - 1])
                else:
                    print("Invalid movie number.")
            else:
                print("\nPlease login to add movies to your watchlist.")

        return movies

    except requests.RequestException as e:
        print(f"Error fetching potential adaptations: {e}")
        return []

    input("\nPress Enter to continue...")

def view_user_reviews(current_user):
    """View the current user's reviews."""
    while True:
        clear_screen()
        print("\n=== Your Reviews ===")
        print("1. View Book Reviews")
        print("2. View Movie Reviews")
        print("3. View All Reviews")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        try:
            if choice == "1":
                view_book_reviews_only(current_user)
            elif choice == "2":
                view_movie_reviews_only(current_user)
            elif choice == "3":
                view_all_reviews(current_user)
            elif choice == "4":
                break
            else:
                print("Invalid choice")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"Error viewing reviews: {e}")
            db.session.rollback()

def view_book_reviews_only(current_user):
    """View only book reviews."""
    print("\n=== Your Book Reviews ===")
    reviews = Review.query.filter_by(UserId=current_user.UserId).filter(
        Review.BookId.isnot(None)
    ).all()
    
    if not reviews:
        print("\nYou haven't reviewed any books yet.")
        return
    
    for review in reviews:
        book = db.session.get(Book, review.BookId)
        if book:
            print(f"\nBook: {book.Title}")
            print(f"Rating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            print(f"Date: {review.CreatedAt.strftime('%Y-%m-%d')}")
            print("-" * 40)

def view_movie_reviews_only(current_user):
    """View only movie reviews."""
    print("\n=== Your Movie Reviews ===")
    reviews = Review.query.filter_by(UserId=current_user.UserId).filter(
        Review.movieID.isnot(None)
    ).all()
    
    if not reviews:
        print("\nYou haven't reviewed any movies yet.")
        return
    
    for review in reviews:
        movie = db.session.get(Movie, review.movieID)
        if movie:
            print(f"\nMovie: {movie.title}")
            print(f"Rating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            print(f"Date: {review.CreatedAt.strftime('%Y-%m-%d')}")
            print("-" * 40)

def view_all_reviews(current_user):
    """View all reviews (both books and movies)."""
    print("\n=== All Your Reviews ===")
    reviews = Review.query.filter_by(UserId=current_user.UserId).all()
    
    if not reviews:
        print("\nYou haven't written any reviews yet.")
        return
    
    for review in reviews:
        if review.BookId:
            book = db.session.get(Book, review.BookId)
            if book:
                print(f"\nBook: {book.Title}")
                print(f"Rating: {review.Rating}/5")
                print(f"Review: {review.Comment}")
                print(f"Date: {review.CreatedAt.strftime('%Y-%m-%d')}")
                print("-" * 40)
        elif review.movieID:
            movie = db.session.get(Movie, review.movieID)
            if movie:
                print(f"\nMovie: {movie.title}")
                print(f"Rating: {review.Rating}/5")
                print(f"Review: {review.Comment}")
                print(f"Date: {review.CreatedAt.strftime('%Y-%m-%d')}")
                print("-" * 40)

def view_recent_reviews():
    """View recent reviews from all users."""
    clear_screen()
    print("\nRecent Reviews:")
    
    reviews = Review.query.order_by(Review.CreatedAt.desc()).limit(10).all()
    
    if reviews:
        for review in reviews:
            user = User.query.get(review.UserId)
            if review.BookId:
                book = Book.query.get(review.BookId)
                print(f"\nBook: {book.Title}")
            elif review.movieID:
                movie = Movie.query.get(review.movieID)
                print(f"\nMovie: {movie.title}")
            elif review.MovieAdaptationId:
                adaptation = MovieAdaptation.query.get(review.MovieAdaptationId)
                print(f"\nMovie Adaptation: {adaptation.Title}")
            
            print(f"By: {user.Username}")
            print(f"Rating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            print(f"Date: {review.CreatedAt.strftime('%Y-%m-%d')}")
            print("-" * 40)
    else:
        print("No reviews found.")

def view_reviews(current_user):
    """View and manage reviews."""
    while True:
        clear_screen()
        print("=== Reviews ===")
        print("1. View My Reviews")
        print("2. View Recent Reviews")
        print("3. Add New Review")
        print("4. Go Back")

        choice = input("\nEnter your choice: ")
        if choice == '1':
            view_user_reviews(current_user)
        elif choice == '2':
            view_recent_reviews()
        elif choice == '3':
            # Ensure both arguments are passed
            book = search_books()  # Assuming a function to select a book
            if book:
                add_book_review(book, current_user)
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again.")

def view_book_reviews(book, current_user=None):
    """View reviews for a specific book."""
    reviews = Review.query.filter_by(BookId=book.BookId).order_by(Review.ReviewDate.desc()).all()
    
    print(f"\nReviews for '{book.Title}':")
    if reviews:
        for review in reviews:
            print(f"\nRating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            print(f"Date: {review.ReviewDate.strftime('%Y-%m-%d')}")
            print("-" * 40)
        
        avg_rating = sum(r.Rating for r in reviews) / len(reviews)
        print(f"\nAverage Rating: {avg_rating:.1f}/5 ({len(reviews)} reviews)")
    else:
        print("No reviews yet.")
    
    if current_user:
        print("\n1. Add a Review")
        print("2. Go Back")
        choice = input("\nEnter your choice: ")
        if choice == '1':
            add_book_review(book, current_user)

def add_book_review(book, current_user):
    """Add a review for a specific book."""
    print("\nAdd Your Review")
    try:
        rating = float(input("Rating (1-5): "))
        if not 1 <= rating <= 5:
            print("Rating must be between 1 and 5")
            return
        
        review_text = input("Your review: ")
        
        review = Review(
            UserId=current_user.UserId,
            BookId=book.BookId,
            Rating=rating,
            Comment=review_text
        )
        
        db.session.add(review)
        db.session.commit()
        print("\nReview added successfully!")
        
    except ValueError:
        print("Please enter a valid rating number")
    except Exception as e:
        print(f"Error adding review: {e}")
        db.session.rollback()

def handle_local_book_selection(book, current_user=None):
    """Handle user selection of a local book."""
    while True:
        print(f"\nSelected: '{book.Title}' by {book.Author}")
        print("\nOptions:")
        print("1. View/Add Reviews")
        print("2. Find Movie Adaptations")
        print("3. Add to Reading History")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        if not current_user and choice in ['1', '2', '3']:
            print("\nPlease login to use this feature")
            input("\nPress Enter to continue...")
            continue
        
        if choice == '1':
            view_book_reviews(book, current_user)
        elif choice == '2':
            book_title = input("\nEnter the book title to search for adaptations: ")
            find_potential_adaptations(book_title, current_user)
        elif choice == '3':
            if current_user:
                add_to_reading_history(book, current_user)
            else:
                print("Please login to add to reading history")
        elif choice == '4':
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

def search_google_books(query):
    """Search Google Books API for a book."""
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

def get_book_details(movie_title):
    """Try to find book details from Google Books API based on movie title."""
    # Remove common movie-specific words
    search_terms = movie_title.lower()
    for term in ['the movie', 'film', 'movie adaptation', 'part 1', 'part 2', 'part one', 'part two']:
        search_terms = search_terms.replace(term, '')
    
    # Add "book" to help find the original book
    books = search_google_books(f"{search_terms} book")
    
    if books:
        # Try to find the most relevant book
        best_match = None
        highest_score = 0
        
        for book in books:
            volume_info = book.get('volumeInfo', {})
            # Skip if it's not a book
            if 'book' not in volume_info.get('printType', '').lower():
                continue
                
            # Calculate relevance score
            score = 0
            title = volume_info.get('title', '').lower()
            if search_terms.strip() in title:
                score += 3
            if volume_info.get('authors'):
                score += 1
            if volume_info.get('description'):
                score += 1
            if volume_info.get('industryIdentifiers'):
                score += 1
            
            if score > highest_score:
                highest_score = score
                best_match = book
        
        if best_match:
            return best_match
    
    return None

def add_book_from_google(book_data):
    """Add a book to our database using Google Books data."""
    try:
        volume_info = book_data['volumeInfo']
        pub_date = datetime.strptime(volume_info.get('publishedDate', '2000'), '%Y')
        
        # Check if book already exists by Google Books ID
        existing_book = Book.query.filter_by(GoogleBooksId=book_data['id']).first()
        if existing_book:
            return existing_book
        
        # Create new book
        book = Book(
            Title=volume_info.get('title'),
            Author=', '.join(volume_info.get('authors', ['Unknown'])),
            ISBN=volume_info.get('industryIdentifiers', [{}])[0].get('identifier'),
            GoogleBooksId=book_data['id'],
            Description=volume_info.get('description'),
            PublicationDate=pub_date,
            CoverImageUrl=volume_info.get('imageLinks', {}).get('thumbnail')
        )
        db.session.add(book)
        db.session.commit()
        return book
    except Exception as e:
        print(f"Error adding book: {e}")
        db.session.rollback()
        return None

def register_user():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(Username=username).first()
        if existing_user:
            print("Username already taken.")
            return None

        # Create a new user
        new_user = User(Username=username, Email=email)
        new_user.set_password(password)  # Assuming there's a method to hash passwords
        db.session.add(new_user)
        db.session.commit()
        print("Registration successful!")
        return new_user
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

    return None

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    try:
        # Query the database for the user
        user = User.query.filter_by(Username=username).first()
        if user and user.check_password(password):
            print("Login successful!")
            return user
        else:
            print("Invalid username or password.")
    except Exception as e:
        print(f"Error: {e}")

    return None

def view_watchlist(current_user):
    """View the watchlist for the current user."""
    if not current_user:
        print("\nPlease login to view your watchlist")
        return
    
    clear_screen()
    print("\n=== Your Watchlist ===")
    
    try:
        watchlist_items = Watchlist.query.filter_by(userID=current_user.UserId).all()
        
        if not watchlist_items:
            print("\nYour watchlist is empty")
            return
        
        for item in watchlist_items:
            movie = db.session.get(Movie, item.movieID)
            if movie:
                print(f"\nTitle: {movie.title}")
                print(f"Added on: {item.added_date.strftime('%Y-%m-%d')}")
                print(f"Rating: {movie.average_rating}/10")
                print("-" * 50)
    
    except Exception as e:
        print(f"Error viewing watchlist: {e}")

def view_reading_history(current_user):
    """View the reading history for the current user."""
    clear_screen()
    print("\n=== Reading History ===\n")
    
    reading_history = ReadHistory.query.filter_by(userID=current_user.UserId).all()
    
    if not reading_history:
        print("No reading history found.")
        return
    
    for entry in reading_history:
        book = Book.query.get(entry.bookID)
        if book:
            print(f"\nBook: {book.Title}")
            print(f"Author: {book.Author}")
            print(f"Date Read: {entry.read_date.strftime('%Y-%m-%d')}")
            print("-" * 30)

def view_watch_history(current_user):
    """Display the user's watch history with movie titles."""
    watch_history_items = WatchHistory.query.filter_by(userID=current_user.UserId).all()
    if not watch_history_items:
        print("\nYour watch history is empty")
        return

    print("\n=== Your Watch History ===")
    for item in watch_history_items:
        movie = db.session.get(Movie, item.movieID)
        if movie:
            print(f"\nMovie: {movie.title}")
            print(f"Watched on: {item.watched_date}")
        else:
            print(f"\nMovie ID {item.movieID} not found in database.")

    input("\nPress Enter to continue...")

def handle_book_selection(book, current_user=None):
    """Handle user selection of a book."""
    while True:
        print(f"\nSelected Book: {book.Title}")
        print(f"Author: {book.Author}")
        print("\nOptions:")
        print("1. Add to Reading List")
        print("2. Mark as Read")
        print("3. Write a Review")
        print("4. View Reviews")
        print("5. Find Movie Adaptations")
        print("6. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        if not current_user and choice in ['1', '2', '3']:
            print("\nPlease login to use this feature")
            input("\nPress Enter to continue...")
            continue
        
        if choice == '1':
            add_to_reading_list(book, current_user)
        elif choice == '2':
            add_to_reading_history(book, current_user)
        elif choice == '3':
            add_book_review(book, current_user)
        elif choice == '4':
            view_book_reviews(book, current_user)
        elif choice == '5':
            book_title = input("\nEnter the book title to search for adaptations: ")
            find_potential_adaptations(book_title, current_user)
        elif choice == '6':
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

def add_to_reading_list(book, current_user):
    """Add a book to the user's reading list."""
    if not current_user:
        print("\nPlease login to add books to your reading list")
        return

    try:
        # Check if already in reading list
        existing = ReadingList.query.filter_by(
            userID=current_user.UserId,
            bookID=book.BookId
        ).first()
        
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

def view_reading_list(current_user):
    """View the current user's reading list."""
    if not current_user:
        print("\nPlease login to view your reading list")
        return
    
    clear_screen()
    print("\n=== Your Reading List ===")
    
    try:
        reading_list = ReadingList.query.filter_by(UserId=current_user.UserId).all()
        
        if not reading_list:
            print("Your reading list is empty.")
            input("\nPress Enter to continue...")
            return
        
        # Display all books in reading list
        books_dict = {}  # To store books for selection
        for i, entry in enumerate(reading_list, 1):
            book = Book.query.get(entry.bookID)
            if book:
                books_dict[i] = book
                print(f"\nTitle: {book.Title}")
                print(f"Author: {book.Author}")
                print(f"Added on: {entry.added_date.strftime('%Y-%m-%d')}")
        
        print("\nOptions:")
        print("1. Move to Reading History")
        print("2. Delete from Reading List")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            # Let user select which book to move
            print("\nSelect a book to move to reading history:")
            for i, book in books_dict.items():
                print(f"{i}. {book.Title}")
            
            try:
                book_choice = int(input("\nEnter book number: "))
                if book_choice in books_dict:
                    selected_book = books_dict[book_choice]
                    add_to_reading_history(selected_book, current_user)
                else:
                    print("Invalid book number")
            except ValueError:
                print("Please enter a valid number")
        elif choice == "2":
            delete_from_reading_list(current_user)
        elif choice != "3":
            print("Invalid choice")
    except Exception as e:
        print(f"Error retrieving reading list: {e}")
        db.session.rollback()

def add_to_reading_history(book, current_user):
    """Add a book to the user's reading history."""
    try:
        # Check if already in reading history
        existing = ReadHistory.query.filter_by(
            userID=current_user.UserId,
            bookID=book.BookId
        ).first()
        
        if existing:
            print("This book is already in your reading history")
            return
        
        # Add to reading history
        reading_entry = ReadHistory(
            userID=current_user.UserId,
            bookID=book.BookId,
            read_date=datetime.utcnow()
        )
        db.session.add(reading_entry)
        db.session.commit()
        print(f"\nAdded '{book.Title}' to your reading history!")
        
    except Exception as e:
        print(f"Error adding to reading history: {e}")
        db.session.rollback()

def handle_movie_selection(movie, current_user=None):
    """Handle user selection of a movie."""
    while True:
        print(f"\nSelected Movie: {movie.title}")
        print("\nWhat would you like to do?")
        print("1. Add to Watchlist")
        print("2. Mark as Watched")
        print("3. Write a Review")
        print("4. Go Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            add_to_watchlist(movie, current_user)
        elif choice == "2":
            add_to_watch_history(movie, current_user)
        elif choice == "3":
            add_movie_review(movie, current_user)
        elif choice == "4":
            break
        else:
            print("Invalid choice")

def filter_movies():
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
            filter_by_genre()
        elif choice == '2':
            filter_by_year()
        elif choice == '3':
            filter_by_rating()
        elif choice == '4':
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

def filter_by_genre():
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
                        display_filtered_movies(movies)
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

def filter_by_year():
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
                display_filtered_movies(movies)
            else:
                print("Error fetching movies")
        else:
            print("Invalid year")
    except Exception as e:
        print(f"Error: {e}")

def filter_by_rating():
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
                display_filtered_movies(movies)
            else:
                print("Error fetching movies")
        else:
            print("Invalid rating. Please enter a number between 0 and 10")
    except ValueError:
        print("Please enter a valid number")
    except Exception as e:
        print(f"Error: {e}")

def display_filtered_movies(movies, current_user=None):
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
                            add_to_watchlist(current_user.UserId, selected_movie)
                        elif option == '2':
                            mark_as_watched(current_user.UserId, selected_movie)
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

def move_to_watch_history(current_user):
    """Move a movie from the watchlist to the watch history."""
    session = db.session
    watchlist_items = session.query(Watchlist).filter_by(userID=current_user.UserId).all()
    if not watchlist_items:
        print("\nYour watchlist is empty")
        return

    print("\n=== Move to Watch History ===")
    for i, item in enumerate(watchlist_items, 1):
        movie = session.get(Movie, item.movieID)
        if movie:
            print(f"{i}. {movie.title}")

    choice = input("\nEnter the number of the movie to move (or 0 to cancel): ")
    if choice.isdigit() and 1 <= int(choice) <= len(watchlist_items):
        selected_item = watchlist_items[int(choice) - 1]
        movie = session.get(Movie, selected_item.movieID)
        if movie:
            movie_data = {
                'id': movie.tmdb_id,
                'title': movie.title,
                'release_date': movie.releaseDate.strftime('%Y-%m-%d') if movie.releaseDate else None,
                'overview': movie.overview,
                'vote_average': movie.average_rating
            }
            mark_as_watched(current_user.UserId, movie_data)
            # Remove from watchlist
            session.delete(selected_item)
            session.commit()
            print("\nMovie moved to watch history!")
        else:
            print("\nError: Movie not found in database")
    else:
        print("Invalid choice.")

def delete_from_watchlist(current_user):
    """Delete a movie from the user's watchlist."""
    session = db.session
    watchlist_items = session.query(Watchlist).filter_by(userID=current_user.UserId).all()
    if not watchlist_items:
        print("\nYour watchlist is empty")
        return

    print("\n=== Delete from Watchlist ===")
    for i, item in enumerate(watchlist_items, 1):
        movie = session.get(Movie, item.movieID)
        if movie:
            print(f"{i}. {movie.title}")

    choice = input("\nEnter the number of the movie to delete (or 0 to cancel): ")
    if choice.isdigit() and 1 <= int(choice) <= len(watchlist_items):
        selected_item = watchlist_items[int(choice) - 1]
        session.delete(selected_item)
        session.commit()
        print("\nMovie deleted from watchlist!")
    else:
        print("Invalid choice.")

def delete_from_watch_history(current_user):
    """Delete a movie from the user's watch history."""
    session = db.session
    watch_history_items = session.query(WatchHistory).filter_by(userID=current_user.UserId).all()
    if not watch_history_items:
        print("\nYour watch history is empty")
        return

    print("\n=== Delete from Watch History ===")
    for i, item in enumerate(watch_history_items, 1):
        movie = session.get(Movie, item.movieID)
        if movie:
            print(f"{i}. {movie.title}")

    choice = input("\nEnter the number of the movie to delete (or 0 to cancel): ")
    if choice.isdigit() and 1 <= int(choice) <= len(watch_history_items):
        selected_item = watch_history_items[int(choice) - 1]
        session.delete(selected_item)
        session.commit()
        print("\nMovie deleted from watch history!")
    else:
        print("Invalid choice.")

def delete_from_reading_list(current_user):
    """Delete a book from the user's reading list."""
    session = db.session
    reading_list_items = session.query(ReadingList).filter_by(userID=current_user.UserId).all()
    if not reading_list_items:
        print("\nYour reading list is empty")
        return

    print("\n=== Delete from Reading List ===")
    for i, item in enumerate(reading_list_items, 1):
        book = session.get(Book, item.bookID)
        if book:
            print(f"{i}. {book.Title}")

    choice = input("\nEnter the number of the book to delete (or 0 to cancel): ")
    if choice.isdigit() and 1 <= int(choice) <= len(reading_list_items):
        selected_item = reading_list_items[int(choice) - 1]
        session.delete(selected_item)
        session.commit()
        print("\nBook deleted from reading list!")
    else:
        print("Invalid choice.")

def delete_from_reading_history(current_user):
    """Delete a book from the user's reading history."""
    session = db.session
    reading_history_items = session.query(ReadHistory).filter_by(userID=current_user.UserId).all()
    if not reading_history_items:
        print("\nYour reading history is empty")
        return

    print("\n=== Delete from Reading History ===")
    for i, item in enumerate(reading_history_items, 1):
        book = session.get(Book, item.bookID)
        if book:
            print(f"{i}. {book.Title}")

    choice = input("\nEnter the number of the book to delete (or 0 to cancel): ")
    if choice.isdigit() and 1 <= int(choice) <= len(reading_history_items):
        selected_item = reading_history_items[int(choice) - 1]
        session.delete(selected_item)
        session.commit()
        print("\nBook deleted from reading history!")
    else:
        print("Invalid choice.")

def view_watchlist(current_user):
    """View the watchlist for the current user."""
    watchlist_items = Watchlist.query.filter_by(userID=current_user.UserId).all()
    if not watchlist_items:
        print("\nYour watchlist is empty")
        return

    print("\n=== Your Watchlist ===")
    for item in watchlist_items:
        movie = db.session.get(Movie, item.movieID)
        if movie:
            print(f"\nTitle: {movie.title}")
            print(f"Added on: {item.added_date.strftime('%Y-%m-%d')}")

    print("\nOptions:")
    print("1. Move to Watch History")
    print("2. Delete from Watchlist")
    print("3. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        move_to_watch_history(current_user)
    elif choice == "2":
        delete_from_watchlist(current_user)
    elif choice != "3":
        print("Invalid choice")

def view_watch_history(current_user):
    """Display the user's watch history with movie titles."""
    watch_history_items = WatchHistory.query.filter_by(userID=current_user.UserId).all()
    if not watch_history_items:
        print("\nYour watch history is empty")
        return

    print("\n=== Your Watch History ===")
    for item in watch_history_items:
        movie = db.session.get(Movie, item.movieID)
        if movie:
            print(f"\nMovie: {movie.title}")
            print(f"Watched on: {item.watched_date}")

    print("\nOptions:")
    print("1. Delete from Watch History")
    print("2. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        delete_from_watch_history(current_user)
    elif choice != "2":
        print("Invalid choice")

def view_reading_list(current_user):
    """View the current user's reading list."""
    reading_list_items = ReadingList.query.filter_by(userID=current_user.UserId).all()
    if not reading_list_items:
        print("\nYour reading list is empty")
        return

    print("\n=== Your Reading List ===")
    for item in reading_list_items:
        book = db.session.get(Book, item.bookID)
        if book:
            print(f"\nTitle: {book.Title}")
            print(f"Author: {book.Author}")
            print(f"Added on: {item.added_date.strftime('%Y-%m-%d')}")

    print("\nOptions:")
    print("1. Move to Reading History")
    print("2. Delete from Reading List")
    print("3. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        # Let user select which book to move
        print("\nSelect a book to move to reading history:")
        for i, item in enumerate(reading_list_items, 1):
            book = db.session.get(Book, item.bookID)
            if book:
                print(f"{i}. {book.Title}")
        
        try:
            book_choice = int(input("\nEnter book number: "))
            if book_choice in books_dict:
                selected_book = books_dict[book_choice]
                add_to_reading_history(selected_book, current_user)
            else:
                print("Invalid book number")
        except ValueError:
            print("Please enter a valid number")
    elif choice == "2":
        delete_from_reading_list(current_user)
    elif choice != "3":
        print("Invalid choice")

def view_reading_history(current_user):
    """View the reading history for the current user."""
    reading_history_items = ReadHistory.query.filter_by(userID=current_user.UserId).all()
    if not reading_history_items:
        print("\nYour reading history is empty")
        return

    print("\n=== Your Reading History ===")
    for item in reading_history_items:
        book = db.session.get(Book, item.bookID)
        if book:
            print(f"\nBook: {book.Title}")
            print(f"Author: {book.Author}")
            print(f"Read on: {item.read_date.strftime('%Y-%m-%d')}")

    print("\nOptions:")
    print("1. Delete from Reading History")
    print("2. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        delete_from_reading_history(current_user)
    elif choice != "2":
        print("Invalid choice")

def view_reading_history(current_user):
    """View the reading history for the current user."""
    clear_screen()
    print("\n=== Your Reading History ===\n")
    
    try:
        history_items = ReadHistory.query.filter_by(userID=current_user.UserId).all()
        
        if not history_items:
            print("\nYour reading history is empty")
            input("\nPress Enter to continue...")
            return
        
        books_dict = {}  # To store books for selection
        for i, item in enumerate(history_items, 1):
            book = Book.query.get(item.bookID)
            if book:
                books_dict[i] = (book, item)
                print(f"\nTitle: {book.Title}")
                print(f"Author: {book.Author}")
                print(f"Date Read: {item.read_date.strftime('%Y-%m-%d')}")
                
                # Check if there's a review
                review = Review.query.filter_by(
                    UserId=current_user.UserId,
                    BookId=book.BookId,
                    movieID=None
                ).first()
                
                if review:
                    print(f"Your Rating: {review.Rating}/5")
                    print(f"Your Review: {review.Comment}")
                else:
                    print("Not reviewed yet")
                print("-" * 50)
        
        print("\nOptions:")
        print("1. Write/Edit Review")
        print("2. Delete from History")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            # Let user select which book to review
            print("\nSelect a book to review:")
            for i, (book, _) in books_dict.items():
                print(f"{i}. {book.Title}")
            
            try:
                book_choice = int(input("\nEnter book number: "))
                if book_choice in books_dict:
                    selected_book = books_dict[book_choice][0]
                    add_book_review(selected_book, current_user)
                else:
                    print("Invalid book number")
            except ValueError:
                print("Please enter a valid number")
        elif choice == "2":
            delete_from_reading_history(current_user)
        elif choice != "3":
            print("Invalid choice")
            
    except Exception as e:
        print(f"Error retrieving reading history: {e}")
        db.session.rollback()

def view_watch_history(current_user):
    """Display the user's watch history with movie titles."""
    clear_screen()
    print("\n=== Your Watch History ===")
    
    try:
        history_items = WatchHistory.query.filter_by(userID=current_user.UserId).all()
        
        if not history_items:
            print("\nYour watch history is empty")
            input("\nPress Enter to continue...")
            return
        
        movies_dict = {}  # To store movies for selection
        for i, item in enumerate(history_items, 1):
            movie = Movie.query.get(item.movieID)
            if movie:
                movies_dict[i] = (movie, item)
                print(f"\nTitle: {movie.title}")
                if movie.releaseDate:
                    print(f"Release Date: {movie.releaseDate.strftime('%Y-%m-%d')}")
                print(f"Watched on: {item.watched_date}")
                
                # Check if there's a review
                review = Review.query.filter_by(
                    UserId=current_user.UserId,
                    movieID=movie.movieID,
                    BookId=None
                ).first()
                
                if review:
                    print(f"Your Rating: {review.Rating}/5")
                    print(f"Your Review: {review.Comment}")
                else:
                    print("Not reviewed yet")
                print("-" * 50)
        
        print("\nOptions:")
        print("1. Write/Edit Review")
        print("2. Delete from History")
        print("3. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            # Let user select which movie to review
            print("\nSelect a movie to review:")
            for i, (movie, _) in movies_dict.items():
                print(f"{i}. {movie.title}")
            
            try:
                movie_choice = int(input("\nEnter movie number: "))
                if movie_choice in movies_dict:
                    selected_movie = movies_dict[movie_choice][0]
                    add_movie_review(selected_movie, current_user)
                else:
                    print("Invalid movie number")
            except ValueError:
                print("Please enter a valid number")
        elif choice == "2":
            delete_from_watch_history(current_user)
        elif choice != "3":
            print("Invalid choice")
            
    except Exception as e:
        print(f"Error retrieving watch history: {e}")
        db.session.rollback()

def add_movie_review(movie, current_user):
    """Add or edit a review for a movie."""
    clear_screen()
    print(f"\n=== Review for {movie.title} ===")
    
    try:
        # Check if review already exists
        review = Review.query.filter_by(
            UserId=current_user.UserId,
            movieID=movie.movieID,
            BookId=None
        ).first()
        
        if review:
            print("\nExisting review found:")
            print(f"Rating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            
            if not get_yes_no_input("\nWould you like to edit this review? (y/n): "):
                return
        
        # Get rating
        while True:
            try:
                rating = float(input("\nEnter rating (0-5): "))
                if 0 <= rating <= 5:
                    break
                print("Rating must be between 0 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        # Get review text
        review_text = input("\nEnter your review: ")
        
        if review:
            # Update existing review
            review.Rating = rating
            review.Comment = review_text
            review.CreatedAt = datetime.utcnow()
        else:
            # Create new review
            review = Review(
                UserId=current_user.UserId,
                movieID=movie.movieID,
                Rating=rating,
                Comment=review_text
            )
            db.session.add(review)
        
        db.session.commit()
        print("\nReview saved successfully!")
        
    except Exception as e:
        print(f"Error saving review: {e}")
        db.session.rollback()

def add_book_review(book, current_user):
    """Add or edit a review for a book."""
    clear_screen()
    print(f"\n=== Review for {book.Title} ===")
    
    try:
        # Check if review already exists
        review = Review.query.filter_by(
            UserId=current_user.UserId,
            BookId=book.BookId,
            movieID=None
        ).first()
        
        if review:
            print("\nExisting review found:")
            print(f"Rating: {review.Rating}/5")
            print(f"Review: {review.Comment}")
            
            if not get_yes_no_input("\nWould you like to edit this review? (y/n): "):
                return
        
        # Get rating
        while True:
            try:
                rating = float(input("\nEnter rating (0-5): "))
                if 0 <= rating <= 5:
                    break
                print("Rating must be between 0 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        # Get review text
        review_text = input("\nEnter your review: ")
        
        if review:
            # Update existing review
            review.Rating = rating
            review.Comment = review_text
            review.CreatedAt = datetime.utcnow()
        else:
            # Create new review
            review = Review(
                UserId=current_user.UserId,
                BookId=book.BookId,
                Rating=rating,
                Comment=review_text
            )
            db.session.add(review)
        
        db.session.commit()
        print("\nReview saved successfully!")
        
    except Exception as e:
        print(f"Error saving review: {e}")
        db.session.rollback()

def get_yes_no_input(prompt):
    """Get a yes/no input from the user."""
    while True:
        response = input(prompt).lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def main():
    """Main function to run the application."""
    app = create_app()
    with app.app_context():
        current_user = None
        
        while True:
            clear_screen()
            
            print_menu(current_user)
            
            if current_user:
                print(f"\nLogged in as: {current_user.Username}")
            
            choice = input("\nEnter your choice: ")
            
            if not current_user:
                if choice == '1':
                    current_user = register_user()
                elif choice == '2':
                    current_user = login_user()
                elif choice == '3':
                    browse_menu()
                elif choice == '4':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice")
            else:
                if choice == '1':
                    browse_menu(current_user)
                elif choice == '2':
                    my_lists_menu(current_user)
                elif choice == '3':
                    book_title = input("\nEnter the book title to search for adaptations: ")
                    find_potential_adaptations(book_title, current_user)
                elif choice == '4':
                    current_user = None
                    print("Logged out successfully")
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
