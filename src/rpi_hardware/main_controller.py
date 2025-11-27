import time
import json
import os
import sys

# Add root path to find modules if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rpi_hardware.sensors import EnvironmentSensors
from src.rpi_hardware.actuators import ActuatorSystem
from src.simulate.data_generator import ComplexBioSimulator

# --- CONFIGURATION ---
STATE_FILE = "state.json"
COMMAND_FILE = "cmd.json"
FATIGUE_THRESHOLD_CRITICAL = 80
FATIGUE_THRESHOLD_WARNING = 50

class CabinController:
    def __init__(self):
        print("🚀 Initializing Local Cabin Controller...")
        self.bio_sim = ComplexBioSimulator()
        self.sensors = EnvironmentSensors()
        self.actuators = ActuatorSystem()
        
        self.system_status = "NORMAL"
        self.latest_vision_emotion = "neutral"

        # Initialize files
        self.write_state({})
        with open(COMMAND_FILE, 'w') as f:
            json.dump({"mode": "NORMAL"}, f)

    def read_commands(self):
        """Checks if the Dashboard sent a command (like 'DROWSY MODE')."""
        try:
            if os.path.exists(COMMAND_FILE):
                with open(COMMAND_FILE, 'r') as f:
                    cmd = json.load(f)
                    mode = cmd.get("mode", "NORMAL")
                    # Update Simulator
                    self.bio_sim.set_scenario(mode)
        except Exception:
            pass # Ignore read errors (file might be busy)

    def write_state(self, data):
        """Writes current system state to JSON for the Dashboard to see."""
        try:
            # Atomic write (write temp then rename) prevents reading half-written files
            temp_file = STATE_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            os.replace(temp_file, STATE_FILE)
        except Exception as e:
            print(f"Error writing state: {e}")

    def run_loop(self):
        print("✅ System Running. Writing to state.json...")
        
        while True:
            # 1. READ COMMANDS (From Dashboard)
            self.read_commands()

            # 2. READ REAL SENSORS
            env_data = self.sensors.read_data()
            
            # 3. READ HARDWARE STATUS
            hw_state = self.actuators.get_state()
            
            # 4. UPDATE SIMULATION
            bio_data = self.bio_sim.update_tick()
            
            # 5. LOGIC & FUSION
            fatigue_score = bio_data['fatigue_index']
            
            # 6. ACTUATOR CONTROL
            if fatigue_score > FATIGUE_THRESHOLD_CRITICAL:
                if self.system_status != "EMERGENCY":
                    self.system_status = "EMERGENCY"
                    self.actuators.activate_emergency_protocol(True)
            elif fatigue_score > FATIGUE_THRESHOLD_WARNING:
                self.system_status = "WARNING"
                self.actuators.activate_emergency_protocol(False)
                self.actuators.set_mood_lighting("ALERT")
            else:
                self.system_status = "NORMAL"
                self.actuators.activate_emergency_protocol(False)
                # Adaptive Comfort
                if env_data.get('temp', 0) > 28:
                    self.actuators.set_mood_lighting("CALM")
                else:
                    self.actuators.set_mood_lighting("WARM")

            # 7. SAVE STATE FOR DASHBOARD
            full_state = {
                "timestamp": time.time(),
                "status": self.system_status,
                "env": env_data,           # REAL SENSOR DATA
                "bio": bio_data,           # SIMULATED DATA
                "hardware": hw_state,      # REAL LIGHT/SOUND STATE
                "vision": "neutral"        # Placeholder if running purely local
            }
            self.write_state(full_state)
            
            # Run fast for responsiveness
            time.sleep(0.1)

if __name__ == "__main__":
    controller = CabinController()
    try:
        controller.run_loop()
    except KeyboardInterrupt:
        print("Stopping...")
        controller.actuators.activate_emergency_protocol(False)
        controller.actuators.set_mood_lighting("OFF")