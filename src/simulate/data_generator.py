import random
import time
import math

class ComplexBioSimulator:
    def __init__(self):
        # --- SYSTEM STATE ---
        self.state = "NORMAL"  # Options: NORMAL, DROWSINESS_EVENT, STRESS_EVENT
        
        # --- PHYSIOLOGICAL PARAMETERS ---
        self.heart_rate = 75.0      # bpm
        self.hrv = 50.0             # Heart Rate Variability (ms) - crucial for stress
        self.fatigue_index = 10.0   # 0-100 scale (100 = Asleep)
        
        # --- SIMULATION PHYSICS ---
        # How fast parameters change per tick (Simulating biological lag)
        self.hr_drift_speed = 0.5   
        self.fatigue_drift_speed = 1.5 

    def set_scenario(self, scenario_name):
        """
        Called by MQTT triggers to start a specific demo scenario.
        """
        print(f"🔄 SIMULATOR STATE CHANGE: {self.state} -> {scenario_name}")
        self.state = scenario_name

    def update_tick(self):
        """
        Updates the internal biological model. Call this 1x per second.
        """
        # 1. SCENARIO LOGIC
        if self.state == "DROWSINESS_EVENT":
            # In drowsiness, HR drops, HRV increases slightly, Fatigue spikes
            target_hr = 55.0
            target_fatigue = 95.0
            target_hrv = 65.0
            
        elif self.state == "STRESS_EVENT":
            # In stress, HR spikes, HRV crashes, Fatigue is low (hyper-alert)
            target_hr = 110.0
            target_fatigue = 5.0
            target_hrv = 20.0 # Low HRV = High Stress
            
        else: # NORMAL
            target_hr = 75.0
            target_fatigue = 10.0
            target_hrv = 50.0

        # 2. PHYSICS DRIFT (Smoothing) - No instant jumps!
        self.heart_rate = self._smooth_move(self.heart_rate, target_hr, self.hr_drift_speed)
        self.fatigue_index = self._smooth_move(self.fatigue_index, target_fatigue, self.fatigue_drift_speed)
        self.hrv = self._smooth_move(self.hrv, target_hrv, 0.8)

        # 3. ADD NOISE (Sensor Imperfection)
        final_hr = self.heart_rate + random.uniform(-1.5, 1.5)
        final_fatigue = min(100, max(0, self.fatigue_index + random.uniform(-0.5, 0.5)))
        
        return {
            "heart_rate": round(final_hr, 1),
            "hrv": round(self.hrv, 1),
            "fatigue_index": int(final_fatigue),
            "simulation_state": self.state
        }

    def _smooth_move(self, current, target, step):
        """Helper function to move values gradually."""
        if current < target:
            return min(current + step, target)
        elif current > target:
            return max(current - step, target)
        return current