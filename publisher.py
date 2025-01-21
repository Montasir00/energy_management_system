import os
import paho.mqtt.client as mqtt
import json
import time
import random
import keyboard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Broker credentials
broker = os.getenv('MQTT_BROKER_URL')
port = int(os.getenv('MQTT_PORT', 8883))  
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')

# Data generation interval
DATA_GENERATION_INTERVAL = float(os.getenv('DATA_GENERATION_INTERVAL', 5))

# MQTT topics
TOPIC_LIGHT = 'devices/light'
TOPIC_AC = 'devices/ac'
TOPIC_HEATER = 'devices/heater'

# Function to get the current time
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

# Data generation functions using normal distribution
def generate_light_data():
    # Simulating light intensity with a normal distribution
    # Mean = 50 (average intensity), Std Dev = 10 (controls variability)
    light_intensity = round(random.normalvariate(50, 10), 2)
    
    # Ensure the light intensity stays within a reasonable range (0-100)
    light_intensity = max(0, min(100, light_intensity))
    
    return {"timestamp": get_time(), "light_intensity": light_intensity}


def generate_ac_data():
    # Simulating AC temperature with mean=22°C and std_dev=2°C
    ac_temperature = round(random.normalvariate(22, 2), 2)
    return {"timestamp": get_time(), "ac_temperature": ac_temperature}

def generate_heater_data():
    # Simulating Heater temperature with mean=22°C and std_dev=2°C
    heater_temperature = round(random.normalvariate(22, 2), 2)
    return {"timestamp": get_time(), "heater_temperature": heater_temperature}

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print(f"Connection failed with code {rc}")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(username, password)
client.tls_set()  # Enable TLS for secure connection
client.connect(broker, port, 60)
client.loop_start()

# Data generation control
generating_data = False

# Function to toggle data generation
def toggle_data_generation():
    global generating_data
    generating_data = not generating_data
    if generating_data:
        print("Data generation started. Press 's' to stop.")
    else:
        print("Data generation stopped. Press 'g' to start.")

keyboard.on_press_key('g', lambda _: toggle_data_generation() if not generating_data else None)
keyboard.on_press_key('s', lambda _: toggle_data_generation() if generating_data else None)

print("Press 'g' to start data generation, 's' to stop, and 'q' to quit.")

# Main loop for generating and publishing data
try:
    while True:
        if generating_data:
            light_data = generate_light_data()
            client.publish(TOPIC_LIGHT, json.dumps(light_data))
            print(f"Published to {TOPIC_LIGHT}: {light_data}")

            ac_data = generate_ac_data()
            client.publish(TOPIC_AC, json.dumps(ac_data))
            print(f"Published to {TOPIC_AC}: {ac_data}")

            heater_data = generate_heater_data()
            client.publish(TOPIC_HEATER, json.dumps(heater_data))
            print(f"Published to {TOPIC_HEATER}: {heater_data}")

            time.sleep(DATA_GENERATION_INTERVAL)  # Wait before generating new data
        else:
            time.sleep(0.1)

        # Check for quit key
        if keyboard.is_pressed('q'):
            print("Quitting...")
            break

except KeyboardInterrupt:
    print("Publisher stopped")

finally:
    client.loop_stop()
    client.disconnect()
