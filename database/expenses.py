"""
Expense database operations module.

This module handles all database interactions related to expenses:
- Creating new expenses
- Fetching expenses (all, by user, with filtering)
- Updating expenses
- Deleting expenses
- Getting expense statistics (totals, by category)

Production-ready practices demonstrated:
- Parameterized queries (SQL injection safe)
- Date/time handling
- Aggregate queries (SUM, GROUP BY for statistics)
- Proper error handling
- Type hints for clarity
"""

from database.db import execute_query, fetch_one, fetch_all
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


def create_expense(
    user_id: int,
    title: str,
    amount: float,
    category: str,
    expense_date: str,
    description: str = None
) -> bool:
    """
    Create a new expense entry.
    
    Args:
        user_id (int): ID of the user creating the expense
        title (str): Expense title/name
        amount (float): Amount spent (e.g., 12.50)
        category (str): Category (Food, Transport, Entertainment, etc.)
        expense_date (str): Date of expense (YYYY-MM-DD format)
        description (str, optional): Additional details
    
    Returns:
        bool: True if created successfully, False otherwise
    
    Example:
        create_expense(
            user_id=1,
            title='Lunch at Chipotle',
            amount=12.50,
            category='Food',
            expense_date='2026-06-10',
            description='With coworkers'
        )
    """
    try:
        query = """
            INSERT INTO expenses (user_id, title, amount, category, date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        result = execute_query(
            query,
            (user_id, title, amount, category, expense_date, description)
        )
        
        return result > 0
        
    except Exception as e:
        print(f"Error creating expense: {e}")
        return False


def get_expense_by_id(expense_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single expense by ID (only for the specified user).
    
    Security: Ensures user can only access their own expenses.
    
    Args:
        expense_id (int): Expense ID to fetch
        user_id (int): User ID (for authorization)
    
    Returns:
        dict: Expense data if found and belongs to user
        None: If not found or doesn't belong to user
    
    Example:
        expense = get_expense_by_id(expense_id=5, user_id=1)
    """
    query = """
        SELECT * FROM expenses 
        WHERE id = %s AND user_id = %s
    """
    
    return fetch_one(query, (expense_id, user_id))


def get_user_expenses(
    user_id: int,
    category: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Fetch all expenses for a user with optional filtering.
    
    Args:
        user_id (int): User ID
        category (str, optional): Filter by category
        start_date (str, optional): Filter by start date (YYYY-MM-DD)
        end_date (str, optional): Filter by end date (YYYY-MM-DD)
        limit (int): Max results to return (default 100)
        offset (int): Pagination offset (default 0)
    
    Returns:
        list: List of expenses matching criteria
    
    Example:
        # Get all Food expenses in June
        expenses = get_user_expenses(
            user_id=1,
            category='Food',
            start_date='2026-06-01',
            end_date='2026-06-30'
        )
    """
    query = "SELECT * FROM expenses WHERE user_id = %s"
    params = [user_id]
    
    # Add optional filters
    if category:
        query += " AND category = %s"
        params.append(category)
    
    if start_date:
        query += " AND date >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= %s"
        params.append(end_date)
    
    # Order by date (newest first)
    query += " ORDER BY date DESC, created_at DESC"
    
    # Add pagination
    query += " LIMIT %s OFFSET %s"
    params.append(limit)
    params.append(offset)
    
    return fetch_all(query, tuple(params))


def update_expense(
    expense_id: int,
    user_id: int,
    title: str = None,
    amount: float = None,
    category: str = None,
    expense_date: str = None,
    description: str = None
) -> bool:
    """
    Update an expense (only if user owns it).
    
    Security: Ensures user can only update their own expenses.
    
    Args:
        expense_id (int): Expense ID to update
        user_id (int): User ID (for authorization)
        title (str, optional): New title
        amount (float, optional): New amount
        category (str, optional): New category
        expense_date (str, optional): New date
        description (str, optional): New description
    
    Returns:
        bool: True if updated successfully, False otherwise
    
    Example:
        update_expense(
            expense_id=5,
            user_id=1,
            amount=15.00,
            category='Groceries'
        )
    """
    try:
        # Build dynamic query (only update provided fields)
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        
        if amount is not None:
            updates.append("amount = %s")
            params.append(amount)
        
        if category is not None:
            updates.append("category = %s")
            params.append(category)
        
        if expense_date is not None:
            updates.append("date = %s")
            params.append(expense_date)
        
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            # Nothing to update
            return False
        
        query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
        params.append(expense_id)
        params.append(user_id)
        
        result = execute_query(query, tuple(params))
        return result > 0
        
    except Exception as e:
        print(f"Error updating expense: {e}")
        return False


def delete_expense(expense_id: int, user_id: int) -> bool:
    """
    Delete an expense (only if user owns it).
    
    Security: Ensures user can only delete their own expenses.
    
    Args:
        expense_id (int): Expense ID to delete
        user_id (int): User ID (for authorization)
    
    Returns:
        bool: True if deleted successfully, False otherwise
    
    Example:
        delete_expense(expense_id=5, user_id=1)
    """
    try:
        query = "DELETE FROM expenses WHERE id = %s AND user_id = %s"
        result = execute_query(query, (expense_id, user_id))
        return result > 0
        
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return False


def get_expense_stats(user_id: int, month: str = None) -> Dict[str, Any]:
    """
    Get expense statistics for a user.
    
    Args:
        user_id (int): User ID
        month (str, optional): Filter by month (YYYY-MM, e.g., '2026-06')
    
    Returns:
        dict: Statistics including:
            - total_spent: Total amount spent
            - expense_count: Number of expenses
            - by_category: Breakdown by category
            - avg_per_expense: Average expense amount
    
    Example:
        stats = get_expense_stats(user_id=1, month='2026-06')
        print(f"Total: ${stats['total_spent']}")
    """
    try:
        stats = {
            'total_spent': 0.0,
            'expense_count': 0,
            'by_category': {},
            'avg_per_expense': 0.0
        }
        
        # Base query
        base_query = "SELECT * FROM expenses WHERE user_id = %s"
        params = [user_id]
        
        if month:
            base_query += " AND DATE_FORMAT(date, '%Y-%m') = %s"
            params.append(month)
        
        expenses = fetch_all(base_query, tuple(params))
        
        if not expenses:
            return stats
        
        stats['expense_count'] = len(expenses)
        
        # Calculate totals and by category
        total = Decimal('0.00')
        category_totals = {}
        
        for expense in expenses:
            amount = Decimal(str(expense['amount']))
            total += amount
            
            category = expense['category']
            if category not in category_totals:
                category_totals[category] = Decimal('0.00')
            category_totals[category] += amount
        
        stats['total_spent'] = float(total)
        stats['by_category'] = {
            cat: float(amount) for cat, amount in category_totals.items()
        }
        
        if stats['expense_count'] > 0:
            stats['avg_per_expense'] = stats['total_spent'] / stats['expense_count']
        
        return stats
        
    except Exception as e:
        print(f"Error getting expense stats: {e}")
        return {
            'total_spent': 0.0,
            'expense_count': 0,
            'by_category': {},
            'avg_per_expense': 0.0
        }


def get_categories() -> List[str]:
    """
    Get all available expense categories.
    
    Returns:
        list: List of category names
    
    Example:
        categories = get_categories()
        # Returns: ['Food', 'Transport', 'Entertainment', 'Health', 'Utilities', 'Shopping', 'Other']
    """
    return [
        'Food',
        'Transport',
        'Entertainment',
        'Health',
        'Utilities',
        'Shopping',
        'Other'
    ]
