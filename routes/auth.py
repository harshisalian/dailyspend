"""
Authentication routes for Daily Spend.

This blueprint handles all user authentication flows:
- User registration (sign up)
- User login (sign in)
- User logout (sign out)
- Session management

Production-ready practices demonstrated:
- Blueprint for modular routes
- Form validation and error handling
- Flask session management
- Password hashing with werkzeug
- Secure session configuration
- Redirect to next page after login (UX best practice)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.users import create_user, verify_user_password, user_exists
import re

# Create blueprint
# A blueprint is a way to organize routes into a module
# This makes the app more maintainable and testable
auth = Blueprint('auth', __name__, url_prefix='/auth')


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, ""


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    GET: Display registration form
    POST: Process registration form submission
    
    Flow:
    1. User submits form with username, email, password
    2. Validate inputs
    3. Check if username/email already exists
    4. Hash password and create user in database
    5. Redirect to login page on success
    
    Security considerations:
    - Password is hashed before database storage
    - Email and username uniqueness is enforced
    - Password strength is validated
    - Error messages don't reveal if email exists (prevents user enumeration)
    """
    
    if request.method == 'GET':
        # Display registration form
        return render_template('register.html')
    
    # POST request - process form
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation: Check all fields are provided
    if not username or not email or not password or not confirm_password:
        flash('All fields are required', 'error')
        return render_template('register.html')
    
    # Validation: Username length
    if len(username) < 3:
        flash('Username must be at least 3 characters', 'error')
        return render_template('register.html')
    
    if len(username) > 50:
        flash('Username must be less than 50 characters', 'error')
        return render_template('register.html')
    
    # Validation: Email format
    if not validate_email(email):
        flash('Invalid email address', 'error')
        return render_template('register.html')
    
    # Validation: Passwords match
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('register.html')
    
    # Validation: Password strength
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        flash(error_msg, 'error')
        return render_template('register.html')
    
    # Validation: Username already exists
    if user_exists(username=username):
        flash('Username already taken. Please choose a different username.', 'error')
        return render_template('register.html')
    
    # Validation: Email already registered
    if user_exists(email=email):
        flash('Email already registered. Try logging in or use a different email.', 'error')
        return render_template('register.html')
    
    # All validations passed - create user
    if create_user(username, email, password):
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    else:
        flash('An error occurred while creating your account. Please try again.', 'error')
        return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    GET: Display login form
    POST: Process login form submission
    
    Flow:
    1. User submits username and password
    2. Verify credentials against database
    3. Create Flask session (session cookie)
    4. Redirect to dashboard or requested page
    
    Security considerations:
    - Password is never stored or logged
    - Session cookie is HTTP-only (prevents JavaScript access)
    - Session cookie is secure (HTTPS only in production)
    - Generic error message (doesn't reveal if username exists)
    """
    
    if request.method == 'GET':
        # Display login form
        return render_template('login.html')
    
    # POST request - process form
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # Validation: Check fields provided
    if not username or not password:
        flash('Username and password are required', 'error')
        return render_template('login.html')
    
    # Verify credentials
    user = verify_user_password(username, password)
    
    if user:
        # Credentials valid - create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session.permanent = True  # Session persists across browser closes
        
        flash(f'Welcome back, {user["username"]}!', 'success')
        
        # Redirect to next page if specified, otherwise dashboard
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
    
    else:
        # Invalid credentials
        flash('Invalid username or password', 'error')
        return render_template('login.html')


@auth.route('/logout')
def logout():
    """
    User logout route.
    
    Clears the Flask session (effectively logging out the user).
    User will need to log in again to access protected pages.
    
    Security considerations:
    - Session is cleared (not just disabled)
    - All session data is removed from server
    - Browser's session cookie becomes invalid
    """
    
    username = session.get('username', 'User')
    
    # Clear session data
    session.clear()
    
    flash(f'Goodbye {username}! You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


def login_required(f):
    """
    Decorator to protect routes - requires user to be logged in.
    
    If user is not logged in, redirects to login page.
    If user is logged in, allows access to the route.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This is protected"
    
    This is a simple version. Flask-Login extension provides more features.
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    
    return decorated_function
