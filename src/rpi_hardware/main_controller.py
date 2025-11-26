import time
import json
import paho.mqtt.client as mqtt
import config

# Import our modules
from src.rpi_hardware.sensors import EnvironmentSensors
from src.rpi_hardware.actuators import ActuatorSystem
from src.simulation.data_generator import ComplexBioSimulator

# --- CONFIGURATION ---
FATIGUE_THRESHOLD_WARNING = 50
FATIGUE_THRESHOLD_CRITICAL = 80
TOPIC_TELEMETRY = "cabin/telemetry"

class CabinController:
    def __init__(self):
        print("🚀 Initializing Cabin ComfortSync System...")
        
        # 1. Initialize Hardware & Simulator
        self.bio_sim = ComplexBioSimulator()
        self.sensors = EnvironmentSensors()
        self.actuators = ActuatorSystem()
        
        # 2. System State
        self.latest_vision_emotion = "neutral"
        self.system_status = "NORMAL" # NORMAL, WARNING, EMERGENCY
        self.emergency_active = False

    def on_mqtt_message(self, client, userdata, msg):
        """Handles commands from Dashboard/Laptop"""
        try:
            payload = json.loads(msg.payload.decode())

            # Vision Data from Laptop
            if msg.topic == config.TOPIC_EMOTION:
                self.latest_vision_emotion = payload.get("emotion", "neutral")
            
            # Simulation Commands from Dashboard
            elif msg.topic == "control/simulation":
                mode = payload.get("mode") # "DROWSINESS_EVENT" or "NORMAL"
                self.bio_sim.set_scenario(mode)
                print(f"🔄 Scenario Changed to: {mode}")

        except Exception as e:
            print(f"MQTT Error: {e}")

    def run_loop(self, client):
        """Main Sensor Fusion Loop"""
        print("✅ System Ready. Monitoring...")
        
        while True:
            # --- A. GATHER DATA ---
            # 1. Real Sensors
            env_data = self.sensors.read_data()
            
            # 2. Simulated Biometrics (Physics drift happens here)
            bio_data = self.bio_sim.update_tick()
            
            # --- B. FUSION LOGIC (The "Complex" Part) ---
            fatigue_score = bio_data['fatigue_index']
            
            # Increase risk if Vision detects eyes closing (simplified to emotion here)
            if self.latest_vision_emotion in ["sad", "fear"]:
                fatigue_score += 10 # Fusion bonus

            # --- C. SYSTEM RESPONSE ---
            if fatigue_score > FATIGUE_THRESHOLD_CRITICAL:
                # EMERGENCY STATE
                if self.system_status != "EMERGENCY":
                    self.system_status = "EMERGENCY"
                    self.actuators.activate_emergency_protocol(True)
                    print(f"🚨 CRITICAL FATIGUE ({fatigue_score}) - EMERGENCY PROTOCOL ACTIVE")
            
            elif fatigue_score > FATIGUE_THRESHOLD_WARNING:
                # WARNING STATE
                self.system_status = "WARNING"
                self.actuators.activate_emergency_protocol(False) # Ensure strobe is off
                self.actuators.set_mood_lighting("ALERT") # Solid Orange
                
            else:
                # NORMAL STATE
                self.system_status = "NORMAL"
                self.actuators.activate_emergency_protocol(False)
                
                # Adaptive Comfort Logic
                temp = env_data.get('temp')
                if temp and temp > 28:
                    self.actuators.set_mood_lighting("CALM") # Cooling Blue
                else:
                    self.actuators.set_mood_lighting("WARM") # Cozy Warm

            # --- D. PUBLISH TELEMETRY ---
            # Send ONE packet so Dashboard graph is perfectly synced
            telemetry = {
                "timestamp": time.time(),
                "status": self.system_status,
                "env": env_data,
                "bio": bio_data,
                "vision": self.latest_vision_emotion,
                "risk_score": fatigue_score
            }
            client.publish(TOPIC_TELEMETRY, json.dumps(telemetry))
            
            # Loop at 2Hz (every 0.5s)
            time.sleep(0.5)

if __name__ == "__main__":
    # MQTT Setup
    client = mqtt.Client()
    
    # We need to pass the controller instance to the callback, 
    # but paho-mqtt makes that tricky. We'll set it up in the controller.
    controller = CabinController()
    client.on_message = controller.on_mqtt_message
    
    try:
        client.connect(config.MQTT_BROKER_IP, config.MQTT_PORT)
        client.subscribe([(config.TOPIC_EMOTION, 0), ("control/simulation", 0)])
        client.loop_start()
        
        controller.run_loop(client)
    except KeyboardInterrupt:
        print("\nStopping System...")
        controller.actuators.activate_emergency_protocol(False)
        controller.actuators.set_mood_lighting("OFF")
        client.loop_stop()