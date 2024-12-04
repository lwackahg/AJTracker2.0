# Development Viewpoint: Authentication Module
# This module handles all user authentication functionality
# Logical Viewpoint: User Management Component
# Manages user accounts and authentication state
# Process Viewpoint: Authentication Workflow
# Implements the flow of user registration and login
# Physical Viewpoint: Security Layer
# Implements password hashing and secure data storage
# Scenario Viewpoint: User Access Control
# Supports user scenarios for account creation and access

from app import db
from app.models import User
from .utils import clear_screen
import os
import json
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

# Process Viewpoint: User Registration
# Implements the workflow for new user registration
def register_user():
    # Process Viewpoint: Registration Workflow
    # Manages new user registration with data validation
    """Register a new user."""
    print("\n=== Register New User ===")
    username = input("Enter username: ")
    
    if User.query.filter_by(Username=username).first():
        print("Username already exists!")
        return None
    
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        return None
    
    user = User(
        Username=username,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    
    print("Registration successful!")
    return user

# Process Viewpoint: User Authentication
# Implements the workflow for user login
def login_user():
    # Process Viewpoint: Login Workflow
    # Implements secure user login with validation
    """Login an existing user."""
    print("\n=== User Login ===")
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    user = User.query.filter_by(Username=username).first()
    if user and check_password_hash(user.password_hash, password):
        print("Login successful!")
        return user
    else:
        print("Invalid username or password!")
        return None
