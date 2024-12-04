# Development Viewpoint: Review Module Structure
# This module is part of the menus package, handling all review-related functionality
# Logical Viewpoint: Review Management Component
# Manages the creation, viewing, and organization of user reviews
# Process Viewpoint: Review Workflow
# Implements the flow of creating, editing, and viewing reviews
# Physical Viewpoint: Database Integration Layer
# Interfaces with SQLAlchemy models for persistent storage of reviews
# Scenario Viewpoint: User Review Management
# Supports various user scenarios for managing their media reviews

from .utils import clear_screen
from app import db
from app.models import Review, Book, Movie
import requests
import os
import json
from datetime import datetime


# Process Viewpoint: Review Navigation
# Implements the main review navigation workflow
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

# Logical Viewpoint: Book Review Component
# Handles the organization and display of book reviews
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

# Logical Viewpoint: Movie Review Component
# Manages the display of movie-specific reviews
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

# Development Viewpoint: Review Display
# Implements the comprehensive review display functionality
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

# Scenario Viewpoint: Community Interaction
# Facilitates user interaction through recent review display
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

# Process Viewpoint: Review Management
# Handles the workflow of viewing and managing reviews
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

# Physical Viewpoint: Book Review Storage
# Manages the persistent storage of book reviews
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

# Process Viewpoint: Book Review Creation
# Implements the workflow for adding book reviews
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

# Logical Viewpoint: Book Selection
# Manages the logic for selecting books to review
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

# Process Viewpoint: Movie Review Creation
# Implements the workflow for adding movie reviews
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
