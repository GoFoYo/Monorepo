import os
import psycopg2

def try_parse(type, value: str):
    try:
        return type(value)
    except Exception:
        return None
# Configuration for POSTGRES
POSTGRES_HOST = os.environ.get("POSTGRES_HOST") or "localhost"
POSTGRES_PORT = try_parse(int, os.environ.get("POSTGRES_PORT")) or 5432
POSTGRES_USER = os.environ.get("POSTGRES_USER") or "user"
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASS") or "pass"
POSTGRES_DB = os.environ.get("POSTGRES_DB") or "test_db"

# try:
#     # Establish connection to the database
#     connection = psycopg2.connect(
#         host=POSTGRES_HOST,
#         port=POSTGRES_PORT,
#         user=POSTGRES_USER,
#         password=POSTGRES_PASSWORD,
#         database=POSTGRES_DB
#     )

#     # Create a cursor object
#     cursor = connection.cursor()

#     # Execute a test query
#     cursor.execute("SELECT version();")

#     # Fetch and print the result
#     db_version = cursor.fetchone()
#     print("PostgreSQL Database Version:", db_version)

#     # Close the cursor and connection
#     cursor.close()
#     connection.close()

#     print("Connection to PostgreSQL database successful!")

# except psycopg2.Error as e:
#     print("Error connecting to PostgreSQL database:", e)