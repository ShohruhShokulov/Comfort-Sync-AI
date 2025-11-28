import sys
import time
sys.path.append('../simulate')

from sensors import SensorManager
from actuators import ActuatorSystem
from data_generator import SmartWatchSimulator, StressScenario

# Test each component individually
print("="*70)
print("🧪 Testing Individual Components")
print("="*70)

# Test sensors
print("\n1️⃣ Testing Sensors...")
sensors = SensorManager()

print("   Reading DHT22...")
temp, humidity = sensors.read_dht22()
print(f"   Temperature: {temp}°C")
print(f"   Humidity: {humidity}%")

print("   Reading MQ135...")
air_quality = sensors.read_mq135()
print(f"   Air Quality: {air_quality} PPM")

print("   Reading all sensors combined...")
sensor_data = sensors.read_all()
print(f"   Combined data: {sensor_data}")
print("   ✓ Sensors working!")

# Test smartwatch
print("\n2️⃣ Testing Smartwatch Simulator...")
smartwatch = SmartWatchSimulator()
smartwatch.set_scenario(StressScenario.NORMAL)
watch_data = smartwatch.get_data()
print(f"   Heart Rate: {watch_data['heart_rate']} bpm")
print(f"   Stress: {watch_data['stress_level']}%")
print("   ✓ Smartwatch working!")

# Test actuators
print("\n3️⃣ Testing Actuators...")
actuators = ActuatorSystem()
print("   Testing cabin lighting...")
actuators.set_cabin_lighting('cabin_day', brightness=120)
time.sleep(2)
print("   Testing cooling lighting...")
actuators.set_cabin_lighting('cooling', brightness=200)
time.sleep(2)
print("   Playing sound...")
actuators.play_sound('calming_deep')
time.sleep(3)
actuators.stop_sound()
print("   ✓ Actuators working!")

print("\n" + "="*70)
print("✅ All components tested!")
print("="*70)
