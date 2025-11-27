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
                print(f"DHT Read Error: {error}")

        # --- READ MQ135 ---
        if self.mq_channel:
            try:
                raw = self.mq_channel.value
                voltage = self.mq_channel.voltage
                data["air_voltage"] = round(voltage, 3)
                data["air_quality"] = self.read_air_quality(voltage)
            except Exception as error:
                print(f"MQ135 Read Error: {error}")

        return data

class SensorManager:
    def __init__(self):
        self.environment_sensors = EnvironmentSensors()
        print("✓ Sensor Manager initialized")
    
    def read_dht22(self):
        """
        Read temperature and humidity from DHT22 sensor
        Returns:
            tuple: (temperature, humidity)
        """
        data = {
            "temp": None,
            "humidity": None
        }

        if self.environment_sensors.dht_sensor:
            try:
                data["temp"] = self.environment_sensors.dht_sensor.temperature
                data["humidity"] = self.environment_sensors.dht_sensor.humidity
            except RuntimeError as error:
                pass 
            except Exception as error:
                print(f"DHT Read Error: {error}")

        return data["temp"], data["humidity"]

    def read_mq135(self):
        """
        Read air quality from MQ135 sensor
        Returns:
            int: Air quality index
        """
        data = {
            "air_voltage": None,
            "air_quality": "Unknown"
        }

        if self.environment_sensors.mq_channel:
            try:
                voltage = self.environment_sensors.mq_channel.voltage
                data["air_voltage"] = round(voltage, 3)
                data["air_quality"] = self.environment_sensors.read_air_quality(voltage)
            except Exception as error:
                print(f"MQ135 Read Error: {error}")

        return data["air_quality"]

    def read_all(self):
        """
        Read all sensors and return combined data dictionary
        Compatible with main_controller.py
        
        Returns:
            dict: {'temperature': float, 'humidity': float, 'air_quality': int}
        """
        temp, humidity = self.read_dht22()
        air_quality = self.read_mq135()
        
        return {
            'temperature': temp,
            'humidity': humidity,
            'air_quality': air_quality,
            'timestamp': time.time()
        }
    
    def get_sensor_status(self):
        """
        Get current status of all sensors
        Returns dict with sensor readings and status
        """
        data = self.read_all()
        
        return {
            'sensors': {
                'dht22': {
                    'temperature': data['temperature'],
                    'humidity': data['humidity'],
                    'status': 'OK' if data['temperature'] > 0 else 'ERROR'
                },
                'mq135': {
                    'air_quality': data['air_quality'],
                    'status': 'OK' if data['air_quality'] >= 0 else 'ERROR'
                }
            },
            'timestamp': data['timestamp']
        }

# --- Quick Test to verify wiring ---
if __name__ == "__main__":
    manager = SensorManager()
    print("🔎 Testing Sensors... (Press Ctrl+C to stop)")
    while True:
        status = manager.get_sensor_status()
        print(f"🌡️ Temp: {status['sensors']['dht22']['temperature']}C | Hum: {status['sensors']['dht22']['humidity']}% | Air: {status['sensors']['mq135']['air_quality']} ({status['sensors']['mq135']['air_quality']}V)")
        time.sleep(2)