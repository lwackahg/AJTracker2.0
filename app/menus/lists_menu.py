# Development Viewpoint: Menu Module Structure
# This module is part of the menus package, handling user list management functionality
# Logical Viewpoint: List Management Component
# Handles user interactions for watchlists, reading lists, and their respective histories
# Process Viewpoint: User List Workflow
# Manages the flow of adding, viewing, and managing user lists and reviews
# Physical Viewpoint: Database Integration Layer
# Interfaces with SQLAlchemy models for persistent storage of user lists
# Scenario Viewpoint: User List Management
# Supports various user scenarios for managing their media consumption

from app import db
from app.models import Watchlist, ReadingList, WatchHistory, ReadHistory, Movie, Book
from app.services.tmdb_service import create_movie_from_tmdb_data
from .utils import clear_screen, display_movie_details, display_book_details
from . import review_menu
from datetime import datetime

# Development Viewpoint: Function Documentation
# This module implements the personal lists management functionality
# Logical Viewpoint: Implements the sequence diagram for user list interactions
# Process Viewpoint: Handles the workflow for managing watchlists and histories
# Scenario Viewpoint: Provides user interaction flows for list management
# Physical Viewpoint: Integrates with Flask and MySQL database for data persistence

# Development Viewpoint: Main Menu Interface
# Provides the primary interface for list management functionality
def my_lists_menu(current_user):
    """Submenu for managing personal lists."""
    while True:
        clear_screen()
        print("\n=== My Lists ===")
        print("1. View Watchlist")
        print("2. View Watch History  (Add Review's Here)")
        print("3. View Reading List")
        print("4. View Reading History (Add Review's Here)")
        print("5. View My Reviews")
        print("6. Go Back")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            view_watchlist(current_user)
        elif choice == "2":
            view_watch_history(current_user)
        elif choice == "3":
            view_reading_list(current_user)
        elif choice == "4":
            view_reading_history(current_user)
        elif choice == "5":
            review_menu.view_user_reviews(current_user)
        elif choice == "6":
            break
        else:
            print("Invalid choice")
        
        input("\nPress Enter to continue...")

# Physical Viewpoint: Watchlist Data Management
# Handles database operations for user watchlist
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

# Process Viewpoint: Watch History Management
# Implements the workflow for tracking watched movies
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
    print("1. Add/Edit Review")
    print("2. Delete from Watch History")
    print("3. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        # Let user select a movie
        print("\n=== Select a Movie to Review ===")
        for i, item in enumerate(watch_history_items, 1):
            movie = db.session.get(Movie, item.movieID)
            if movie:
                print(f"{i}. {movie.title}")
        
        try:
            movie_choice = int(input("\nEnter the number of the movie to review (or 0 to cancel): "))
            if movie_choice > 0 and movie_choice <= len(watch_history_items):
                movie = db.session.get(Movie, watch_history_items[movie_choice-1].movieID)
                if movie:
                    review_menu.add_movie_review(movie, current_user)
        except ValueError:
            print("Please enter a valid number")
    elif choice == "2":
        delete_from_watch_history(current_user)
    elif choice != "3":
        print("Invalid choice")

# Physical Viewpoint: Reading History Storage
# Manages the persistent storage of completed books
def add_to_reading_history(book, current_user):
    """Add a book to the user's reading history and remove from reading list."""
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
        
        # Remove from reading list
        reading_list_entry = ReadingList.query.filter_by(
            userID=current_user.UserId,
            bookID=book.BookId
        ).first()
        if reading_list_entry:
            db.session.delete(reading_list_entry)
            
        db.session.commit()
        print(f"\nAdded '{book.Title}' to your reading history!")
        
    except Exception as e:
        print(f"Error adding to reading history: {e}")
        db.session.rollback()


# Logical Viewpoint: Reading List Component
# Implements the reading list management logic
def view_reading_list(current_user):
    """View the current user's reading list."""
    if not current_user:
        print("\nPlease login to view your reading list")
        return
    
    clear_screen()
    print("\n=== Your Reading List ===")
    
    try:
        reading_list = ReadingList.query.filter_by(userID=current_user.UserId).all()
        
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

# Process Viewpoint: Reading History Workflow
# Manages the process of tracking read books
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
    print("1. Add/Edit Review")
    print("2. Delete from Reading History")
    print("3. Go Back")
    
    choice = input("\nEnter your choice: ")
    if choice == "1":
        # Let user select a book
        print("\n=== Select a Book to Review ===")
        for i, item in enumerate(reading_history_items, 1):
            book = db.session.get(Book, item.bookID)
            if book:
                print(f"{i}. {book.Title}")
        
        try:
            book_choice = int(input("\nEnter the number of the book to review (or 0 to cancel): "))
            if book_choice > 0 and book_choice <= len(reading_history_items):
                book = db.session.get(Book, reading_history_items[book_choice-1].bookID)
                if book:
                    review_menu.add_book_review(book, current_user)
        except ValueError:
            print("Please enter a valid number")
    elif choice == "2":
        delete_from_reading_history(current_user)
    elif choice != "3":
        print("Invalid choice")

# Development Viewpoint: Watchlist Operations
# Implements core watchlist manipulation functions
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

# Logical Viewpoint: Reading List Operations
# Handles the core reading list functionality
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


# Process Viewpoint: Watch Status Update
# Manages the workflow of moving items to watch history
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


# Process Viewpoint: Reading Status Update
# Handles the process of marking books as read
def move_to_reading_history(current_user):
    """Move a book from the reading list to the reading history."""
    try:
        # Get reading list items
        reading_list = ReadingList.query.filter_by(UserId=current_user.UserId).all()
        if not reading_list:
            print("\nYour reading list is empty")
            return

        print("\n=== Move to Reading History ===")
        for i, item in enumerate(reading_list, 1):
            book = Book.query.get(item.BookId)
            if book:
                print(f"{i}. {book.Title}")

        choice = input("\nEnter the number of the book to move (or 0 to cancel): ")
        if choice.isdigit() and 1 <= int(choice) <= len(reading_list):
            selected_item = reading_list[int(choice) - 1]
            book = Book.query.get(selected_item.BookId)
            
            if book:
                # Add to reading history
                history_item = ReadHistory(
                    userID=current_user.UserId,
                    bookID=book.BookId,
                    read_date=datetime.utcnow()
                )
                db.session.add(history_item)
                
                # Remove from reading list
                db.session.delete(selected_item)
                db.session.commit()
                print("\nBook moved to reading history!")
            else:
                print("\nError: Book not found in database")
        else:
            print("Invalid choice.")
    except Exception as e:
        print(f"Error moving book to reading history: {e}")
        db.session.rollback()


# Physical Viewpoint: Watchlist Cleanup
# Manages removal of items from watchlist
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


# Physical Viewpoint: Watch History Cleanup
# Handles deletion of watch history entries
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

# Physical Viewpoint: Reading List Cleanup
# Manages removal of items from reading list
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

# Physical Viewpoint: Reading History Cleanup
# Handles deletion of reading history entries
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


# Process Viewpoint: Movie Status Tracking
# Implements the workflow for marking movies as watched
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

# Process Viewpoint: Book Status Tracking
# Implements the workflow for marking books as read
def mark_as_read(user_id, book_data):
    """Mark a book as read."""
    try:
        # Add to reading history
        add_to_reading_history(book_data, user_id)
        print(f"\nMarked '{book_data.Title}' as read")
    except Exception as e:
        print(f"Error marking book as read: {e}")
        db.session.rollback()
