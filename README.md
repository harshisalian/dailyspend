# Daily Spend - Expense Tracker

A production-grade expense tracking web application built with Flask, MySQL, HTML, and CSS.

## Project Structure

```
dailyspend/
├── app.py                 # Flask application factory and entry point
├── config.py              # Configuration for different environments
├── requirements.txt       # Python package dependencies
├── .env.example           # Example environment variables (copy to .env)
├── README.md              # This file
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Home/dashboard page
│   ├── add_expense.html   # Add expense form
│   └── expenses.html      # View expenses list
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── script.js      # Client-side JavaScript
└── database/              # Database setup scripts (added in Step 2)
    └── schema.sql         # Database schema
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your MySQL credentials
# Update MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
```

### 3. Set up MySQL Database

```bash
# Create database and tables (instructions in Step 2)
mysql -u root -p < database/schema.sql
```

### 4. Run the Application

```bash
# Start Flask development server
python app.py

# Application will be available at http://localhost:5000
```

## Development

- **Debug Mode**: Enabled in development environment (auto-reload, detailed error pages)
- **Database**: MySQL 8.0+
- **Python**: 3.8+

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set `FLASK_ENV=production`
3. Ensure all environment variables are securely set
4. Enable HTTPS
5. Use a reverse proxy (Nginx, Apache)
6. Set up proper logging and monitoring

## Next Steps

See individual step documentation for setup and configuration details.
