import time
import sys
sys.path.append('../simulate')
from actuators import ActuatorSystem
from sensors import SensorManager
from data_generator import SmartWatchSimulator, StressScenario

class AlertSystemDemo:
    def __init__(self):
        self.actuators = ActuatorSystem()
        self.sensors = SensorManager()
        self.smartwatch = SmartWatchSimulator()
        self.current_emotion = "neutral"
        
    def get_emotion_from_stress(self, stress_level):
        """Determine emotion based on stress level"""
        if stress_level > 70:
            return "😰 Fear/Anxious"
        elif stress_level > 50:
            return "😟 Stressed"
        elif stress_level > 30:
            return "😐 Neutral"
        elif stress_level < 20:
            return "😴 Drowsy"
        else:
            return "😊 Happy"
        
    def wait_for_acknowledgment(self):
        """Wait for user to press Enter to acknowledge alert"""
        print("\n" + "="*70)
        print("⚠️  ALERT WILL CONTINUE UNTIL ACKNOWLEDGED")
        print("="*70)
        print("\n   🔘 Press ENTER to acknowledge alert and stop alarm")
        print("   ⚠️  Alert will NOT stop automatically...\n")
        
        start_time = time.time()
        
        # Show alert status while waiting
        print("   🚨 Waiting for acknowledgment...", end='')
        sys.stdout.flush()
        
        # Wait for Enter key
        input()
        
        elapsed = int(time.time() - start_time)
        print(f"\n\n   ✅ Alert acknowledged after {elapsed} seconds!")
        return True
    
    def run_demo(self):
        """Run realistic alert system demonstration with drowsiness detection"""
        print("="*70)
        print("🚨 COMFORT SYNC AI - DROWSINESS ALERT DEMO")
        print("="*70)
        print("\nSimulating real-time cabin monitoring")
        print("Monitoring: Heart Rate, Stress, Temperature, Humidity, Air Quality, Emotion")
        print("\n")
        
        # Phase 1: Normal Driving (10 seconds - 5 readings at 2s intervals)
        print("─"*70)
        print("✅ NORMAL DRIVING MODE")
        print("─"*70)
        
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        
        # Stop any previous music
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        self.actuators.set_cabin_lighting('ocean_blue', brightness=180)
        self.actuators.play_sound('uplifting_ambient', volume=40)
        
        print("   💙 Ocean blue ambient lighting")
        print("   🎵 Uplifting ambient music playing")
        print("   🚗 Driver alert and comfortable\n")
        
        # Show normal readings for 5 iterations (10 seconds total)
        for i in range(5):
            sensor_data = self.sensors.read_all()
            watch_data = self.smartwatch.get_data()
            emotion = self.get_emotion_from_stress(watch_data['stress_level'])
            
            print(f"   [{i+1}/5] Monitoring...")
            print(f"      🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
            print(f"      💧 Humidity: {sensor_data['humidity']:.0f}%")
            print(f"      💨 Air Quality: {sensor_data['air_quality']} PPM")
            print(f"      ❤️  Heart Rate: {watch_data['heart_rate']} bpm")
            print(f"      📊 Stress: {watch_data['stress_level']:.1f}%")
            print(f"      {emotion}")
            print(f"      ✅ Status: Normal\n")
            
            time.sleep(2)
        
        # Phase 2: Detecting Drowsiness (Transition)
        print("\n" + "─"*70)
        print("⚠️  DROWSINESS DETECTED!")
        print("─"*70)
        
        # Simulate drowsiness scenario
        print("\n   📉 Heart rate dropping...")
        print("   😴 Reduced alertness detected")
        print("   🔍 Analyzing driver state...")
        time.sleep(2)
        
        # Show critical readings
        print("\n   🚨 CRITICAL READINGS:")
        print("      ❤️  Heart Rate: 55 bpm (TOO LOW)")
        print("      📊 Stress: 15% (DROWSY STATE)")
        print("      🌡️  Temperature: 27°C (TOO WARM)")
        print("      💧 Humidity: 65% (HIGH)")
        print("      💨 Air Quality: 280 PPM (POOR)")
        print("      😴 Emotion: Drowsy")
        print("      ⏰ Time: 02:30 AM (HIGH RISK HOUR)")
        
        time.sleep(2)
        
        # Phase 3: EMERGENCY ALERT ACTIVATION (Continues until Enter pressed)
        print("\n" + "="*70)
        print("🚨🚨🚨 EMERGENCY ALERT ACTIVATED! 🚨🚨🚨")
        print("="*70)
        print("\n   ⚠️  DROWSINESS ALERT: DRIVER ATTENTION REQUIRED")
        print("   ⚠️  PULLING OVER RECOMMENDED")
        print("   ⚠️  EMERGENCY PROTOCOL INITIATED")
        
        # Stop music and activate emergency
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        self.actuators.activate_emergency_protocol()
        
        print("\n   🔴 RED FLASHING LIGHTS → Activated")
        print("   🔊 ALERT SOUND → Playing (CONTINUOUS)")
        print("   💨 VENTILATION → Maximum")
        print("   ❄️  COOLING → Activated")
        print("   📢 VOICE ALERT → 'Please pull over safely'")
        
        # Wait for user to press Enter (alert continues)
        self.wait_for_acknowledgment()
        
        # Phase 4: Alert Acknowledged - Anti-Fatigue Mode with Rock Music
        print("\n" + "─"*70)
        print("✅ ALERT ACKNOWLEDGED - ACTIVATING ANTI-FATIGUE MODE")
        print("─"*70)
        
        print("\n   👍 Driver acknowledged alert")
        print("   🅿️  Vehicle pulled over safely")
        print("   ⚡ Activating energizing environment to combat fatigue...\n")
        
        time.sleep(1)
        
        # Stop emergency and activate ENERGIZING environment
        self.actuators.emergency_active = False
        self.actuators.stop_sound()
        time.sleep(0.5)
        
        # ENERGIZING MODE - Bright yellow light + ROCK MUSIC
        self.actuators.set_cabin_lighting('energizing_yellow', brightness=220)
        self.actuators.play_sound('rock', volume=60)
        
        print("   ⚡ ANTI-FATIGUE MODE ACTIVATED")
        print("   ═" * 35)
        print("\n   🌟 Bright energizing yellow lighting (220 brightness)")
        print("   🎸 ROCK MUSIC playing (energizing)")
        print("   ❄️  Cool air circulation (18°C target)")
        print("   💨 Fresh air ventilation (maximum)")
        print("   ☕ Recommended: Take a 15-minute energizing break")
        
        print("\n   💡 FATIGUE REDUCTION TIPS:")
        print("      • Stretch your legs and arms")
        print("      • Drink cold water")
        print("      • Walk around for 5 minutes")
        print("      • Deep breathing exercises")
        print("      • Face washing with cold water")
        
        print("\n   🎸 Rock music will play continuously...")
        print("   ⌨️  Press Ctrl+C to stop when ready\n")
        
        # Keep rock music playing continuously until user stops
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n   🛑 User stopped the demo")
        
        print("\n" + "="*70)
        print("✅ DROWSINESS ALERT DEMO COMPLETE!")
        print("="*70)
        print("\n📊 Summary:")
        print("   ✓ Normal monitoring (10s): Ocean blue + Ambient music")
        print("   ✓ Drowsiness detected: Low heart rate, high humidity, drowsy emotion")
        print("   ✓ Emergency alert: Red flashing + Loud alarm (until Enter pressed)")
        print("   ✓ Anti-fatigue mode: Bright yellow + Rock music (continuous)")
        
        print("\n💡 System Features Demonstrated:")
        print("   • Real-time biometric monitoring")
        print("   • Environmental monitoring (temp, humidity, air quality)")
        print("   • Emotion detection from stress levels")
        print("   • Automatic drowsiness detection")
        print("   • Continuous alert until acknowledgment")
        print("   • Keyboard-controlled alert stop (Enter key)")
        print("   • Rock music for active fatigue recovery")
        
        print("\n👋 Demo finished. Cleaning up...\n")
        
        # Final cleanup
        self.actuators.stop_sound()
        time.sleep(0.3)
        self.actuators.cleanup()

if __name__ == "__main__":
    print("\n🎬 Starting Drowsiness Alert Demo in 3 seconds...")
    print("   Press Ctrl+C to stop at any time\n")
    time.sleep(3)
    
    try:
        demo = AlertSystemDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo stopped by user")
        demo = AlertSystemDemo()
        demo.actuators.emergency_active = False
        demo.actuators.stop_sound()
        demo.actuators.cleanup()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()