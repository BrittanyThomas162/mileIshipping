import os
import psycopg2
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


# Shipping rates to initialize
rates = [
    {'pounds': '1 lb', 'usd': 4.83, 'jmd': 750},
    {'pounds': '2 lbs', 'usd': 6.76, 'jmd': 1100},
    {'pounds': '3 lbs', 'usd': 9.33, 'jmd': 1540},
    {'pounds': '4 lbs', 'usd': 12.37, 'jmd': 2050},
    {'pounds': '5 lbs', 'usd': 14.30, 'jmd': 2400},
    {'pounds': '6 lbs', 'usd': 16.80, 'jmd': 2800},
    {'pounds': '7 lbs', 'usd': 20.00, 'jmd': 3300},
    {'pounds': '8 lbs', 'usd': 23.83, 'jmd': 3950},
    {'pounds': '9 lbs', 'usd': 26.97, 'jmd': 4450},
    {'pounds': '10 lbs', 'usd': 30.00, 'jmd': 4950},
]

# SQL queries
check_rate_query = """
SELECT COUNT(*) FROM "shipping_rates" WHERE pounds = %s;
"""
insert_rate_query = """
INSERT INTO "shipping_rates" (pounds, usd, jmd)
VALUES (%s, %s, %s);
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
    
    # Initialize shipping rates
    for rate in rates:
        cursor.execute(check_rate_query, (rate['pounds'],))
        rate_count = cursor.fetchone()[0]

        if rate_count == 0:
            cursor.execute(insert_rate_query, (rate['pounds'], rate['usd'], rate['jmd']))
            print(f"Added rate for {rate['pounds']}")
        else:
            print(f"Rate for {rate['pounds']} already exists")

    # Commit the transaction
    connection.commit()
    print("Shipping rates initialized successfully")

except Exception as error:
    print(f"Error connecting to the database or initializing shipping rates: {error}")

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Database connection closed")
