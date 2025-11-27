import time
import threading
from datetime import datetime
from enum import Enum
from sensors import SensorManager
from actuators import ActuatorSystem
import sys
sys.path.append('../simulate')
from simulate import SmartWatchSimulator, StressScenario

class ComfortLevel(Enum):
    COMFORTABLE = "comfortable"
    MODERATE = "moderate"
    UNCOMFORTABLE = "uncomfortable"
    CRITICAL = "critical"

class MainController:
    def __init__(self):
        print("="*70)
        print("🚀 Comfort Sync AI - Initializing Main Controller")
        print("="*70)
        
        # Initialize components
        self.sensors = SensorManager()
        self.actuators = ActuatorSystem()
        self.smartwatch = SmartWatchSimulator()
        
        # Control state
        self.current_comfort_level = ComfortLevel.COMFORTABLE
        self.running = False
        self.update_interval = 2  # seconds
        
        # Thresholds for decision making
        self.thresholds = {
            'temperature': {'min': 20, 'max': 26, 'critical_min': 16, 'critical_max': 30},
            'humidity': {'min': 40, 'max': 60, 'critical_min': 30, 'critical_max': 70},
            'air_quality': {'good': 100, 'moderate': 200, 'bad': 300},
            'stress': {'low': 40, 'moderate': 70, 'high': 85},
            'heart_rate': {'normal': 85, 'elevated': 100, 'high': 115}
        }
        
        # Emotion data from laptop vision
        self.current_emotion = "neutral"
        self.emotion_lock = threading.Lock()
        
        print("✓ Controller initialized successfully\n")
    
    def calculate_discomfort_score(self, sensor_data, watch_data):
        """
        Calculate overall discomfort score based on all sensor data
        Returns score 0-10 and list of issues
        """
        score = 0
        issues = []
        
        # Check temperature
        temp = sensor_data['temperature']
        if temp < self.thresholds['temperature']['critical_min'] or \
           temp > self.thresholds['temperature']['critical_max']:
            score += 3
            issues.append(f"Critical temperature: {temp}°C")
        elif temp < self.thresholds['temperature']['min'] or \
             temp > self.thresholds['temperature']['max']:
            score += 2
            issues.append(f"Uncomfortable temperature: {temp}°C")
        
        # Check humidity
        humidity = sensor_data['humidity']
        if humidity < self.thresholds['humidity']['critical_min'] or \
           humidity > self.thresholds['humidity']['critical_max']:
            score += 2
            issues.append(f"Critical humidity: {humidity}%")
        elif humidity < self.thresholds['humidity']['min'] or \
             humidity > self.thresholds['humidity']['max']:
            score += 1
            issues.append(f"Suboptimal humidity: {humidity}%")
        
        # Check air quality
        air_quality = sensor_data['air_quality']
        if air_quality > self.thresholds['air_quality']['bad']:
            score += 3
            issues.append(f"Poor air quality: {air_quality} PPM")
        elif air_quality > self.thresholds['air_quality']['moderate']:
            score += 1
            issues.append(f"Moderate air quality: {air_quality} PPM")
        
        # Check stress level (most important for comfort)
        stress = watch_data['stress_level']
        if stress > self.thresholds['stress']['high']:
            score += 3
            issues.append(f"Very high stress: {stress}%")
        elif stress > self.thresholds['stress']['moderate']:
            score += 2
            issues.append(f"Elevated stress: {stress}%")
        elif stress > self.thresholds['stress']['low']:
            score += 1
            issues.append(f"Mild stress: {stress}%")
        
        # Check heart rate
        hr = watch_data['heart_rate']
        if hr > self.thresholds['heart_rate']['high']:
            score += 2
            issues.append(f"High heart rate: {hr} bpm")
        elif hr > self.thresholds['heart_rate']['elevated']:
            score += 1
            issues.append(f"Elevated heart rate: {hr} bpm")
        
        # Check emotion (if available)
        if self.current_emotion in ['angry', 'fear', 'sad']:
            score += 2
            issues.append(f"Negative emotion detected: {self.current_emotion}")
        
        return min(score, 10), issues
    
    def determine_comfort_level(self, discomfort_score):
        """Determine comfort level from discomfort score"""
        if discomfort_score >= 7:
            return ComfortLevel.CRITICAL
        elif discomfort_score >= 5:
            return ComfortLevel.UNCOMFORTABLE
        elif discomfort_score >= 3:
            return ComfortLevel.MODERATE
        else:
            return ComfortLevel.COMFORTABLE
    
    def apply_comfort_adjustments(self, comfort_level, sensor_data, watch_data, issues):
        """Apply appropriate adjustments based on comfort level"""
        
        if comfort_level == ComfortLevel.CRITICAL:
            print("\n🔴 CRITICAL DISCOMFORT - Taking immediate action!")
            print(f"   Issues: {', '.join(issues)}")
            
            # Emergency cooling/warming
            if sensor_data['temperature'] > self.thresholds['temperature']['max']:
                self.actuators.set_cabin_lighting('cooling_intense', brightness=255)
                self.actuators.play_sound('calming_deep')
            else:
                self.actuators.set_cabin_lighting('warming', brightness=255)
                self.actuators.play_sound('calming_deep')
        
        elif comfort_level == ComfortLevel.UNCOMFORTABLE:
            print("\n🟠 UNCOMFORTABLE - Applying comfort measures")
            print(f"   Issues: {', '.join(issues)}")
            
            # Strong intervention
            if watch_data['stress_level'] > 70:
                if sensor_data['temperature'] > 25:
                    self.actuators.set_cabin_lighting('cooling', brightness=220)
                else:
                    self.actuators.set_cabin_lighting('calming_blue', brightness=200)
                self.actuators.play_sound('nature_calm')
            else:
                self.actuators.set_cabin_lighting('neutral_warm', brightness=180)
                self.actuators.play_sound('ambient_soft')
        
        elif comfort_level == ComfortLevel.MODERATE:
            print("\n🟡 MODERATE - Minor adjustments")
            print(f"   Issues: {', '.join(issues) if issues else 'Minor discomfort detected'}")
            
            # Gentle adjustments
            if watch_data['stress_level'] > 50:
                self.actuators.set_cabin_lighting('calming_soft', brightness=150)
                self.actuators.play_sound('ambient_soft')
            else:
                self.actuators.set_cabin_lighting('cabin_day', brightness=130)
                self.actuators.stop_sound()
        
        else:  # COMFORTABLE
            print("\n🟢 COMFORTABLE - Maintaining optimal environment")
            self.actuators.set_cabin_lighting('cabin_day', brightness=120)
            self.actuators.stop_sound()
    
    def update_emotion(self, emotion):
        """Update emotion from vision system (called via MQTT or other means)"""
        with self.emotion_lock:
            self.current_emotion = emotion
    
    def control_loop(self):
        """Main control loop"""
        iteration = 0
        
        print("\n" + "="*70)
        print("▶️  Starting Comfort Sync AI Control Loop")
        print("="*70 + "\n")
        
        try:
            while self.running:
                print(f"\n{'─'*70}")
                print(f"📊 Iteration #{iteration + 1} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'─'*70}")
                
                # Gather all sensor data
                sensor_data = self.sensors.read_all()
                watch_data = self.smartwatch.get_data()
                
                # Display sensor readings
                print(f"\n📡 Sensor Readings:")
                print(f"   🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
                print(f"   💧 Humidity: {sensor_data['humidity']:.1f}%")
                print(f"   💨 Air Quality: {sensor_data['air_quality']} PPM")
                print(f"   ⌚ Heart Rate: {watch_data['heart_rate']} bpm")
                print(f"   📊 Stress Level: {watch_data['stress_level']:.1f}%")
                print(f"   😊 Emotion: {self.current_emotion}")
                
                # Calculate discomfort and determine action
                discomfort_score, issues = self.calculate_discomfort_score(sensor_data, watch_data)
                comfort_level = self.determine_comfort_level(discomfort_score)
                
                print(f"\n🎯 Analysis:")
                print(f"   Discomfort Score: {discomfort_score}/10")
                print(f"   Comfort Level: {comfort_level.value.upper()}")
                
                # Apply adjustments if comfort level changed
                if comfort_level != self.current_comfort_level:
                    print(f"   Status Changed: {self.current_comfort_level.value} → {comfort_level.value}")
                    self.current_comfort_level = comfort_level
                
                # Apply comfort adjustments
                self.apply_comfort_adjustments(comfort_level, sensor_data, watch_data, issues)
                
                # Auto-change smartwatch scenario for testing (every 30 iterations)
                if iteration > 0 and iteration % 15 == 0:
                    scenarios = [StressScenario.NORMAL, StressScenario.MODERATE, StressScenario.BAD]
                    current_idx = scenarios.index(self.smartwatch.current_scenario)
                    next_scenario = scenarios[(current_idx + 1) % len(scenarios)]
                    print(f"\n{'='*70}")
                    self.smartwatch.set_scenario(next_scenario)
                    print(f"{'='*70}")
                
                iteration += 1
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Control loop interrupted by user")
        except Exception as e:
            print(f"\n❌ Error in control loop: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the controller"""
        if self.running:
            print("⚠️  Controller already running")
            return
        
        self.running = True
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        
        # Start control loop in separate thread
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()
        
        print("✓ Controller started")
    
    def stop(self):
        """Stop the controller"""
        print("\n🛑 Stopping controller...")
        self.running = False
        
        if hasattr(self, 'control_thread'):
            self.control_thread.join(timeout=5)
        
        self.actuators.cleanup()
        print("✓ Controller stopped")

if __name__ == "__main__":
    controller = MainController()
    controller.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n👋 Goodbye!")
