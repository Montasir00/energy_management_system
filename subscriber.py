import os
import paho.mqtt.client as mqtt
import mysql.connector
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials
mysql_host = os.getenv('MYSQL_HOST', "localhost")
mysql_user = os.getenv('MYSQL_USER', "root")
mysql_password = os.getenv('MYSQL_PASSWORD', "123456")
mysql_db = os.getenv('MYSQL_DB', "sensors_data")

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# MQTT topics
TOPIC_LIGHT = 'devices/light'
TOPIC_AC = 'devices/ac'
TOPIC_HEATER = 'devices/heater'

# Insert functions for MySQL
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
            timestamp VARCHAR(50),
            ac_temperature FLOAT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heater (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(50),
            heater_temperature FLOAT
        )
    """)
# Database connection
mysql_conn = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_db
)

cursor = mysql_conn.cursor()
create_tables(cursor)

def insert_lights(cursor, data):
    """Insert light intensity data into the lights table."""
    cursor.execute(
        "INSERT INTO lights (timestamp, light_intensity) VALUES (%s, %s)",
        (data["timestamp"], data["light_intensity"])
    )
    mysql_conn.commit()

def insert_ac(cursor, data):
    """Insert AC data into the ac table."""
    cursor.execute(
        "INSERT INTO ac (timestamp, ac_temperature) VALUES (%s, %s)",
        (data['timestamp'], data['ac_temperature'])
    )
    mysql_conn.commit()

def insert_heater(cursor, data):
    """Insert heater data into the heater table."""
    cursor.execute(
        "INSERT INTO heater (timestamp, heater_temperature) VALUES (%s, %s)",
        (data['timestamp'], data['heater_temperature'])
    )
    mysql_conn.commit()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe([
            ("devices/light", 0),  
            ("devices/ac", 0),      
            ("devices/heater", 0)  
        ])
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    data = json.loads(msg.payload)
    if msg.topic == TOPIC_LIGHT:
        insert_lights(cursor, data)
    elif msg.topic == TOPIC_AC:
        insert_ac(cursor, data)
    elif msg.topic == TOPIC_HEATER:
        insert_heater(cursor, data)
    print(f"Received and stored data for {msg.topic}")


# MQTT client setup
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

client.connect(broker, port, 60)

# Start MQTT client loop
try:
    print("Subscriber started. Press Ctrl+C to stop.")
    client.loop_forever()
except KeyboardInterrupt:
    print("Subscriber stopped")
finally:
    client.disconnect()
    cursor.close()
    mysql_conn.close()
