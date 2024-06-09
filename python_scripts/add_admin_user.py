import os
import psycopg2
from werkzeug.security import generate_password_hash
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Parse the database URL to get connection parameters
url = urlparse(DATABASE_URL)
DB_HOST = url.hostname
DB_NAME = url.path[1:]  # Remove the leading '/'
DB_USER = url.username
DB_PASS = url.password
DB_PORT = url.port


# Admin user details from environment variables
ADMIN_FIRST_NAME = os.getenv('ADMIN_FIRST_NAME')
ADMIN_LAST_NAME = os.getenv('ADMIN_LAST_NAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PHONE = os.getenv('ADMIN_PHONE')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_ROLE = os.getenv('ADMIN_ROLE')

# Generate password hash
password_hash = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')

# SQL queries
check_user_query = """
SELECT COUNT(*) FROM "users" WHERE email = %s;
"""
insert_admin_query = """
INSERT INTO "users" (first_name, last_name, email, phone, password_hash, role)
VALUES (%s, %s, %s, %s, %s, %s);
"""

# Connect to PostgreSQL database and execute the queries
try:
    # Connect to the database
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    print("Database connection successful")
    cursor = connection.cursor()
    
    # Check if the user already exists
    cursor.execute(check_user_query, (ADMIN_EMAIL,))
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Execute the insert query if the user does not exist
        cursor.execute(insert_admin_query, (ADMIN_FIRST_NAME, ADMIN_LAST_NAME, ADMIN_EMAIL, ADMIN_PHONE, password_hash, ADMIN_ROLE))
        
        # Commit the transaction
        connection.commit()
        print("Admin user added successfully")
    else:
        print("Admin user already exists in the database")

except Exception as error:
    print(f"Error connecting to the database or adding admin user: {error}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Database connection closed")
