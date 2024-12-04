# Development Viewpoint: Main Menu Module Structure
# This module serves as the entry point for the application's user interface
# Logical Viewpoint: Navigation Component
# Manages the high-level navigation and user session state
# Process Viewpoint: Application Flow
# Controls the main application workflow and user interactions
# Physical Viewpoint: System Integration
# Integrates with Flask application and database components
# Scenario Viewpoint: User Navigation
# Supports different user scenarios for authenticated and anonymous users

from app import create_app, db
from app.models import User
from . import browse_menu, lists_menu, auth_menu, review_menu
import os
from .utils import clear_screen
import json
from datetime import datetime
# Logical Viewpoint: Menu Display
# Handles the presentation of appropriate menu options based on user state
def print_menu(current_user=None):
    """Print the main menu options."""
    clear_screen()
    print("\n=== Film Adaptation Tracker ===")
    if current_user:
        print(f"\nWelcome, {current_user.Username}!")
    print("\n1. Browse Content")
    print("2. Search")
    print("3. My Lists")
    #print("4. Reviews")
    print("4. View your confirmed adaptations")
    if current_user:
        print("5. Logout")
    else:
        print("5. Login")
        print("6. Register")
    print("0. Exit")

# Process Viewpoint: Application Control
# Manages the main application loop and user session
def main():
    app = create_app()
    with app.app_context():
        current_user = None
        while True:
            print_menu(current_user)
            choice = input("\nEnter your choice: ")
            
            if choice == "1":
                browse_menu.browse_menu(current_user)
            elif choice == "2":
                browse_menu.search(current_user)
            elif choice == "3":
                if current_user:
                    lists_menu.my_lists_menu(current_user)
                else:
                    print("\nPlease login to access your lists")
                    input("\nPress Enter to continue...")

            elif choice == "4":
                browse_menu.view_saved_adaptations()
            elif choice == "5":
                if current_user:
                    current_user = None
                    print("\nLogged out successfully!")
                    input("\nPress Enter to continue...")
                else:
                    current_user = auth_menu.login_user()
            elif choice == "6" and not current_user:
                current_user = auth_menu.register_user()
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice")
                input("\nPress Enter to continue...")
