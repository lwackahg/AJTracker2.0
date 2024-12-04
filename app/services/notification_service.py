"""
Notification Service: Implements the Observer pattern for user notifications
"""
from typing import Dict, Any, List
from ..models import User, Movie, Watchlist
from datetime import datetime

class NotificationService:
    """
    Singleton pattern implementation for notification service
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance.notifications = {}
        return cls._instance

    def notify_watchlist_updates(self, movie: Movie) -> None:
        """Notify users when a movie in their watchlist has updates"""
        watchers = Watchlist.query.filter_by(movieID=movie.movieID).all()
        
        for watchlist_entry in watchers:
            user = User.query.get(watchlist_entry.userID)
            if user:
                self._create_notification(
                    user,
                    f"Update for '{movie.title}'",
                    f"There are new details available for {movie.title}"
                )

    def notify_new_adaptation(self, book_title: str, movie: Movie) -> None:
        """Notify relevant users about new adaptations"""
        # This could be enhanced with user preferences
        users = User.query.all()
        
        for user in users:
            if self._should_notify_user(user, movie):
                self._create_notification(
                    user,
                    "New Adaptation Alert",
                    f"'{book_title}' has been adapted into '{movie.title}'"
                )

    def _should_notify_user(self, user: User, movie: Movie) -> bool:
        """Check if user should be notified based on preferences"""
        if not user.preferences:
            return False
            
        # Check genre preferences
        user_genres = user.preferences.get('preferred_genres', [])
        if movie.genres:
            return any(genre in user_genres for genre in movie.genres)
            
        return False

    def _create_notification(self, user: User, title: str, message: str) -> None:
        """Create a new notification for a user"""
        if user.userID not in self.notifications:
            self.notifications[user.userID] = []
            
        self.notifications[user.userID].append({
            'title': title,
            'message': message,
            'timestamp': datetime.utcnow(),
            'read': False
        })

    def get_user_notifications(self, user: User) -> List[Dict[str, Any]]:
        """Get all notifications for a user"""
        return self.notifications.get(user.userID, [])
