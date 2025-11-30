import time
import sys
import threading
import json
import paho.mqtt.client as mqtt
sys.path.append('../simulate')
from actuators import ActuatorSystem
from sensors import SensorManager
from data_generator import SmartWatchSimulator, StressScenario

class RealTimeAlertSystem:
    def __init__(self, mqtt_broker="165.246.80.166", mqtt_port=1883):
        print("="*70)
        print("🚨 COMFORT SYNC AI - REAL-TIME DROWSINESS ALERT SYSTEM")
        print("="*70)
        print()
        
        # Initialize hardware
        self.actuators = ActuatorSystem()
        self.sensors = SensorManager()
        self.smartwatch = SmartWatchSimulator()
        
        # MQTT Setup
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = mqtt.Client(client_id="AlertSystem")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_connected = False
        
        # Alert state
        self.alert_active = False
        self.alert_acknowledged = False
        self.current_alert_type = None
        self.drowsiness_data = {
            'blinks': 0,
            'microsleeps': 0.0,
            'yawns': 0,
            'yawn_duration': 0.0,
            'alert': ''
        }
        
        # System state
        self.running = False
        self.normal_mode_active = True
        
        # Connect to MQTT
        self.connect_mqtt()
        
        print("✓ Alert System initialized\n")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.mqtt_connected = True
            print(f"✅ MQTT Connected to broker at {self.mqtt_broker}:{self.mqtt_port}")
            client.subscribe("vision/infer/drowsiness")
            print("   📡 Subscribed to: vision/infer/drowsiness\n")
        else:
            print(f"❌ MQTT Connection failed with code {rc}\n")
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            
            self.drowsiness_data = {
                'blinks': payload.get("blinks", 0),
                'microsleeps': payload.get("microsleeps", 0.0),
                'yawns': payload.get("yawns", 0),
                'yawn_duration': payload.get("yawn_duration", 0.0),
                'alert': payload.get("alert", "")
            }
            
            # Check if alert should be triggered
            alert_type = self.drowsiness_data['alert']
            
            if alert_type in ['prolonged_microsleep'] and not self.alert_active:
                print(f"\n{'='*70}")
                print(f"🚨 DROWSINESS ALERT TRIGGERED: {alert_type.upper()}")
                print(f"{'='*70}")
                self.trigger_alert(alert_type)
            
        except Exception as e:
            print(f"⚠️  MQTT message error: {e}")
    
    def connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"⚠️  Could not connect to MQTT broker: {e}")
            print("   System will run in demo mode without vision data\n")
    
    def start_normal_mode(self):
        """Start normal comfortable driving mode"""
        print("─"*70)
        print("✅ NORMAL DRIVING MODE")
        print("─"*70)
        
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        
        # Stop any previous audio
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        # Set comfortable ocean blue environment
        self.actuators.set_cabin_lighting('ocean_blue', brightness=180)
        self.actuators.play_sound('ocean_waves', volume=35)
        
        print("   💙 Ocean blue ambient lighting")
        print("   🎵 Ambient music playing")
        print("   🚗 Monitoring driver state...\n")
        
        self.normal_mode_active = True
    
    def trigger_alert(self, alert_type):
        """Trigger emergency alert"""
        self.alert_active = True
        self.alert_acknowledged = False
        self.current_alert_type = alert_type
        self.normal_mode_active = False
        
        # Get current sensor data
        sensor_data = self.sensors.read_all()
        watch_data = self.smartwatch.get_data()
        
        print(f"\n   🚨 CRITICAL DROWSINESS DETECTED!")
        print(f"   📊 Drowsiness Stats:")
        print(f"      👁️  Blinks: {self.drowsiness_data['blinks']}")
        print(f"      💤 Microsleeps: {self.drowsiness_data['microsleeps']:.2f} sec")
        print(f"      😮 Yawns: {self.drowsiness_data['yawns']}")
        print(f"      ⏳ Yawn Duration: {self.drowsiness_data['yawn_duration']:.2f} sec")
        
        print(f"\n   📈 Biometric & Environmental Data:")
        print(f"      ❤️  Heart Rate: {watch_data['heart_rate']} bpm")
        print(f"      📊 Stress Level: {watch_data['stress_level']:.1f}%")
        print(f"      🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
        print(f"      💧 Humidity: {sensor_data['humidity']:.0f}%")
        print(f"      💨 Air Quality: {sensor_data['air_quality']} PPM")
        
        print(f"\n   ⚠️  ALERT TYPE: {alert_type.replace('_', ' ').upper()}")
        
        # Stop normal music and activate emergency
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        self.actuators.activate_emergency_protocol()
        
        print("\n   🔴 RED FLASHING LIGHTS → Activated")
        print("   🔊 LOUD ALERT SOUND → Playing (CONTINUOUS)")
        print("   💨 VENTILATION → Maximum")
        print("   ❄️  COOLING → Activated")
        print("   📢 RECOMMENDATION: Pull over safely")
        
        print("\n" + "="*70)
        print("⚠️  ALERT WILL CONTINUE UNTIL ACKNOWLEDGED")
        print("="*70)
        print("\n   🔘 Press ENTER to acknowledge alert and activate anti-fatigue mode")
        print("   ⚠️  Alert will NOT stop automatically...\n")
        
        # Wait for acknowledgment in separate thread
        ack_thread = threading.Thread(target=self.wait_for_acknowledgment, daemon=True)
        ack_thread.start()
    
    def wait_for_acknowledgment(self):
        """Wait for user to acknowledge alert"""
        print("   🚨 Waiting for acknowledgment...", end='')
        sys.stdout.flush()
        
        start_time = time.time()
        input()  # Wait for Enter key
        
        elapsed = int(time.time() - start_time)
        self.alert_acknowledged = True
        
        print(f"\n\n   ✅ Alert acknowledged after {elapsed} seconds!")
        
        # Activate anti-fatigue mode
        self.activate_anti_fatigue_mode()
    
    def activate_anti_fatigue_mode(self):
        """Activate energizing anti-fatigue environment"""
        print("\n" + "─"*70)
        print("✅ ALERT ACKNOWLEDGED - ACTIVATING ANTI-FATIGUE MODE")
        print("─"*70)
        
        print("\n   👍 Driver acknowledged alert")
        print("   🅿️  Vehicle should pull over safely")
        print("   ⚡ Activating energizing environment to combat fatigue...\n")
        
        time.sleep(1)
        
        # Stop emergency
        self.actuators.emergency_active = False
        self.actuators.stop_sound()
        time.sleep(0.5)
        
        # ENERGIZING MODE - Bright yellow + Rock/Energizing music
        self.actuators.set_cabin_lighting('energizing_yellow', brightness=220)
        self.actuators.play_sound('rock', volume=60)
        
        print("   ⚡ ANTI-FATIGUE MODE ACTIVATED")
        print("   ═" * 35)
        print("\n   🌟 Bright energizing yellow lighting (220 brightness)")
        print("   🎸 Energizing music playing (loud)")
        print("   ❄️  Cool air circulation activated")
        print("   💨 Fresh air ventilation (maximum)")
        print("   ☕ Recommended: Take a 15-minute break")
        
        print("\n   💡 FATIGUE REDUCTION TIPS:")
        print("      • Stretch your legs and arms")
        print("      • Drink cold water or coffee")
        print("      • Walk around for 5-10 minutes")
        print("      • Deep breathing exercises")
        print("      • Wash face with cold water")
        
        print("\n   🎸 Energizing music will continue playing...")
        print("   ⌨️  System will return to normal mode automatically\n")
        
        # Reset alert state after acknowledgment
        self.alert_active = False
        self.current_alert_type = None
        
        # Keep anti-fatigue mode for 30 seconds before returning to normal
        time.sleep(30)
        
        if not self.alert_active:  # If no new alert triggered
            print("\n   🔄 Returning to normal mode...\n")
            self.start_normal_mode()
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        iteration = 0
        
        print("▶️  Starting Real-Time Monitoring")
        print("="*70 + "\n")
        
        try:
            while self.running:
                if self.normal_mode_active and not self.alert_active:
                    # Normal monitoring
                    sensor_data = self.sensors.read_all()
                    watch_data = self.smartwatch.get_data()
                    
                    if iteration % 5 == 0:  # Print status every 10 seconds
                        print(f"📊 Monitoring Status (Iteration {iteration + 1})")
                        print(f"   🌡️  Temp: {sensor_data['temperature']:.1f}°C | "
                              f"💧 Humidity: {sensor_data['humidity']:.0f}% | "
                              f"💨 Air: {sensor_data['air_quality']} PPM")
                        print(f"   ❤️  Heart Rate: {watch_data['heart_rate']} bpm | "
                              f"📊 Stress: {watch_data['stress_level']:.1f}%")
                        
                        if self.mqtt_connected:
                            print(f"   👁️  Blinks: {self.drowsiness_data['blinks']} | "
                                  f"💤 Microsleeps: {self.drowsiness_data['microsleeps']:.1f}s | "
                                  f"😮 Yawns: {self.drowsiness_data['yawns']}")
                        
                        print(f"   ✅ Status: Normal\n")
                
                iteration += 1
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  System stopped by user")
    
    def start(self):
        """Start the alert system"""
        if self.running:
            print("⚠️  System already running")
            return
        
        self.running = True
        
        # Start in normal mode
        self.start_normal_mode()
        
        # Start monitoring loop in separate thread
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✓ Alert System started\n")
    
    def stop(self):
        """Stop the alert system"""
        print("\n🛑 Stopping alert system...")
        self.running = False
        self.alert_active = False
        self.actuators.emergency_active = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        
        # Stop MQTT
        if self.mqtt_connected:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.actuators.cleanup()
        print("✓ Alert System stopped")


if __name__ == "__main__":
    print("\n🎬 Starting Real-Time Drowsiness Alert System...")
    print("   Waiting for drowsiness detection data from vision system")
    print("   Press Ctrl+C to stop at any time\n")
    time.sleep(2)
    
    try:
        alert_system = RealTimeAlertSystem()
        alert_system.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  System stopped by user")
        alert_system.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        alert_system.stop()