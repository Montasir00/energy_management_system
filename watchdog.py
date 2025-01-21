import os
import mysql.connector
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Database credentials
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_user = os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQL_PASSWORD', '123456')
mysql_db = os.getenv('MYSQL_DB', 'sensors_data')

# Connect to the database with retry logic
def get_db_connection():
    retry_count = 5  # Set a maximum number of retries
    while retry_count > 0:
        try:
            connection = mysql.connector.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                database=mysql_db
            )
            print("Connected to the database.")
            return connection
        except mysql.connector.errors.InterfaceError as e:
            print(f"Connection failed: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            retry_count -= 1

    raise Exception("Could not connect to MySQL after multiple attempts.")

# Function to calculate the average of the last 10 entries
def calculate_average(cursor, table_name, column_name):
    query = f"SELECT {column_name} FROM {table_name} ORDER BY id DESC LIMIT 10"
    cursor.execute(query)
    rows = cursor.fetchall()
    if not rows:
        return None
    values = [row[0] for row in rows]
    return sum(values) / len(values)

# Function to get the latest data
def get_latest_data(cursor, table_name, column_name):
    query = f"SELECT {column_name} FROM {table_name} ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    return row[0] if row else None

# Function to monitor and trigger an alert
def monitor_and_alert():
    connection = get_db_connection()  # Establish database connection with retry
    cursor = connection.cursor()

    table_name = 'lights'  # Replace with the appropriate table
    column_name = 'light_intensity'  # Replace with the appropriate column

    while True:
        average = calculate_average(cursor, table_name, column_name)
        latest_data = get_latest_data(cursor, table_name, column_name)

        if average is not None and latest_data is not None:
            threshold = average * 1.3  # 30% above the average
            if latest_data > threshold:
                print(f"🚨 ALERT! Latest value ({latest_data}) exceeds threshold ({threshold:.2f}).")

        # Wait for a few seconds before checking again
        time.sleep(10)

if __name__ == "__main__":
    print("Starting watchdog...")
    monitor_and_alert()
