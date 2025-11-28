import time
import board
import busio
import adafruit_dht
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1x15 as ads1x15

class SensorManager:
    def __init__(self):
        # --- 1. SETUP DHT22 (Temperature & Humidity) ---
        try:
            self.dht_sensor = adafruit_dht.DHT22(board.D4)
            print("✅ DHT22 Sensor initialized on Pin D4")
        except Exception as e:
            print(f"❌ Error initializing DHT22: {e}")
            self.dht_sensor = None

        # --- 2. SETUP MQ135 (Air Quality via ADC) ---
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS1115(self.i2c, address=0x48)
            self.mq_channel = AnalogIn(self.ads, ads1x15.Pin.A0)
            print("✅ MQ135 (ADS1115) initialized on I2C")
        except Exception as e:
            print(f"❌ Error initializing MQ135/ADS1115: {e}")
            self.mq_channel = None
        
        print("✓ Sensor Manager initialized")

    def classify_air_quality(self, voltage):
        """
        Classifies air quality based on voltage thresholds
        Returns PPM estimate for compatibility with main controller
        """
        if voltage < 0.30:
            return 50  # Excellent
        elif voltage < 0.45:
            return 100  # Good
        elif voltage < 0.60:
            return 200  # Moderate
        elif voltage < 0.80:
            return 300  # Poor
        else:
            return 400  # Hazardous

    def read_dht22(self):
        """
        Read DHT22 sensor for temperature and humidity
        Returns: (temperature, humidity) in Celsius and %
        """
        if not self.dht_sensor:
            return 0.0, 0.0
        
        try:
            temp = self.dht_sensor.temperature
            humidity = self.dht_sensor.humidity
            
            if temp is not None and humidity is not None:
                return round(temp, 1), round(humidity, 1)
            else:
                return 0.0, 0.0
                
        except RuntimeError as error:
            # DHT sensors are slow and often fail to read; this is normal
            return 0.0, 0.0
        except Exception as error:
            print(f"⚠️ DHT Read Error: {error}")
            return 0.0, 0.0

    def read_mq135(self):
        """
        Read MQ135 air quality sensor via ADS1115
        Returns: air quality in PPM estimate
        """
        if not self.mq_channel:
            return 0
        
        try:
            voltage = self.mq_channel.voltage
            ppm = self.classify_air_quality(voltage)
            return ppm
        except Exception as error:
            print(f"⚠️ MQ135 Read Error: {error}")
            return 0

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
    
    def get_detailed_reading(self):
        """
        Get detailed sensor reading with voltage info (for debugging)
        """
        data = {
            "temp": None,
            "humidity": None,
            "air_voltage": None,
            "air_quality_ppm": None
        }

        # Read DHT22
        if self.dht_sensor:
            try:
                data["temp"] = self.dht_sensor.temperature
                data["humidity"] = self.dht_sensor.humidity
            except RuntimeError:
                pass
            except Exception as error:
                print(f"⚠️ DHT Read Error: {error}")

        # Read MQ135
        if self.mq_channel:
            try:
                voltage = self.mq_channel.voltage
                data["air_voltage"] = round(voltage, 3)
                data["air_quality_ppm"] = self.classify_air_quality(voltage)
            except Exception as error:
                print(f"⚠️ MQ135 Read Error: {error}")

        return data

# Quick test
if __name__ == "__main__":
    sensors = SensorManager()
    print("🔎 Testing Sensors... (Press Ctrl+C to stop)")
    try:
        while True:
            # Test read_all() method (for main controller)
            data = sensors.read_all()
            print(f"🌡️ Temp: {data['temperature']}°C | "
                  f"💧 Hum: {data['humidity']}% | "
                  f"💨 Air: {data['air_quality']} PPM")
            
            # Also show detailed reading
            detailed = sensors.get_detailed_reading()
            if detailed['air_voltage']:
                print(f"   (Voltage: {detailed['air_voltage']}V)")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n✅ Sensor test ended.")