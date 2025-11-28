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
        
    def wait_for_acknowledgment(self):
        """Wait for Enter key to acknowledge alert"""
        print("\n🔴 [ALERT] Press ENTER to acknowledge and stop alarm\n")
        start_time = time.time()
        input()
        elapsed = int(time.time() - start_time)
        print(f"✅ [ACKNOWLEDGED] Alert stopped after {elapsed}s\n")
        return True
    
    def run_demo(self):
        """Run drowsiness alert demonstration"""
        print("="*70)
        print("🚗 COMFORT SYNC AI - DROWSINESS DETECTION SYSTEM")
        print("="*70)
        print()
        
        # Phase 1: Normal Monitoring (10 seconds)
        print("📊 PHASE 1: NORMAL MONITORING\n")
        
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        self.actuators.set_cabin_lighting('ocean_blue', brightness=180)
        self.actuators.play_sound('uplifting_ambient', volume=40)
        
        print("💙 Environment: Ocean Blue Lighting + Ambient Music")
        print("✅ Status: Normal Operation\n")
        
        # Monitor for 10 seconds
        for i in range(5):
            sensor_data = self.sensors.read_all()
            watch_data = self.smartwatch.get_data()
            
            print(f"[{i+1}/5] 🌡️  {sensor_data['temperature']:.1f}°C | "
                  f"💧 {sensor_data['humidity']:.0f}% | "
                  f"💨 {sensor_data['air_quality']} PPM")
            print(f"      ❤️  {watch_data['heart_rate']} bpm | "
                  f"📊 Stress: {watch_data['stress_level']:.0f}% | "
                  f"😊 Normal")
            print()
            
            time.sleep(2)
        
        # Phase 2: Drowsiness Detection
        print("─"*70)
        print("⚠️  PHASE 2: DROWSINESS DETECTED\n")
        
        print("🚨 Critical Readings:")
        print("  • ❤️  Heart Rate: 55 bpm (LOW)")
        print("  • 📉 Stress Level: 15% (DROWSY)")
        print("  • 🌡️  Temperature: 27°C (WARM)")
        print("  • 🕐 Time: 02:30 AM (HIGH RISK)\n")
        
        time.sleep(2)
        
        # Phase 3: Emergency Alert
        print("="*70)
        print("🚨 EMERGENCY ALERT ACTIVATED 🚨")
        print("="*70)
        print()
        
        self.actuators.stop_sound()
        time.sleep(0.3)
        
        self.actuators.activate_emergency_protocol()
        
        print("⚠️  Alert Status:")
        print("  • 🔴 Red Flashing Lights: ACTIVE")
        print("  • 🔊 Alert Sound: CONTINUOUS")
        print("  • 💨 Ventilation: MAXIMUM")
        print("  • ❄️  Cooling: ACTIVATED\n")
        
        # Wait for acknowledgment
        self.wait_for_acknowledgment()
        
        # Phase 4: Anti-Fatigue Recovery Mode
        print("─"*70)
        print("⚡ PHASE 3: ANTI-FATIGUE RECOVERY MODE\n")
        
        self.actuators.emergency_active = False
        self.actuators.stop_sound()
        time.sleep(0.5)
        
        # Energizing environment with rock music
        self.actuators.set_cabin_lighting('energizing_yellow', brightness=220)
        self.actuators.play_sound('rock', volume=60)
        
        print("🌟 Environment: Bright Yellow Lighting + Rock Music")
        print("🎯 Target: Combat Fatigue & Restore Alertness")
        print()
        print("💡 Recovery Recommendations:")
        print("  • 🧘 Stretch and move around")
        print("  • 💧 Drink cold water")
        print("  • 🫁 Take deep breaths")
        print("  • ⏰ 15-minute energizing break")
        print()
        print("🎸 [INFO] Rock music playing continuously...")
        print("⌨️  [INFO] Press Ctrl+C to stop when ready\n")
        
        # Keep playing until user stops
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 [STOPPED] User interrupted")
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETE")
        print("="*70)
        print()
        
        # Cleanup
        self.actuators.stop_sound()
        time.sleep(0.3)
        self.actuators.cleanup()

if __name__ == "__main__":
    print("\n🎬 Starting in 3 seconds...\n")
    time.sleep(3)
    
    try:
        demo = AlertSystemDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n🛑 [STOPPED] Demo interrupted")
        demo = AlertSystemDemo()
        demo.actuators.emergency_active = False
        demo.actuators.stop_sound()
        demo.actuators.cleanup()
    except Exception as e:
        print(f"\n❌ [ERROR] {e}")
        import traceback
        traceback.print_exc()