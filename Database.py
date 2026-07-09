import psycopg2
from typing import Optional

def connect_to_database() -> Optional[psycopg2.extensions.connection]:
    """
    Simple function to connect to PostgreSQL database.
    """
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="BankData",
            user="yashodip",
            password="1234"
        )
        print("Connected to PostgreSQL database!")
        return connection
    except Exception as error:
        print("Error connecting to PostgreSQL database:", error)
        return None

# Test the connection
if __name__ == "__main__":
    conn = connect_to_database()
    if conn:
        conn.close()
        print("Connection closed.")