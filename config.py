MQTT_BROKER_IP = "192.168.X.X"  # <--- CHANGE THIS TO YOUR PI'S IP
MQTT_PORT = 1883

# --- MQTT TOPICS (The "Channels") ---
# 1. Vision System (Laptop -> Pi)
TOPIC_EMOTION = "vision/infer/mood"

# 2. Telemetry (Pi -> Dashboard)
# This sends one big JSON with Temp, HR, Fatigue, and Status
TOPIC_TELEMETRY = "cabin/telemetry"

# 3. Control Commands (Dashboard -> Pi)
# Used to trigger the "Drowsiness Simulation" button
TOPIC_CONTROL_SIM = "control/simulation"

# --- SYSTEM THRESHOLDS ---
# Fatigue Index (0-100)
FATIGUE_THRESHOLD_WARNING = 50   # Lights turn Orange
FATIGUE_THRESHOLD_CRITICAL = 80  # Emergency Stop (Red Strobe)

# Comfort Logic
TEMP_THRESHOLD_HOT = 28.0        # Above this, lights go Cool Blue

# --- HARDWARE PINS (Reference Only) ---
# These are used inside the hardware modules, but good to keep here for reference.
PIN_DHT = 4       # GPIO 4
PIN_LEDS = 18     # GPIO 18 (PWM)