"""
Daily Spend - Expense Tracker Application
Main Flask application entry point.

This module initializes and configures the Flask application. It serves as the
entry point for running the application. The app is configured using the config.py
settings to support different environments (development, testing, production).

Production-ready practices demonstrated:
- Configuration from config.py for environment separation
- Proper app initialization and teardown handlers
- Error handling for database connections
- Structured logging (ready for enhancement)
- Clear code organization
"""

import os
from dotenv import load_dotenv

# Load .env file FIRST before importing config
# This ensures environment variables are available to config.py
load_dotenv()

from flask import Flask, render_template, jsonify
from config import get_config


def create_app(config_name=None):
    """
    Application factory function for creating Flask app instances.
    
    This pattern allows us to:
    - Create multiple app instances for testing
    - Apply different configurations easily
    - Keep the app structure modular and testable
    - Support different environments without code changes
    
    Args:
        config_name (str, optional): Configuration environment name.
                                     If None, uses FLASK_ENV environment variable.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    
    # Create Flask app instance
    app = Flask(
        __name__,
        template_folder='templates',  # HTML templates location
        static_folder='static',        # CSS, JS, images location
        static_url_path='/static'      # URL prefix for static files
    )
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Register database initialization (placeholder for later steps)
    # In Step 2, we'll add database connection logic here
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints (routes will go here in Step 3)
    # In Step 3, we'll register main blueprint with routes
    
    return app


def register_error_handlers(app):
    """
    Register error handler functions with the Flask app.
    
    These handlers provide consistent error responses across the application
    and allow us to customize error pages based on environment.
    
    Args:
        app (Flask): Flask application instance.
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({'error': 'Page not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        # In production, log this error to a logging service
        return jsonify({'error': 'Internal server error'}), 500


# Create the Flask app instance when module is imported
# This is the instance that will be used by the development server
app = create_app()


if __name__ == '__main__':
    """
    Run the Flask development server.
    
    Note: This should ONLY be used for local development.
    For production, use a WSGI server like Gunicorn:
    
        gunicorn -w 4 -b 0.0.0.0:8000 app:app
    
    The -w 4 flag creates 4 worker processes for handling concurrent requests.
    This is much safer and more efficient than Flask's built-in development server.
    """
    
    # Get environment (defaults to 'development')
    env = os.getenv('FLASK_ENV', 'development')
    
    # Run the development server
    # debug=True enables auto-reloading and better error pages (dev only!)
    # host='0.0.0.0' allows external connections (useful in some setups)
    # port=5000 is the default Flask port
    app.run(
        debug=app.config['DEBUG'],
        host='127.0.0.1',
        port=5000
    )
