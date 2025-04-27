import os
import paho.mqtt.client as mqtt
import mysql.connector
import json
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
# Suppress detailed logs from libraries
logging.getLogger('mysql.connector').setLevel(logging.WARNING)
logging.getLogger('paho').setLevel(logging.WARNING)


# Database credentials
mysql_host = os.getenv('MYSQL_HOST', "mysql")
mysql_user = os.getenv('MYSQL_USER', "root")
mysql_password = os.getenv('MYSQL_PASSWORD', "123456")
mysql_db = os.getenv('MYSQL_DB', "sensors_data")

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# Connect to MySQL
try:
    mysql_conn = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db
    )
    cursor = mysql_conn.cursor()
    logging.info("🎉 Connected to MySQL database.")
except mysql.connector.Error as err:
    logging.error(f"🚨 MySQL connection error: {err}")
    exit(1)

# Create tables if not exist
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lights (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            light_intensity FLOAT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ac (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            ac_temperature FLOAT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heater (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            heater_temperature FLOAT NOT NULL
        )
    """)

create_tables(cursor)

# Insert functions
def insert_lights(cursor, data):
    cursor.execute(
        "INSERT INTO lights (timestamp, light_intensity) VALUES (%s, %s)",
        (data["timestamp"], data["light_intensity"])
    )
    mysql_conn.commit()

def insert_ac(cursor, data):
    cursor.execute(
        "INSERT INTO ac (timestamp, ac_temperature) VALUES (%s, %s)",
        (data['timestamp'], data['ac_temperature'])
    )
    mysql_conn.commit()

def insert_heater(cursor, data):
    cursor.execute(
        "INSERT INTO heater (timestamp, heater_temperature) VALUES (%s, %s)",
        (data['timestamp'], data['heater_temperature'])
    )
    mysql_conn.commit()

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("✅ Connected to MQTT broker.")
        client.subscribe([
            ("devices/light", 0),
            ("devices/ac", 0),
            ("devices/heater", 0)
        ])
    else:
        logging.error(f"🚨 MQTT connection failed (code {rc}).")

# MQTT message callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        if msg.topic == "devices/light":
            insert_lights(cursor, data)
        elif msg.topic == "devices/ac":
            insert_ac(cursor, data)
        elif msg.topic == "devices/heater":
            insert_heater(cursor, data)
        logging.info(f"📩 Data from {msg.topic} stored.")
    except json.JSONDecodeError:
        logging.error(f"⚠️ Invalid JSON from {msg.topic}.")
    except KeyError as e:
        logging.error(f"⚠️ Missing key in data: {e}")

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

# Connect to MQTT broker
try:
    client.connect(broker, port, 60)
    logging.info(f"🌐 MQTT broker connected at {broker}:{port}")
except Exception as e:
    logging.error(f"🚨 MQTT connection error: {e}")
    exit(1)

# Start MQTT client loop
try:
    logging.info("🚀 Subscriber running... Press Ctrl+C to stop.")
    client.loop_forever()
except KeyboardInterrupt:
    logging.info("🛑 Subscriber stopped.")
finally:
    client.disconnect()
    cursor.close()
    mysql_conn.close()
    logging.info("✅ Cleanup complete: MQTT and MySQL connections closed.")
