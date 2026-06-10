# Database Setup Instructions

## Step 1: Create the Database

### Option A: Using Command Line (Recommended)

```bash
# Navigate to project directory
cd e:\coding\dailyspend

# Run the SQL schema file
mysql -u root -p < database/schema.sql

# When prompted, enter your MySQL root password
```

### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Create a new connection or use existing
3. Open `File > Run SQL Script`
4. Select `database/schema.sql`
5. Click "Run"

### Option C: Manual - Copy & Paste in MySQL CLI

```bash
# Start MySQL CLI
mysql -u root -p

# In the MySQL prompt, paste the contents of database/schema.sql
mysql> source database/schema.sql;
```

## Step 2: Verify the Database Was Created

```bash
# Connect to MySQL
mysql -u root -p

# In MySQL prompt, run:
mysql> USE dailyspend;
mysql> SHOW TABLES;
```

Expected output:
```
+----------------------+
| Tables_in_dailyspend |
+----------------------+
| expenses             |
| users                |
+----------------------+
```

## Step 3: Check Table Structure

```bash
mysql> DESCRIBE users;
mysql> DESCRIBE expenses;
```

## Step 4: (Optional) Insert Sample Data

Uncomment the sample data section in `database/schema.sql` and re-run it, or:

```sql
-- Insert a test user
INSERT INTO users (username, email, password_hash) VALUES
('testuser', 'test@example.com', 'hashed_password_here');

-- Insert test expenses
INSERT INTO expenses (user_id, title, amount, category, date) VALUES
(1, 'Test Expense', 10.50, 'Food', '2026-06-10');
```

## Step 5: Test Connection from Python

Update your `.env` file with:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=dailyspend
```

Then test:
```python
from database.db import test_connection
if test_connection():
    print("✓ Database connection works!")
else:
    print("✗ Database connection failed")
```

## Troubleshooting

### "Access denied for user 'root'@'localhost'"
- Make sure you entered the correct MySQL root password
- If you forgot it, see MySQL documentation for password reset

### "Can't find database 'dailyspend'"
- Run the schema.sql file again to create it
- Check that the SQL executed without errors

### "Table 'expenses' doesn't exist"
- The SQL file may have failed to execute completely
- Check for error messages when running the SQL
- Try running individual table creation statements

### "Can't connect from Python"
- Check that MySQL is running
- Verify credentials in .env file match your MySQL setup
- Run `test_connection()` to debug
