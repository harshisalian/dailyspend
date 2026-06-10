"""
Main application routes (non-authentication).

This module handles:
- Home/index page
- Dashboard (protected - requires login)

Production-ready practices demonstrated:
- Blueprint for organizing routes
- Login required decorator on protected routes
- Template rendering
"""

from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required

# Create blueprint for main routes
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
    Home page route.
    
    Displays landing page if not logged in.
    Redirects to dashboard if logged in.
    """
    if session.get('user_id'):
        return redirect(url_for('main.dashboard'))
    
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard route (requires login).
    
    Shows user's expense summary and quick actions.
    """
    return render_template('dashboard.html')
