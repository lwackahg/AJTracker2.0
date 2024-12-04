# Book to Movie Adaptation Tracker (`app/`)

A comprehensive application for tracking and discovering book-to-movie adaptations, managing reading lists, and sharing reviews.

## Project Structure (`app/`)
- **Core Components** (`app/core/`)
  - Database models (`app/core/models/`)
  - Configuration (`app/core/config/`)
  - Utilities (`app/core/utils/`)

- **User Interface** (`app/menus/`)
  - Main menu (`app/menus/main_menu.py`)
  - Authentication (`app/menus/auth_menu.py`)
  - Browse content (`app/menus/browse_menu.py`)
  - Manage lists (`app/menus/lists_menu.py`)
  - Review system (`app/menus/review_menu.py`)

- **Services** (`app/services/`)
  - TMDb integration (`app/services/tmdb_service.py`)
  - Google Books integration (`app/services/google_books_service.py`)
  - Authentication (`app/services/auth_service.py`)
  - Data management (`app/services/data_service.py`)

## Recent Updates (`docs/changelog.md`)

### Enhanced Menu Structure (`app/menus/`)
1. **Streamlined Navigation** (`app/menus/main_menu.py`)
   - Reorganized main menu for better user experience
   - Created intuitive submenus for related features
   - Simplified access to core functionalities

2. **Browse & Discover Submenu** (`app/menus/browse_menu.py`)
   - Browse Popular Movies
   - Browse Popular Books
   - Filter Movies by various criteria
   - Quick access to all discovery features

3. **My Lists Submenu** (`app/menus/lists_menu.py`)
   - Unified access to personal lists
   - Watchlist management
   - Reading list management
   - Review management
   - Reading and Watch history

### Enhanced Review System (`app/menus/review_menu.py`)
1. **Comprehensive Review Management** (`app/models/review.py`)
   - Write and edit reviews for books and movies
   - View reviews by category (books/movies/all)
   - Rating system (0-5 stars)
   - Detailed review comments
   - Review date tracking

2. **History Integration** (`app/services/history_service.py`)
   - Review books from reading history
   - Review movies from watch history
   - View existing reviews while browsing history
   - Edit capabilities for existing reviews

### Enhanced Adaptation Tracking
1. **Improved Adaptation Search**
   - Integration with TMDb API for comprehensive movie search
   - Automatic book record creation from Google Books data
   - Duplicate checking to prevent multiple confirmations
   - User-friendly confirmation workflow

2. **Adaptation Management**
   - View confirmed adaptations for specific books
   - Browse all confirmed adaptations
   - Automatic movie record creation from TMDb data
   - Persistent storage of adaptation relationships

3. **Integration Layer**
   - Seamless integration between Google Books and TMDb APIs
   - Automatic conversion of API responses to database records
   - Error handling and user feedback
   - Consistent data presentation across sources

## Requirements Implementation

### Functional Requirements

#### R1: Film Adaptation Search
- **Location**: `app/menus/browse_menu.py`
- **Implementation**: 
  - `find_potential_adaptations()` function for searching and confirming adaptations
  - Integration with TMDb API for movie search
  - Integration with Google Books API for book data
  - Cross-reference functionality between books and movies
  - Local database storage for confirmed adaptations
  - Duplicate checking to prevent multiple confirmations

#### R2: Movie Logging and Reviews
- **Location**: `app/menus/review_menu.py`
- **Implementation**:
  - Rating system (0-5 stars)
  - Personal review management
  - Watch history tracking
  - Analytics service integration

#### R3: Adaptation Feedback
- **Location**: `app/menus/review_menu.py`, `app/models/review.py`
- **Implementation**:
  - Unified review system for books and movies
  - Comparison functionality
  - Review editing capabilities

#### R6: User Account Management
- **Location**: `app/menus/auth_menu.py`
- **Implementation**:
  - User registration and login system
  - Session management
  - Personal history tracking

#### R7: Movie Filtering
- **Location**: `app/menus/browse_menu.py`
- **Implementation**:
  - Genre-based filtering
  - Release year filtering
  - Rating-based filtering

#### R8: Watchlist Management
- **Location**: `app/menus/lists_menu.py`
- **Implementation**:
  - Personal watchlist creation
  - Reading list management
  - Add/remove functionality

### Non-Functional Requirements

#### R4: Response Time
- **Location**: `app/services/performance_monitor.py`
- **Implementation**:
  - Performance monitoring system
  - Metrics collection
  - Weekly performance reports

#### R5: Data Privacy
- **Location**: `app/services/auth_service.py`, `app/config/security.py`
- **Implementation**:
  - Password hashing with Werkzeug
  - Secure session management
  - User data protection

#### R9: Database Backups
- **Location**: `app/services/backup_service.py`
- **Implementation**:
  - Automated daily backups
  - Backup monitoring
  - Weekly backup reports

### Design Patterns

#### Adapter Pattern
- **Location**: `app/adapters/`
  - `tmdb_adapter.py`
  - `google_books_adapter.py`
- **Purpose**: Standardizes data format across different APIs

#### Observer Pattern
- **Location**: `app/services/notification_service.py`
- **Purpose**: Handles notifications and user preference tracking

#### Singleton Pattern
- **Location**: `app/services/`
  - `session_manager.py`
  - `db_manager.py`
  - `config_manager.py`
- **Purpose**: Manages shared resources and configurations

## Features

### Content Discovery
- **Movie and Book Search** (`app/menus/browse_menu.py`)
  - Search across multiple platforms (`app/services/tmdb_service.py`, `app/services/google_books_service.py`)
  - Advanced filtering options (`app/menus/browse_menu.py:filter_content()`)
  - Detailed information display (`app/views/content_view.py`)
  - Find movie adaptations (`app/menus/browse_menu.py:find_potential_adaptations()`)

### User Collections
- **Watchlist Management** (`app/menus/lists_menu.py`)
  - Add/remove movies (`app/menus/lists_menu.py:manage_watchlist()`)
  - Sort and filter watchlist (`app/models/watchlist.py`)
  - Track watching progress (`app/models/watch_history.py`)
  - Get recommendations (`app/services/recommendation_service.py`)

- **Reading List** (`app/menus/lists_menu.py`)
  - Manage books (`app/menus/lists_menu.py:manage_reading_list()`)
  - Track reading progress (`app/models/reading_history.py`)
  - Organize by categories (`app/models/reading_list.py`)
  - Set reading goals (`app/services/goals_service.py`)

- **History Tracking** (`app/menus/lists_menu.py`)
  - Watch history (`app/models/watch_history.py`)
  - Reading history (`app/models/reading_history.py`)
  - History filtering (`app/services/history_service.py`)
  - Data export (`app/services/export_service.py`)

### Review System
- **Movie Reviews** (`app/menus/review_menu.py`)
  - Rating system (`app/models/review.py:MovieReview`)
  - Review management (`app/menus/review_menu.py:manage_movie_review()`)
  - Edit functionality (`app/menus/review_menu.py:edit_review()`)
  - History viewing (`app/services/review_history_service.py`)

- **Book Reviews** (`app/menus/review_menu.py`)
  - Book rating (`app/models/review.py:BookReview`)
  - Adaptation comparison (`app/services/comparison_service.py`)
  - Experience sharing (`app/menus/review_menu.py:share_review()`)
  - Quote tracking (`app/models/book_quotes.py`)

### User Experience
- **Personalization** (`app/menus/user_menu.py`)
  - Profile management (`app/models/user_profile.py`)
  - Preferences (`app/services/preferences_service.py`)
  - Genre preferences (`app/models/user_preferences.py`)
  - Notifications (`app/services/notification_service.py`)

- **Analytics** (`app/services/analytics_service.py`)
  - Viewing analysis (`app/services/analytics/viewing_analysis.py`)
  - Reading stats (`app/services/analytics/reading_analysis.py`)
  - Genre analytics (`app/services/analytics/genre_analysis.py`)
  - Time tracking (`app/services/analytics/time_tracking.py`)

### Security
- **Account Protection** (`app/services/auth_service.py`)
  - Password security (`app/services/security/password_service.py`)
  - Session handling (`app/services/security/session_service.py`)
  - Privacy settings (`app/services/security/privacy_service.py`)
  - Data protection (`app/services/security/encryption_service.py`)

### Technical Features
- **Performance** (`app/services/performance_service.py`)
  - Query optimization (`app/services/db/query_optimizer.py`)
  - API management (`app/services/api_manager.py`)
  - Monitoring (`app/services/monitoring_service.py`)
  - Backup system (`app/services/backup_service.py`)

- **API Integration** (`app/services/api_service.py`)
  - TMDb integration (`app/services/tmdb_service.py`)
  - Google Books integration (`app/services/google_books_service.py`)
  - Data sync (`app/services/sync_service.py`)
  - Platform management (`app/services/platform_service.py`)

## Limitations

### Adaptation Discovery
- The system can only identify potential adaptations when the movie and book titles share similar names
- Adaptations where titles differ significantly (e.g., "Do Androids Dream of Electric Sheep?" → "Blade Runner") are outside the scope of this system
- Manual adaptation confirmation is required to ensure accuracy

#### Technical Reasoning
This limitation exists because:
1. Our system relies on string similarity algorithms to match book and movie titles across different APIs (TMDb and Google Books)
2. Creating a comprehensive database of all book-to-movie adaptations would require:
   - Extensive manual curation
   - Complex natural language processing to understand plot similarities
   - Access to detailed metadata beyond what public APIs provide
3. Maintaining such a database would be:
   - Resource-intensive
   - Prone to errors
   - Outside the scope of our current architecture
4. The current approach prioritizes accuracy over completeness - we'd rather miss some adaptations than make incorrect matches


## Getting Started

### Prerequisites
- Python 3.8+
- SQLite or MySQL database
- TMDb API key
- Google Books API key

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API keys in `.env`
4. Initialize database: `python init_db.py`
5. Run the database migrations: `python run.py`
6. Run the application: `python menu.py`

## Usage

### Main Menu
1. **Browse & Discover**
   - Search for books and movies
   - Filter content
   - Find adaptations

2. **Your Collections**
   - Manage watchlist
   - Manage reading list
   - View history
   - Write reviews

3. **Account Management**
   - Register/Login
   - Update preferences
   - View personal history

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
