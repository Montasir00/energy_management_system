# 📦 Containerized IoT Data Pipeline

This project demonstrates a fully containerized IoT data pipeline, consisting of three Python services—[[Publisher]], [[Subscriber]], and [[Watchdog]]—all orchestrated with [[Docker]] Compose. Each component runs in its own container, communicates over MQTT, persists data in MySQL, and (for Watchdog) sends email alerts. Docker ensures consistency, isolation, and easy deployment.
The [[DockerFile]] also makes **watchdog.py** an image.

---

## 🎯 1. Publisher

A simple Python script that:
- **Simulates sensor readings** (light, AC temperature, heater temperature) using a normal distribution plus occasional spikes.
- **Publishes** those readings as JSON messages to MQTT topics:
  - `devices/light`
  - `devices/ac`
  - `devices/heater`
- **Interactive controls** via keyboard:
  - Press **g** to start publishing
  - Press **s** to stop
  - Press **q** to quit

### Key functions
- `generate_data()`: returns `{"timestamp":…, "<metric>": value}`
- `publish_data()`: sends JSON to the broker and logs to console
- `on_connect()`: confirms MQTT connection

---

## 📥 2. Subscriber

A Python service that:
- **Connects** to the same MQTT broker over TLS
- **Listens** on the three topics above
- **Parses** each incoming JSON message
- **Inserts** the timestamp and metric into MySQL tables `lights`, `ac`, and `heater`

### Key functions
- `on_connect()`: subscribes to topics
- `on_message()`: routes each message to the correct `insert_*` function
- `create_tables()`: ensures tables exist on startup

---

## 🛎️ 3. Watchdog (Email Alert)

A Python “watchdog” that:
- **Reads** the last 10 entries from the `lights` table every 10 s
- **Computes** the average light intensity
- **Fetches** the latest single reading
- **Checks** if it exceeds 130% of the average
- **Sends** an email alert via SMTP (Gmail) when the threshold is breached

### Key functions
- `get_last_10_readings()`, `get_latest_reading()`, `calculate_average()`
- `send_alert_email()`: constructs and sends an alert message
- `monitor_and_alert()`: main loop tying everything together

---

## 🔗 Integration & Data Flow

1. **Publisher Container**
   - Runs the publisher script
   - Publishes to MQTT topics on the broker

2. **MQTT Broker**
   - Acts as the “post office” passing messages from Publisher → Subscriber

3. **Subscriber Container**
   - Subscribes to these topics
   - Writes each reading into MySQL

4. **MySQL Container**
   - Persists all sensor readings in durable storage

5. **Watchdog Container**
   - Reads data from MySQL
   - Performs threshold check
   - Sends email alerts

All services communicate over a private Docker network (`app-network`), so no external ports are exposed (except for monitoring UIs like phpMyAdmin).

---

## 🐳 How Docker Helped

- **Isolation**: Each service runs in its own container with its dependencies locked down.
- **Reproducibility**: “It works on my machine” is solved—containers behave identically on any host with Docker.
- **Orchestration**: Docker Compose brings up all components (`docker-compose up -d`) and tears them down cleanly (`docker-compose down`).
- **Networking**: Containers automatically share a bridge network, making service discovery easy—e.g., `subscriber` reaches MySQL at hostname `mysql`.
- **Persistence**: Named volumes (e.g., `mysql_data`) ensure database data survives container restarts.
- **Scalability**: You can spin up multiple publishers or watchdog instances without worrying about port conflicts or environment mismatches.

---

## 🛠️ Essential Docker Compose Commands

```bash
# Start all services in background
docker-compose up -d

# See container status and mapped ports
docker-compose ps

# View logs in real time
docker-compose logs -f

# Stop and remove containers (volumes remain)
docker-compose down
