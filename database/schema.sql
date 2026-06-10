-- ========================================================================
-- Daily Spend - Expense Tracker Database Schema
-- ========================================================================
-- This SQL file creates the complete database structure for the Daily Spend
-- expense tracker application. It defines the users and expenses tables with
-- proper data types, constraints, and indexes for production use.
--
-- How to use this file:
--   mysql -u root -p < database/schema.sql
--   OR in MySQL CLI:
--   mysql> source database/schema.sql;
-- ========================================================================


-- ========================================================================
-- DATABASE CREATION
-- ========================================================================

-- Drop database if it exists (useful for fresh starts/testing)
DROP DATABASE IF EXISTS dailyspend;

-- Create the main database
-- UTF8MB4 charset: supports emojis, special characters, and full Unicode
CREATE DATABASE dailyspend
CHARACTER
SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Select the newly created database
USE dailyspend;


-- ========================================================================
-- USERS TABLE
-- ========================================================================
-- Stores user account information. Each row represents one user.
-- Password hashing is done in Python (never in database).
-- ========================================================================

CREATE TABLE users (
    -- Primary Key: Unique identifier for each user
    -- AUTO_INCREMENT: Automatically increments with each new record
    -- INT: Can handle up to ~2 billion users (more than enough)
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Username: User's login name
    -- VARCHAR(255): Can store up to 255 characters
    -- UNIQUE: No two users can have the same username
    -- NOT NULL: Username is required
    username VARCHAR
(255) NOT NULL UNIQUE,
    
    -- Email: User's email address
    -- VARCHAR(255): Email addresses rarely exceed 255 characters
    -- UNIQUE: One account per email (standard practice)
    -- NOT NULL: Email is required for communication/password recovery
    email VARCHAR
(255) NOT NULL UNIQUE,
    
    -- Password Hash: NEVER store plain passwords!
    -- We store the hash (one-way encryption) created by Python's bcrypt
    -- VARCHAR(255): bcrypt hashes are ~60 chars, but we have buffer
    -- NOT NULL: Required for authentication
    password_hash VARCHAR
(255) NOT NULL,
    
    -- Account Creation Timestamp
    -- TIMESTAMP: Automatically records date and time
    -- DEFAULT CURRENT_TIMESTAMP: Fills in current time if not specified
    -- UNIQUE constraint: Ensures email and username are unique
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance:
    -- Users will often be looked up by username or email, so we index these
    INDEX idx_username
(username),
    INDEX idx_email
(email)
) ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Stores user account information including credentials';


-- ========================================================================
-- EXPENSES TABLE
-- ========================================================================
-- Stores individual expense transactions. Each row is one expense entry.
-- Foreign key constraint links each expense to a specific user.
-- ========================================================================

CREATE TABLE expenses (
    -- Primary Key: Unique identifier for each expense
    -- AUTO_INCREMENT: Automatically increments with each new expense
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- User ID: Foreign Key linking to users table
    -- INT: Must match the type in users.id
    -- NOT NULL: Every expense must belong to a user
    -- FOREIGN KEY: Ensures referential integrity (can't have expenses for non-existent users)
    -- ON DELETE CASCADE: If user is deleted, their expenses are automatically deleted
    user_id INT NOT NULL,
    
    -- Expense Title/Name
    -- VARCHAR(255): Short descriptive name (e.g., "Lunch at McDonald's", "Gas fill-up")
    -- NOT NULL: Required field
    title VARCHAR
(255) NOT NULL,
    
    -- Amount: The money spent
    -- DECIMAL(10, 2): Perfect for money
    --   - First number (10): Total digits allowed
    --   - Second number (2): Decimal places (cents)
    --   - So max value is $99,999,999.99
    -- NOTE: We use DECIMAL, NOT FLOAT!
    --   Why? Float has rounding errors ($9.99 + $0.01 might = $10.0000001)
    --   DECIMAL is exact, which is critical for financial data
    -- NOT NULL: Required field
    amount DECIMAL
(10, 2) NOT NULL,
    
    -- Category: Type of expense
    -- VARCHAR(100): 100 characters enough for category names
    -- NOT NULL: Required for filtering/reporting
    -- Examples: Food, Transport, Entertainment, Health, Utilities, Shopping
    category VARCHAR
(100) NOT NULL,
    
    -- Expense Date: When the expense occurred
    -- DATE: Stores just the date (no time) since we typically care about daily expenses
    -- NOT NULL: Required for sorting and filtering
    date DATE NOT NULL,
    
    -- Description: Optional longer details about the expense
    -- TEXT: Allows up to 65,535 characters for detailed notes
    -- NULL allowed: This field is optional
    description TEXT,
    
    -- Record Creation Timestamp: When this expense was logged into the system
    -- TIMESTAMP: Date and time
    -- DEFAULT CURRENT_TIMESTAMP: Auto-fills with current time
    -- NOTE: Different from 'date' field
    --   'date' = when expense happened (can be any date)
    --   'created_at' = when user recorded it in the system (always now)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    -- Ensures user_id references an actual user in the users table
    -- ON DELETE CASCADE: If user is deleted, their expenses are deleted too
    -- ON UPDATE CASCADE: If user.id is updated, expenses.user_id updates too
    CONSTRAINT fk_expenses_user 
        FOREIGN KEY
(user_id) 
        REFERENCES users
(id) 
        ON
DELETE CASCADE 
        ON
UPDATE CASCADE,
    
    -- Indexes for performance:
    -- Queries often filter by user_id and date, so we index these
    INDEX idx_user_id (user_id),
    INDEX idx_date (date),
    -- Combined index for common query: "Get expenses for user X after date Y"
    INDEX idx_user_date (user_id, date)

) ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='Stores individual expense transactions linked to users';


-- ========================================================================
-- OPTIONAL: Sample Data for Testing
-- ========================================================================
-- Uncomment the lines below to insert sample data for development/testing.
-- Make sure you have passwords hashed first!
-- In production, don't include sample data.
-- ========================================================================

/*
-- Sample user (password is 'password123' hashed with bcrypt)
-- This is just an example hash - generate real ones in Python!
INSERT INTO users (username, email, password_hash) VALUES
('john_doe', 'john@example.com', '$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ee5XYOJ8NW0vPJbG'),
('jane_smith', 'jane@example.com', '$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ee5XYOJ8NW0vPJbG');

-- Sample expenses for john_doe (user_id = 1)
INSERT INTO expenses (user_id, title, amount, category, date, description) VALUES
(1, 'Coffee at Starbucks', 5.50, 'Food', '2026-06-10', 'Morning coffee before work'),
(1, 'Gas fill-up', 45.00, 'Transport', '2026-06-10', 'Filled up at Shell'),
(1, 'Movie tickets', 28.00, 'Entertainment', '2026-06-09', 'Evening movie with friend'),
(1, 'Groceries', 75.25, 'Food', '2026-06-08', 'Weekly grocery shopping at Trader Joe''s'),
(1, 'Gym membership', 50.00, 'Health', '2026-06-01', 'Monthly gym fee');

-- Sample expenses for jane_smith (user_id = 2)
INSERT INTO expenses (user_id, title, amount, category, date, description) VALUES
(2, 'Restaurant dinner', 65.00, 'Food', '2026-06-10', 'Dinner at Italian place'),
(2, 'Yoga class', 25.00, 'Health', '2026-06-10', 'Weekly yoga session'),
(2, 'Book purchase', 15.99, 'Entertainment', '2026-06-09', 'New fiction book');
*/


-- ========================================================================
-- VERIFICATION: Check table structure
-- ========================================================================
-- Run these queries to verify tables were created correctly:
-- 
--   SHOW TABLES;
--   DESCRIBE users;
--   DESCRIBE expenses;
--   SHOW CREATE TABLE expenses;
-- ========================================================================
