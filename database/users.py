"""
User database operations module.

This module handles all database interactions related to users:
- Creating new user accounts
- Fetching user by username/email
- Checking password correctness
- Updating user information

Production-ready practices demonstrated:
- Parameterized queries (prevents SQL injection)
- Clear error handling
- Function docstrings with examples
- Type hints for clarity
"""

from database.db import execute_query, fetch_one
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Any


def create_user(username: str, email: str, password: str) -> bool:
    """
    Create a new user account in the database.
    
    The password is hashed using werkzeug.security.generate_password_hash
    which uses the PBKDF2 algorithm with SHA256 by default.
    
    Args:
        username (str): Unique username for login
        email (str): Unique email address
        password (str): Plain-text password (will be hashed before storage)
    
    Returns:
        bool: True if user created successfully, False otherwise
    
    Raises:
        Exception: If database error occurs (e.g., username already exists)
    
    Example:
        if create_user('john_doe', 'john@example.com', 'SecurePass123'):
            print("User created successfully")
        else:
            print("Failed to create user")
    """
    try:
        # Hash the password before storing
        # IMPORTANT: Never store plain passwords!
        password_hash = generate_password_hash(password)
        
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        
        # Execute query with parameterized values (safe from SQL injection)
        result = execute_query(query, (username, email, password_hash))
        
        # execute_query returns rowcount (1 if successful, 0 if failed)
        return result > 0
        
    except Exception as e:
        # In production, log this error to a logging service
        print(f"Error creating user: {e}")
        return False


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a user from database by username.
    
    Args:
        username (str): Username to search for
    
    Returns:
        dict: User data if found (includes id, username, email, password_hash, created_at)
        None: If user not found
    
    Example:
        user = get_user_by_username('john_doe')
        if user:
            print(f"Found user: {user['email']}")
        else:
            print("User not found")
    """
    query = "SELECT * FROM users WHERE username = %s"
    return fetch_one(query, (username,))


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a user from database by email.
    
    Args:
        email (str): Email address to search for
    
    Returns:
        dict: User data if found
        None: If user not found
    
    Example:
        user = get_user_by_email('john@example.com')
    """
    query = "SELECT * FROM users WHERE email = %s"
    return fetch_one(query, (email,))


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a user from database by ID.
    
    Args:
        user_id (int): User's unique ID
    
    Returns:
        dict: User data if found
        None: If user not found
    
    Example:
        user = get_user_by_id(1)
    """
    query = "SELECT * FROM users WHERE id = %s"
    return fetch_one(query, (user_id,))


def verify_user_password(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials (login authentication).
    
    This is the main function used during login:
    1. Find user by username
    2. Check if password matches the stored hash
    3. Return user data if valid, None if invalid
    
    Uses werkzeug.security.check_password_hash which safely compares passwords.
    It's resistant to timing attacks (doesn't leak info through comparison speed).
    
    Args:
        username (str): Username
        password (str): Plain-text password (from login form)
    
    Returns:
        dict: User data if credentials valid
        None: If username doesn't exist or password is incorrect
    
    Example:
        user = verify_user_password('john_doe', 'MyPassword123')
        if user:
            print(f"Login successful for user ID: {user['id']}")
            # Start session here
        else:
            print("Invalid username or password")
    """
    # Find user by username
    user = get_user_by_username(username)
    
    if not user:
        # User doesn't exist
        return None
    
    # Check if provided password matches the stored hash
    if check_password_hash(user['password_hash'], password):
        # Password correct - return user data (but exclude password_hash for security)
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
        return user_data
    
    # Password incorrect
    return None


def user_exists(username: str = None, email: str = None) -> bool:
    """
    Check if a user exists by username or email.
    
    Args:
        username (str, optional): Username to check
        email (str, optional): Email to check
    
    Returns:
        bool: True if user exists, False otherwise
    
    Example:
        if user_exists(username='john_doe'):
            print("Username already taken")
        
        if user_exists(email='john@example.com'):
            print("Email already registered")
    """
    if username:
        return get_user_by_username(username) is not None
    
    if email:
        return get_user_by_email(email) is not None
    
    return False
