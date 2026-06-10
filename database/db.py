"""
Database connection and interaction module for Daily Spend.

This module handles all communication with MySQL database including:
- Creating and managing database connections
- Executing queries safely (preventing SQL injection)
- Converting query results to Python objects
- Connection pooling and error handling

Production-ready practices demonstrated:
- Parameterized queries (prevents SQL injection attacks)
- Connection pooling for performance
- Proper error handling and logging
- Context managers for resource cleanup
- Type hints for clarity
"""

import mysql.connector
from mysql.connector import Error, pooling
from flask import current_app
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple


# Database connection pool
# Pooling reuses connections instead of creating new ones, improving performance
_db_pool = None


def init_db_pool(app=None):
    """
    Initialize the MySQL connection pool.
    
    A connection pool maintains multiple ready-to-use connections.
    This is much faster than creating a new connection for each query.
    
    Args:
        app (Flask): Flask application instance (optional).
    """
    global _db_pool
    
    # Get configuration from Flask app
    if app:
        config = {
            'host': app.config['MYSQL_HOST'],
            'user': app.config['MYSQL_USER'],
            'password': app.config['MYSQL_PASSWORD'],
            'database': app.config['MYSQL_DB'],
            'pool_name': 'dailyspend_pool',
            'pool_size': 5,  # Keep 5 connections ready
            'pool_reset_session': True
        }
    else:
        # Fallback to current_app if no app provided
        config = {
            'host': current_app.config['MYSQL_HOST'],
            'user': current_app.config['MYSQL_USER'],
            'password': current_app.config['MYSQL_PASSWORD'],
            'database': current_app.config['MYSQL_DB'],
            'pool_name': 'dailyspend_pool',
            'pool_size': 5,
            'pool_reset_session': True
        }
    
    try:
        _db_pool = pooling.MySQLConnectionPool(**config)
        print("✓ Database connection pool initialized successfully")
    except Error as e:
        print(f"✗ Error initializing connection pool: {e}")
        raise


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    Using 'with' statement ensures connections are properly returned to pool.
    Even if an error occurs, the connection is released (unlike manual try-catch).
    
    Yields:
        mysql.connector.MySQLConnection: Active database connection.
    
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    conn = None
    try:
        if _db_pool is None:
            init_db_pool()
        
        conn = _db_pool.get_connection()
        yield conn
        
    except Error as e:
        print(f"Database connection error: {e}")
        if conn:
            conn.rollback()  # Undo any uncommitted changes
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()  # Return connection to pool


def execute_query(query: str, params: Optional[Tuple] = None) -> int:
    """
    Execute INSERT, UPDATE, or DELETE queries.
    
    Args:
        query (str): SQL query with %s placeholders (parameterized)
        params (tuple, optional): Parameters to safely substitute into query
    
    Returns:
        int: Number of rows affected
    
    Raises:
        Exception: If database operation fails
    
    Example:
        execute_query(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            ('john_doe', 'john@example.com')
        )
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Use parameterized query (params are substituted safely by library)
            # This prevents SQL injection attacks
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Commit changes to database
            conn.commit()
            
            # Return number of rows affected
            return cursor.rowcount
            
    except Error as e:
        print(f"Error executing query: {e}")
        raise


def fetch_one(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch a single row from database.
    
    Args:
        query (str): SQL SELECT query with %s placeholders
        params (tuple, optional): Parameters to safely substitute
    
    Returns:
        dict: First matching row as dictionary (keys are column names)
        None: If no rows match
    
    Example:
        user = fetch_one("SELECT * FROM users WHERE id = %s", (1,))
        if user:
            print(user['username'])
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)  # Results as dicts, not tuples
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchone()  # Get first row or None
            
    except Error as e:
        print(f"Error fetching data: {e}")
        raise


def fetch_all(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Fetch multiple rows from database.
    
    Args:
        query (str): SQL SELECT query with %s placeholders
        params (tuple, optional): Parameters to safely substitute
    
    Returns:
        list: All matching rows as list of dictionaries
        list: Empty list if no rows match
    
    Example:
        expenses = fetch_all("SELECT * FROM expenses WHERE user_id = %s", (1,))
        for expense in expenses:
            print(f"{expense['title']}: ${expense['amount']}")
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()  # Get all rows
            
    except Error as e:
        print(f"Error fetching data: {e}")
        raise


def execute_many(query: str, data: List[Tuple]) -> int:
    """
    Execute multiple INSERT/UPDATE/DELETE operations at once.
    
    More efficient than calling execute_query multiple times.
    Useful for bulk operations.
    
    Args:
        query (str): SQL query with %s placeholders
        data (list): List of tuples, each tuple is one set of parameters
    
    Returns:
        int: Total rows affected
    
    Example:
        expenses_data = [
            (1, 'Coffee', 5.50, 'Food', '2026-06-10'),
            (1, 'Gas', 45.00, 'Transport', '2026-06-10'),
            (1, 'Movie', 28.00, 'Entertainment', '2026-06-09'),
        ]
        execute_many(
            "INSERT INTO expenses (user_id, title, amount, category, date) 
             VALUES (%s, %s, %s, %s, %s)",
            expenses_data
        )
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # executemany runs the same query multiple times with different params
            cursor.executemany(query, data)
            conn.commit()
            
            return cursor.rowcount
            
    except Error as e:
        print(f"Error executing bulk query: {e}")
        raise


def test_connection() -> bool:
    """
    Test if database connection is working.
    
    Useful for startup checks and debugging.
    
    Returns:
        bool: True if connection successful, False otherwise
    
    Example:
        if test_connection():
            print("Database is online")
        else:
            print("Database connection failed")
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
    except Error:
        return False
