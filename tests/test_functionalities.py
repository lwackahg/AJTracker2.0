from app import create_app, db
from app.models import User, Book, MovieAdaptation, Review

def setup_app_context():
    app = create_app()
    app.app_context().push()


def test_user_registration_and_login():
    print("Testing user registration and login...")
    user = User(Username='testuser', Email='testuser@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Attempt to login
    registered_user = User.query.filter_by(Email='testuser@example.com').first()
    if registered_user and registered_user.check_password('password'):
        print("User login successful.")
    else:
        print("User login failed.")


def test_add_book():
    print("Testing book addition...")
    book = Book(Title='Test Book', Author='Test Author')
    db.session.add(book)
    db.session.commit()

    # Verify book addition
    added_book = Book.query.filter_by(Title='Test Book').first()
    if added_book:
        print("Book addition successful.")
    else:
        print("Book addition failed.")


def test_add_movie_adaptation():
    print("Testing movie adaptation addition...")
    book = Book.query.filter_by(Title='Test Book').first()
    if book:
        movie_adaptation = MovieAdaptation(Title='Test Movie', BookId=book.BookId)
        db.session.add(movie_adaptation)
        db.session.commit()

        # Verify movie adaptation addition
        added_adaptation = MovieAdaptation.query.filter_by(Title='Test Movie').first()
        if added_adaptation:
            print("Movie adaptation addition successful.")
        else:
            print("Movie adaptation addition failed.")
    else:
        print("Book for adaptation not found.")


def test_add_review():
    print("Testing review addition...")
    movie_adaptation = MovieAdaptation.query.filter_by(Title='Test Movie').first()
    if movie_adaptation:
        review = Review(UserId=1, MovieAdaptationId=movie_adaptation.MovieAdaptationId, Rating=5, Comment='Great movie!')
        db.session.add(review)
        db.session.commit()

        # Verify review addition
        added_review = Review.query.filter_by(Comment='Great movie!').first()
        if added_review:
            print("Review addition successful.")
        else:
            print("Review addition failed.")
    else:
        print("Movie adaptation for review not found.")


def cleanup():
    print("Cleaning up test data...")
    Review.query.delete()
    MovieAdaptation.query.delete()
    Book.query.delete()
    User.query.delete()
    db.session.commit()


def run_tests():
    setup_app_context()
    test_user_registration_and_login()
    test_add_book()
    test_add_movie_adaptation()
    test_add_review()
    cleanup()


if __name__ == "__main__":
    run_tests()
