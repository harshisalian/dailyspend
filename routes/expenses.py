"""
Expense management routes for Daily Spend.

This blueprint handles all expense-related operations:
- Create new expenses
- View all expenses with filtering
- Edit expenses
- Delete expenses
- View expense statistics

Production-ready practices demonstrated:
- Blueprint for modular routes
- Login required on all routes
- User authorization (can only access own expenses)
- Form validation
- Error handling with user feedback
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.expenses import (
    create_expense,
    get_expense_by_id,
    get_user_expenses,
    update_expense,
    delete_expense,
    get_expense_stats,
    get_categories
)
from routes.auth import login_required
from datetime import datetime, date

# Create blueprint
expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')


def get_current_user_id():
    """Get the current logged-in user's ID."""
    return session.get('user_id')


def validate_date(date_string: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_amount(amount_string: str) -> bool:
    """Validate amount is a valid decimal."""
    try:
        amount = float(amount_string)
        return amount > 0
    except ValueError:
        return False


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    """
    Add new expense route.
    
    GET: Display add expense form
    POST: Process form and create expense
    """
    user_id = get_current_user_id()
    categories = get_categories()
    
    if request.method == 'GET':
        # Display form with today's date pre-filled
        return render_template(
            'add_expense.html',
            categories=categories,
            today=date.today().strftime('%Y-%m-%d')
        )
    
    # POST request - process form
    title = request.form.get('title', '').strip()
    amount = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    expense_date = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validation: Check all required fields
    if not all([title, amount, category, expense_date]):
        flash('All fields marked * are required', 'error')
        return render_template(
            'add_expense.html',
            categories=categories,
            title=title,
            amount=amount,
            category=category,
            expense_date=expense_date,
            description=description
        )
    
    # Validation: Title length
    if len(title) < 3:
        flash('Title must be at least 3 characters', 'error')
        return render_template('add_expense.html', categories=categories)
    
    if len(title) > 100:
        flash('Title must be less than 100 characters', 'error')
        return render_template('add_expense.html', categories=categories)
    
    # Validation: Amount is valid decimal
    if not validate_amount(amount):
        flash('Amount must be a positive number', 'error')
        return render_template('add_expense.html', categories=categories)
    
    # Validation: Category is valid
    if category not in categories:
        flash('Invalid category selected', 'error')
        return render_template('add_expense.html', categories=categories)
    
    # Validation: Date format and not in future
    if not validate_date(expense_date):
        flash('Invalid date format (use YYYY-MM-DD)', 'error')
        return render_template('add_expense.html', categories=categories)
    
    expense_date_obj = datetime.strptime(expense_date, '%Y-%m-%d').date()
    if expense_date_obj > date.today():
        flash('Expense date cannot be in the future', 'error')
        return render_template('add_expense.html', categories=categories)
    
    # Validation: Description length
    if len(description) > 500:
        flash('Description must be less than 500 characters', 'error')
        return render_template('add_expense.html', categories=categories)
    
    # All validations passed - create expense
    if create_expense(
        user_id=user_id,
        title=title,
        amount=float(amount),
        category=category,
        expense_date=expense_date,
        description=description if description else None
    ):
        flash(f'Expense "{title}" added successfully!', 'success')
        return redirect(url_for('expenses.view_expenses'))
    else:
        flash('Error creating expense. Please try again.', 'error')
        return render_template('add_expense.html', categories=categories)


@expenses_bp.route('/view', methods=['GET'])
@login_required
def view_expenses():
    """
    View all expenses with filtering and pagination.
    
    Query parameters:
    - category: Filter by category
    - start_date: Filter by start date (YYYY-MM-DD)
    - end_date: Filter by end date (YYYY-MM-DD)
    - page: Page number (default 1)
    """
    user_id = get_current_user_id()
    categories = get_categories()
    
    # Get filters from query parameters
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)
    
    # Validate filters
    if start_date and not validate_date(start_date):
        flash('Invalid start date format', 'error')
        start_date = ''
    
    if end_date and not validate_date(end_date):
        flash('Invalid end date format', 'error')
        end_date = ''
    
    # Pagination
    items_per_page = 10
    offset = (page - 1) * items_per_page
    
    # Fetch expenses with filters
    expenses = get_user_expenses(
        user_id=user_id,
        category=category if category else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        limit=items_per_page + 1,  # Fetch one extra to check if more pages exist
        offset=offset
    )
    
    # Check if there are more pages
    has_next_page = len(expenses) > items_per_page
    if has_next_page:
        expenses = expenses[:items_per_page]  # Remove the extra item
    
    # Get statistics for current filters
    month_param = None
    if start_date and start_date[:7]:
        month_param = start_date[:7]  # Extract YYYY-MM
    
    stats = get_expense_stats(user_id=user_id, month=month_param)
    
    # Format amounts for display
    for expense in expenses:
        expense['amount_formatted'] = f"${expense['amount']:.2f}"
    
    return render_template(
        'view_expenses.html',
        expenses=expenses,
        categories=categories,
        selected_category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        has_next_page=has_next_page,
        stats=stats
    )


@expenses_bp.route('/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    """
    Edit an existing expense.
    
    GET: Display edit form
    POST: Process form and update expense
    """
    user_id = get_current_user_id()
    categories = get_categories()
    
    # Fetch the expense (ensures user owns it)
    expense = get_expense_by_id(expense_id, user_id)
    
    if not expense:
        flash('Expense not found', 'error')
        return redirect(url_for('expenses.view_expenses'))
    
    if request.method == 'GET':
        return render_template(
            'edit_expense.html',
            expense=expense,
            categories=categories
        )
    
    # POST request - process form
    title = request.form.get('title', '').strip()
    amount = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    expense_date = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validation
    if not all([title, amount, category, expense_date]):
        flash('All fields marked * are required', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    if len(title) < 3 or len(title) > 100:
        flash('Title must be between 3 and 100 characters', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    if not validate_amount(amount):
        flash('Amount must be a positive number', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    if category not in categories:
        flash('Invalid category selected', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    if not validate_date(expense_date):
        flash('Invalid date format (use YYYY-MM-DD)', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    expense_date_obj = datetime.strptime(expense_date, '%Y-%m-%d').date()
    if expense_date_obj > date.today():
        flash('Expense date cannot be in the future', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)
    
    # Update expense
    if update_expense(
        expense_id=expense_id,
        user_id=user_id,
        title=title,
        amount=float(amount),
        category=category,
        expense_date=expense_date,
        description=description if description else None
    ):
        flash(f'Expense "{title}" updated successfully!', 'success')
        return redirect(url_for('expenses.view_expenses'))
    else:
        flash('Error updating expense. Please try again.', 'error')
        return render_template('edit_expense.html', expense=expense, categories=categories)


@expenses_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense_route(expense_id):
    """
    Delete an expense (POST only for safety).
    
    Returns JSON response for AJAX handling.
    """
    user_id = get_current_user_id()
    
    # Fetch expense to get title (for flash message)
    expense = get_expense_by_id(expense_id, user_id)
    
    if not expense:
        return jsonify({'success': False, 'error': 'Expense not found'}), 404
    
    # Delete expense
    if delete_expense(expense_id, user_id):
        return jsonify({
            'success': True,
            'message': f'Expense "{expense["title"]}" deleted successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Error deleting expense'
        }), 500


@expenses_bp.route('/stats')
@login_required
def get_stats():
    """
    Get expense statistics for current month (JSON API).
    
    Used by dashboard for statistics display.
    """
    user_id = get_current_user_id()
    month = request.args.get('month', None)
    
    stats = get_expense_stats(user_id=user_id, month=month)
    
    return jsonify(stats)
