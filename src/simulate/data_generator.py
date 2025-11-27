import json
import time
import random
import math
from datetime import datetime
from enum import Enum

class StressScenario(Enum):
    NORMAL = "normal"
    MODERATE = "moderate"
    BAD = "bad"

class SmartWatchSimulator:
    def __init__(self):
        # Baseline values for different scenarios
        self.scenarios = {
            StressScenario.NORMAL: {
                "heart_rate_base": 72,
                "heart_rate_variance": 8,
                "stress_level_base": 25,
                "stress_level_variance": 10,
                "description": "Relaxed and comfortable state"
            },
            StressScenario.MODERATE: {
                "heart_rate_base": 95,
                "heart_rate_variance": 12,
                "stress_level_base": 60,
                "stress_level_variance": 15,
                "description": "Moderate stress, slightly uncomfortable"
            },
            StressScenario.BAD: {
                "heart_rate_base": 115,
                "heart_rate_variance": 18,
                "stress_level_base": 85,
                "stress_level_variance": 10,
                "description": "High stress, very uncomfortable"
            }
        }
        
        self.current_scenario = StressScenario.NORMAL
        self.time_offset = 0
        
    def generate_heart_rate(self, scenario):
        """Generate realistic heart rate with circadian rhythm and random variations"""
        config = self.scenarios[scenario]
        base = config["heart_rate_base"]
        variance = config["heart_rate_variance"]
        
        # Add circadian rhythm (slight sinusoidal variation)
        circadian = math.sin(self.time_offset * 0.1) * 5
        
        # Add random walk for realistic variation
        random_variation = random.gauss(0, variance / 2)
        
        # Occasional spikes (simulate movement or sudden stress)
        spike = 0
        if random.random() < 0.05:  # 5% chance of spike
            spike = random.randint(5, 15)
        
        heart_rate = base + circadian + random_variation + spike
        
        # Clamp values to realistic range
        heart_rate = max(50, min(180, heart_rate))
        
        return round(heart_rate)
    
    def generate_stress_level(self, scenario, heart_rate):
        """Generate stress level correlated with heart rate"""
        config = self.scenarios[scenario]
        base = config["stress_level_base"]
        variance = config["stress_level_variance"]
        
        # Stress correlates with heart rate deviation
        hr_factor = (heart_rate - 70) * 0.3
        
        # Add random variation
        random_variation = random.gauss(0, variance / 2)
        
        stress_level = base + hr_factor + random_variation
        
        # Clamp values to 0-100 range
        stress_level = max(0, min(100, stress_level))
        
        return round(stress_level, 1)
    
    def get_stress_category(self, stress_level):
        """Categorize stress level"""
        if stress_level < 40:
            return "low"
        elif stress_level < 70:
            return "moderate"
        else:
            return "high"
    
    def get_data(self):
        """Generate and return smartwatch data for current scenario"""
        heart_rate = self.generate_heart_rate(self.current_scenario)
        stress_level = self.generate_stress_level(self.current_scenario, heart_rate)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate": heart_rate,
            "stress_level": stress_level,
            "stress_category": self.get_stress_category(stress_level),
            "scenario": self.current_scenario.value,
            "description": self.scenarios[self.current_scenario]["description"]
        }
        
        self.time_offset += 1
        return data
    
    def set_scenario(self, scenario):
        """Change the current scenario"""
        if isinstance(scenario, StressScenario):
            self.current_scenario = scenario
            print(f"🔄 Scenario changed to: {scenario.value.upper()}")
            print(f"   {self.scenarios[scenario]['description']}")
        else:
            print("✗ Invalid scenario")


# Example usage and testing
if __name__ == "__main__":
    simulator = SmartWatchSimulator()
    
    print("="*60)
    print("SmartWatch Simulator - Testing Mode")
    print("="*60)
    print()
    
    # Test all three scenarios
    scenarios = [StressScenario.NORMAL, StressScenario.MODERATE, StressScenario.BAD]
    
    try:
        for scenario in scenarios:
            simulator.set_scenario(scenario)
            print()
            
            # Generate 5 readings for each scenario
            for i in range(5):
                data = simulator.get_data()
                print(f"  HR: {data['heart_rate']:3d} bpm | "
                      f"Stress: {data['stress_level']:5.1f}% ({data['stress_category']:8s}) | "
                      f"Time: {data['timestamp']}")
                time.sleep(1)
            
            print()
            time.sleep(2)
        
        print("="*60)
        print("✓ Testing completed successfully!")
        print("="*60)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulator stopped by user")
