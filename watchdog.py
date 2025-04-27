import mysql.connector
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

mysql_host = os.getenv('MYSQL_HOST')
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_db = os.getenv('MYSQL_DB')

# --- EMAIL CONFIG ---
email_sender = 'fazlurrahaman365@gmail.com'
email_password = 'nmernyicbtpumkgo' 
email_recipient = 'hoodr4096@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587

def send_alert_email(latest_reading, threshold):
    """
    Sends an email alert if the latest sensor reading exceeds a threshold.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_recipient
        msg['Subject'] = "🚨 ALERT: Sensor Reading Exceeded"

        body = f"""
        ⚠️ ALERT: Sensor reading has exceeded the 30% threshold!

        📍 Current reading: {latest_reading:.2f}
        🔺 Threshold: {threshold:.2f}
        """

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.send_message(msg)

        print(f"✉️ Alert email sent to {email_recipient}")

    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db
        )
        if connection.is_connected():
            print("✅ Connected to the database")
            return connection
    except mysql.connector.Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
    return None

def get_last_10_readings(cursor, table_name, column_name):
    try:
        query = f"""
        SELECT {column_name}
        FROM {table_name}
        ORDER BY timestamp DESC
        LIMIT 10;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [row[0] for row in results]
    except mysql.connector.Error as e:
        print(f"❌ Error retrieving last 10 readings: {e}")
        return None

def get_latest_reading(cursor, table_name, column_name):
    try:
        query = f"""
        SELECT {column_name}
        FROM {table_name}
        ORDER BY timestamp DESC
        LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        return float(result[0]) if result else None
    except mysql.connector.Error as e:
        print(f"❌ Error retrieving latest reading: {e}")
        return None

def calculate_average(readings):
    if not readings:
        return None
    readings = [float(reading) for reading in readings]
    return sum(readings) / len(readings)

def monitor_and_alert():
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")

    table_name = 'lights'
    column_name = 'light_intensity'
    alert_sent = False

    try:
        while True:
            readings = get_last_10_readings(cursor, table_name, column_name)

            if readings:
                average = calculate_average(readings)
                print(f"📊 Last 10 readings: {readings}")
                print(f"📉 Average light intensity: {average:.2f}")

                latest_reading = get_latest_reading(cursor, table_name, column_name)
                if latest_reading is not None:
                    print(f"📍 Latest reading: {latest_reading:.2f}")
                    threshold = average * 1.3

                    if latest_reading > threshold:
                        print(f"🚨 ALERT! Value ({latest_reading:.2f}) > threshold ({threshold:.2f})")
                        if not alert_sent:
                            send_alert_email(latest_reading, threshold)
                            alert_sent = True
                    else:
                        print(f"✅ Value ({latest_reading:.2f}) within normal range")
                        alert_sent = False
                else:
                    print("⚠️ No latest reading found.")
            else:
                print("⚠️ No readings found in the database.")

            time.sleep(10)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    finally:
        cursor.close()
        connection.close()
        print("✅ Database connection closed")

def test_smtp_config():
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_recipient, "Subject: Test Email\n\nThis is a test.")
        print("✅ SMTP test email sent successfully.")
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")

# Start point
if __name__ == "__main__":
    test_smtp_config()  # Optional: comment out after verifying
    monitor_and_alert()
