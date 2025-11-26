import time
import board
import busio
import adafruit_dht
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1x15 as ads1x15

class EnvironmentSensors:
    def __init__(self):
        # --- 1. SETUP DHT22 (Temperature & Humidity) ---
        # Using GPIO4 as per your wiring
        try:
            self.dht_sensor = adafruit_dht.DHT22(board.D4)
            print("✅ DHT22 Sensor initialized on Pin D4")
        except Exception as e:
            print(f"❌ Error initializing DHT22: {e}")
            self.dht_sensor = None

        # --- 2. SETUP MQ135 (Air Quality via ADC) ---
        # Using I2C (SCL/SDA) and ADS1115 at 0x48
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS1115(self.i2c, address=0x48)
            self.mq_channel = AnalogIn(self.ads, ads1x15.Pin.A0)
            print("✅ MQ135 (ADS1115) initialized on I2C")
        except Exception as e:
            print(f"❌ Error initializing MQ135/ADS1115: {e}")
            self.mq_channel = None

    def read_air_quality(self, voltage):
        """
        Classifies air quality based on the voltage thresholds you provided.
        """
        if voltage < 0.30: return "Excellent"
        elif voltage < 0.45: return "Good"
        elif voltage < 0.60: return "Moderate"
        elif voltage < 0.80: return "Poor"
        else: return "Hazardous"

    def read_data(self):
        """
        Returns a dictionary with current sensor readings.
        Handles errors gracefully (returns None for missing data).
        """
        data = {
            "temp": None,
            "humidity": None,
            "air_voltage": None,
            "air_quality": "Unknown"
        }

        # --- READ DHT22 ---
        if self.dht_sensor:
            try:
                data["temp"] = self.dht_sensor.temperature
                data["humidity"] = self.dht_sensor.humidity
            except RuntimeError as error:
                # DHT sensors are slow and often fail to read; this is normal.
                # We just ignore this frame's data.
                pass 
            except Exception as error:
                print(f"⚠️ DHT Read Error: {error}")

        # --- READ MQ135 ---
        if self.mq_channel:
            try:
                raw = self.mq_channel.value
                voltage = self.mq_channel.voltage
                data["air_voltage"] = round(voltage, 3)
                data["air_quality"] = self.read_air_quality(voltage)
            except Exception as error:
                print(f"⚠️ MQ135 Read Error: {error}")

        return data

# --- Quick Test to verify wiring ---
if __name__ == "__main__":
    sensors = EnvironmentSensors()
    print("🔎 Testing Sensors... (Press Ctrl+C to stop)")
    while True:
        reading = sensors.read_data()
        print(f"🌡️ Temp: {reading['temp']}C | 💧 Hum: {reading['humidity']}% | 💨 Air: {reading['air_quality']} ({reading['air_voltage']}V)")
        time.sleep(2)