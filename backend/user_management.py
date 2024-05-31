import mysql.connector
import logging
from dotenv import load_dotenv
import os

# Database configuration
# Database connection details
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_config = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_name
}

logger = logging.getLogger(__name__)

def create_user(phone_number):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT * FROM User WHERE phoneNumber = %s", (phone_number,))
        user = cursor.fetchone()

        if user:
            logger.info(f'User already exists: {user}')
        else:
            # Create a new user
            cursor.execute("INSERT INTO User (phoneNumber, email) VALUES (%s, %s)", (phone_number, f'{phone_number}@example.com'))
            conn.commit()
            logger.info(f'Created new user with phone number {phone_number}')

    except mysql.connector.Error as err:
        logger.error(f'Error creating user: {err}')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
