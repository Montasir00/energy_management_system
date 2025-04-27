import os
import paho.mqtt.client as mqtt
import json
import time
import random
import keyboard
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))  # Default to port 8883 if not specified
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# Data generation interval (default to 5 seconds if not provided)
DATA_GENERATION_INTERVAL = float(os.getenv('DATA_GENERATION_INTERVAL', 5))

# MQTT topics for different devices
TOPIC_LIGHT = 'devices/light'
TOPIC_AC = 'devices/ac'
TOPIC_HEATER = 'devices/heater'

# Utility: Get the current time in a readable format
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

# Data generation functions
def generate_data(device, mean, std_dev, min_val, max_val, last_value_key):
    global last_values
    if last_value_key not in last_values:
        last_values[last_value_key] = round(random.normalvariate(mean, std_dev), 2)

    if random.random() < 0.2:  # 10% chance for a higher value
        value = last_values[last_value_key] * 1.3
    else:
        value = round(random.normalvariate(mean, std_dev), 2)

    value = max(min_val, min(max_val, value))  # Clamp to range
    last_values[last_value_key] = value
    return {"timestamp": get_time(), device: value}

# Publish data with formatted output
def publish_data(topic, data):
    client.publish(topic, json.dumps(data))
    print(f"""
Published to {topic}:
  - Timestamp: {data['timestamp']}
  - {list(data.keys())[1]}: {list(data.values())[1]}
""")

# MQTT connection callback to confirm the connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
    else:
        print(f"Connection failed with code {rc}")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(username, password)  # Set MQTT credentials
client.tls_set()  # Enable TLS for a secure connection
client.connect(broker, port, 60)  # Connect to the broker
client.loop_start()  # Start the network loop

# Flag to control data generation and last values storage
generating_data = False
last_values = {}

# Toggle data generation
def toggle_data_generation():
    global generating_data
    generating_data = not generating_data
    if generating_data:
        print("Data generation started. Press 's' to stop.")
    else:
        print("Data generation stopped. Press 'g' to start.")

# Configure keyboard shortcuts
keyboard.on_press_key('g', lambda _: toggle_data_generation() if not generating_data else None)
keyboard.on_press_key('s', lambda _: toggle_data_generation() if generating_data else None)

print("Press 'g' to start data generation, 's' to stop, and 'q' to quit.")

# Main loop
try:
    while True:
        if generating_data:
            # Generate and publish data for devices
            light_data = generate_data("light_intensity", 50, 10, 0, 100, "light")
            publish_data(TOPIC_LIGHT, light_data)

            ac_data = generate_data("ac_temperature", 22, 2, 15, 30, "ac")
            publish_data(TOPIC_AC, ac_data)

            heater_data = generate_data("heater_temperature", 22, 2, 15, 30, "heater")
            publish_data(TOPIC_HEATER, heater_data)

            time.sleep(DATA_GENERATION_INTERVAL)
        else:
            time.sleep(0.1)  # Small delay when idle

        if keyboard.is_pressed('q'):  # Quit on 'q'
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("Publisher stopped manually.")

finally:
    # Clean up MQTT client on exit
    print("Cleaning up resources...")
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker.")
