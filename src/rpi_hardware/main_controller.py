import time
import threading
from datetime import datetime
from enum import Enum
import json
import paho.mqtt.client as mqtt
from sensors import SensorManager
from actuators import ActuatorSystem
import sys
sys.path.append('../simulate')
from data_generator import SmartWatchSimulator, StressScenario
from decision_model import EnvironmentDecisionModel
from personalization_model import PersonalizationModel

class ComfortLevel(Enum):
    COMFORTABLE = "comfortable"
    MODERATE = "moderate"
    UNCOMFORTABLE = "uncomfortable"
    CRITICAL = "critical"

class MainController:
    def __init__(self, mqtt_broker="127.0.0.1", mqtt_port=1883, user_id="user_default"):
        print("="*70)
        print("🚀 Comfort Sync AI - Initializing Main Controller")
        print("="*70)
        
        # Initialize components
        self.sensors = SensorManager()
        self.actuators = ActuatorSystem()
        self.smartwatch = SmartWatchSimulator()
        
        # MQTT Setup for emotion detection - Match your working code
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_connected = False
        
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
        self.last_emotion_time = time.time()
        
        # Emotion to lighting mapping
        self.emotion_lighting = {
            'happy': {'color': 'cabin_evening', 'brightness': 180, 'description': 'Warm and welcoming'},
            'neutral': {'color': 'cabin_day', 'brightness': 130, 'description': 'Comfortable neutral'},
            'sad': {'color': 'warming_intense', 'brightness': 200, 'description': 'Warm comforting glow'},
            'angry': {'color': 'cooling_intense', 'brightness': 180, 'description': 'Cool calming blue'},
            'fear': {'color': 'calming_soft', 'brightness': 220, 'description': 'Soft reassuring light'},
            'surprise': {'color': 'neutral_warm', 'brightness': 160, 'description': 'Gentle neutral'},
            'disgust': {'color': 'nature_green', 'brightness': 150, 'description': 'Fresh natural green'},
        }
        
        # Decision model for environment control
        self.decision_model = EnvironmentDecisionModel(window_seconds=20)
        
        # Personalization model
        self.personalization = PersonalizationModel(user_id=user_id)
        self.use_personalization = True  # Toggle between generic and personalized
        
        # Track previous comfort level for learning
        self.previous_comfort_score = 50
        
        # Try to connect to MQTT
        self.connect_mqtt()
        
        print("✓ Controller initialized successfully\n")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.mqtt_connected = True
            print(f"✅ Connected successfully to Mosquitto Broker at {self.mqtt_broker}:{self.mqtt_port}")
            # Subscribe to the topic the PC is publishing to
            client.subscribe("vision/infer/mood")
            print(f"   📡 Subscribed to topic: vision/infer/mood")
        else:
            print(f"❌ Connection failed with code {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            # Decode the JSON payload
            payload = json.loads(msg.payload.decode())
            
            emotion = payload.get("emotion")
            timestamp = payload.get("ts")
            
            with self.emotion_lock:
                self.current_emotion = emotion
                self.last_emotion_time = time.time()
            
            print(f"\n   😊 NEW EMOTION DETECTED: {emotion}")
            
        except json.JSONDecodeError:
            print(f"   ⚠️  Error decoding JSON payload: {msg.payload}")
        except Exception as e:
            print(f"   ⚠️  MQTT message error: {e}")
    
    def connect_mqtt(self):
        """Connect to MQTT broker for emotion data"""
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            # Start the loop in background thread
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"⚠️  Could not start MQTT subscriber: {e}")
            print("   Controller will run without emotion detection")
    
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
    
    def get_emotion_based_lighting(self):
        """Get lighting settings based on current emotion"""
        with self.emotion_lock:
            emotion = self.current_emotion
            # Check if emotion data is recent (within last 10 seconds)
            if time.time() - self.last_emotion_time > 10:
                emotion = "neutral"
        
        return self.emotion_lighting.get(emotion, self.emotion_lighting['neutral'])
    
    def apply_comfort_adjustments(self, comfort_level, sensor_data, watch_data, issues):
        """Apply appropriate adjustments based on comfort level AND emotion"""
        
        # Get emotion-based lighting preference
        emotion_light = self.get_emotion_based_lighting()
        
        if comfort_level == ComfortLevel.CRITICAL:
            print("\n🔴 CRITICAL DISCOMFORT - Taking immediate action!")
            print(f"   Issues: {', '.join(issues)}")
            print(f"   Emotion: {self.current_emotion} → Using emergency protocol")
            
            # Critical situations override emotion
            if sensor_data['temperature'] > self.thresholds['temperature']['max']:
                self.actuators.set_cabin_lighting('cooling_intense', brightness=255)
            else:
                self.actuators.set_cabin_lighting('warming_intense', brightness=255)
            
            self.actuators.play_sound('calming_deep', volume=70)
        
        elif comfort_level == ComfortLevel.UNCOMFORTABLE:
            print("\n🟠 UNCOMFORTABLE - Applying comfort measures")
            print(f"   Issues: {', '.join(issues)}")
            print(f"   Emotion: {self.current_emotion} → {emotion_light['description']}")
            
            # Strong intervention with emotion consideration
            if watch_data['stress_level'] > 70:
                # High stress + negative emotion = strong calming
                if self.current_emotion in ['angry', 'fear', 'sad']:
                    self.actuators.set_cabin_lighting('calming_blue', brightness=220)
                    self.actuators.play_sound('nature_calm', volume=60)
                else:
                    self.actuators.set_cabin_lighting('cooling', brightness=200)
                    self.actuators.play_sound('ambient_soft', volume=50)
            else:
                # Use emotion-based lighting
                self.actuators.set_cabin_lighting(emotion_light['color'], brightness=emotion_light['brightness'])
                self.actuators.play_sound('ambient_soft', volume=40)
        
        elif comfort_level == ComfortLevel.MODERATE:
            print("\n🟡 MODERATE - Minor adjustments")
            print(f"   Issues: {', '.join(issues) if issues else 'Minor discomfort detected'}")
            print(f"   Emotion: {self.current_emotion} → {emotion_light['description']}")
            
            # Gentle adjustments based on emotion
            if watch_data['stress_level'] > 50:
                if self.current_emotion == 'angry':
                    self.actuators.set_cabin_lighting('cooling', brightness=160)
                    self.actuators.play_sound('ambient_soft', volume=35)
                elif self.current_emotion in ['sad', 'fear']:
                    self.actuators.set_cabin_lighting('warming', brightness=180)
                    self.actuators.play_sound('ambient_soft', volume=30)
                else:
                    self.actuators.set_cabin_lighting('calming_soft', brightness=150)
                    self.actuators.play_sound('ambient_soft', volume=25)
            else:
                # Use emotion-based lighting
                self.actuators.set_cabin_lighting(emotion_light['color'], brightness=emotion_light['brightness'])
                self.actuators.stop_sound()
        
        else:  # COMFORTABLE
            print("\n🟢 COMFORTABLE - Maintaining optimal environment")
            print(f"   Emotion: {self.current_emotion} → {emotion_light['description']}")
            
            # Use emotion-based lighting for comfortable state
            self.actuators.set_cabin_lighting(emotion_light['color'], brightness=emotion_light['brightness'])
            self.actuators.stop_sound()
    
    def control_loop(self):
        """Main control loop"""
        iteration = 0
        
        print("\n" + "="*70)
        print("▶️  Starting Comfort Sync AI Control Loop")
        print(f"   Personalization: {'ENABLED' if self.use_personalization else 'DISABLED'}")
        print("="*70 + "\n")
        
        try:
            while self.running:
                print(f"\n{'─'*70}")
                print(f"📊 Iteration #{iteration + 1} | {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'─'*70}")
                
                # Gather all sensor data
                sensor_data = self.sensors.read_all()
                watch_data = self.smartwatch.get_data()
                
                # Add data to decision model
                self.decision_model.add_data_point(sensor_data, watch_data, self.current_emotion)
                
                # Calculate comfort score
                comfort_score = self.personalization.get_comfort_score(sensor_data, watch_data)
                comfort_improved = comfort_score > self.previous_comfort_score
                
                # Display sensor readings
                print(f"\n📡 Sensor Readings:")
                print(f"   🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
                print(f"   💧 Humidity: {sensor_data['humidity']:.1f}%")
                print(f"   💨 Air Quality: {sensor_data['air_quality']} PPM")
                print(f"   ⌚ Heart Rate: {watch_data['heart_rate']} bpm")
                print(f"   📊 Stress Level: {watch_data['stress_level']:.1f}%")
                print(f"   😊 Emotion: {self.current_emotion}")
                
                # Make environment decision (only once every 20 seconds)
                decision = self.decision_model.make_decision()
                
                if decision:
                    # Choose between generic and personalized decision
                    if self.use_personalization:
                        personalized_env = self.personalization.get_personalized_environment(
                            self.current_emotion, 
                            sensor_data, 
                            watch_data
                        )
                        
                        print(f"\nPERSONALIZED ENVIRONMENT DECISION (based on last 20 seconds):")
                        print(f"   {personalized_env['description']}")
                        print(f"   Emotion: {self.current_emotion}")
                        print(f"   Comfort Score: {comfort_score:.0f}/100")
                        print(f"   Color: {personalized_env['color']}")
                        print(f"   Audio: {personalized_env['audio']}")
                        
                        # Record feedback about previous environment
                        if iteration > 0:
                            prev_env = self.decision_model.get_current_environment()
                            self.personalization.record_feedback(
                                prev_env, 
                                sensor_data, 
                                watch_data, 
                                self.current_emotion,
                                comfort_improved
                            )
                        
                        # Apply personalized environment
                        self.actuators.set_cabin_lighting(
                            personalized_env['color'], 
                            brightness=personalized_env['brightness']
                        )
                        self.actuators.play_sound(personalized_env['audio'], volume=personalized_env['volume'])
                        
                    else:
                        # Use generic decision model
                        print(f"\nNEW ENVIRONMENT DECISION (based on last 20 seconds):")
                        print(f"   Decision: {decision['description']}")
                        print(f"   Dominant Emotion: {decision['analytics']['dominant_emotion']}")
                        print(f"   Avg Stress: {decision['analytics']['avg_stress']:.1f}%")
                        print(f"   Avg Heart Rate: {decision['analytics']['avg_heart_rate']:.0f} bpm")
                        print(f"   Avg Temperature: {decision['analytics']['avg_temp']:.1f}°C")
                        
                        # Apply the decision
                        self.actuators.set_cabin_lighting(
                            decision['color_scheme'], 
                            brightness=decision['brightness']
                        )
                        self.actuators.play_sound(decision['audio'], volume=decision['volume'])
                
                else:
                    # Show current environment
                    current_env = self.decision_model.get_current_environment()
                    print(f"\n🔄 Current Environment: {current_env['description']}")
                    print(f"   🎵 Playing: {current_env.get('audio', 'N/A')}")
                    print(f"   💯 Comfort Score: {comfort_score:.0f}/100")
                
                # Learn from session every 10 decisions (every ~200 seconds)
                if iteration > 0 and iteration % 100 == 0 and self.use_personalization:
                    self.personalization.learn_from_session()
                
                # Update previous comfort score
                self.previous_comfort_score = comfort_score
                
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
            # Save learning before exit
            if self.use_personalization and self.personalization.session_data:
                print("💾 Saving session learning...")
                self.personalization.learn_from_session()
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
        
        # Set default environment immediately
        print("\n🎨 Setting default calming environment...")
        default_env = self.decision_model.get_current_environment()
        self.actuators.set_cabin_lighting(
            default_env['color_scheme'], 
            brightness=default_env['brightness']
        )
        self.actuators.play_sound(default_env['audio'], volume=default_env['volume'])
        print(f"   {default_env['description']}")
        
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
        
        # Stop MQTT
        if self.mqtt_connected:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.actuators.cleanup()
        print("✓ Controller stopped")

if __name__ == "__main__":
    # You can specify user_id for personalization
    controller = MainController(user_id="shohruh_demo")
    controller.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n👋 Goodbye!")
