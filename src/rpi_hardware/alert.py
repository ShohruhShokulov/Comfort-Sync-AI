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
        
        # Alert thresholds
        self.critical_thresholds = {
            'stress_level': 85,
            'heart_rate': 120,
            'temperature_high': 30,
            'temperature_low': 16,
            'air_quality': 350
        }
        
    def check_critical_condition(self, sensor_data, watch_data):
        """Check if any critical condition is met"""
        critical_issues = []
        
        # Check stress
        if watch_data['stress_level'] > self.critical_thresholds['stress_level']:
            critical_issues.append(f"CRITICAL STRESS: {watch_data['stress_level']:.0f}%")
        
        # Check heart rate
        if watch_data['heart_rate'] > self.critical_thresholds['heart_rate']:
            critical_issues.append(f"CRITICAL HEART RATE: {watch_data['heart_rate']} bpm")
        
        # Check temperature
        if sensor_data['temperature'] > self.critical_thresholds['temperature_high']:
            critical_issues.append(f"CRITICAL HIGH TEMP: {sensor_data['temperature']:.1f}°C")
        elif sensor_data['temperature'] < self.critical_thresholds['temperature_low']:
            critical_issues.append(f"CRITICAL LOW TEMP: {sensor_data['temperature']:.1f}°C")
        
        # Check air quality
        if sensor_data['air_quality'] > self.critical_thresholds['air_quality']:
            critical_issues.append(f"CRITICAL AIR QUALITY: {sensor_data['air_quality']} PPM")
        
        return critical_issues
    
    def activate_alert(self, issues):
        """Activate emergency alert protocol"""
        print("\n" + "="*70)
        print("🚨 EMERGENCY ALERT ACTIVATED! 🚨")
        print("="*70)
        
        for issue in issues:
            print(f"   ⚠️  {issue}")
        
        # Activate emergency protocol
        self.actuators.activate_emergency_protocol()
        print("\n   🔴 Red flashing lights activated")
        print("   🔊 Alert sound playing")
        print("   💨 Emergency ventilation (simulated)")
        
    def run_demo(self):
        """Run the alert system demonstration"""
        print("="*70)
        print("🚨 COMFORT SYNC AI - ALERT SYSTEM DEMONSTRATION")
        print("="*70)
        print("\nThis demo shows how the system responds to critical situations")
        print("Duration: 20 seconds per scenario\n")
        
        # Scenario 1: Normal conditions (5 seconds)
        print("\n" + "─"*70)
        print("📊 SCENARIO 1: Normal Conditions (5 seconds)")
        print("─"*70)
        
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        self.actuators.set_cabin_lighting('cabin_day', brightness=150)
        self.actuators.play_sound('ambient_soft', volume=30)
        
        for i in range(3):
            sensor_data = self.sensors.read_all()
            watch_data = self.smartwatch.get_data()
            
            print(f"\n   Reading {i+1}/3:")
            print(f"   🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
            print(f"   💧 Humidity: {sensor_data['humidity']:.1f}%")
            print(f"   💨 Air Quality: {sensor_data['air_quality']} PPM")
            print(f"   ⌚ Heart Rate: {watch_data['heart_rate']} bpm")
            print(f"   📊 Stress Level: {watch_data['stress_level']:.1f}%")
            print("   ✅ All systems normal")
            
            time.sleep(1.5)
        
        # Scenario 2: Critical stress situation (10 seconds)
        print("\n" + "─"*70)
        print("📊 SCENARIO 2: CRITICAL STRESS SITUATION (10 seconds)")
        print("─"*70)
        print("⚠️  Simulating: High stress + elevated heart rate\n")
        
        self.smartwatch.set_scenario(StressScenario.CRITICAL)
        time.sleep(1)
        
        alert_activated = False
        for i in range(5):
            sensor_data = self.sensors.read_all()
            watch_data = self.smartwatch.get_data()
            
            print(f"\n   Reading {i+1}/5:")
            print(f"   🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
            print(f"   💧 Humidity: {sensor_data['humidity']:.1f}%")
            print(f"   💨 Air Quality: {sensor_data['air_quality']} PPM")
            print(f"   ⌚ Heart Rate: {watch_data['heart_rate']} bpm")
            print(f"   📊 Stress Level: {watch_data['stress_level']:.1f}%")
            
            # Check for critical conditions
            critical_issues = self.check_critical_condition(sensor_data, watch_data)
            
            if critical_issues and not alert_activated:
                self.activate_alert(critical_issues)
                alert_activated = True
            elif critical_issues:
                print("   🚨 Alert continuing...")
            
            time.sleep(2)
        
        # Scenario 3: Recovery (5 seconds)
        print("\n" + "─"*70)
        print("📊 SCENARIO 3: RECOVERY (5 seconds)")
        print("─"*70)
        print("✅ Returning to normal conditions\n")
        
        # Stop emergency protocol
        self.actuators.emergency_active = False
        self.actuators.stop_sound()
        
        self.smartwatch.set_scenario(StressScenario.NORMAL)
        self.actuators.set_cabin_lighting('calming_soft', brightness=180)
        self.actuators.play_sound('meditation_calm', volume=50)
        
        for i in range(3):
            sensor_data = self.sensors.read_all()
            watch_data = self.smartwatch.get_data()
            
            print(f"\n   Reading {i+1}/3:")
            print(f"   🌡️  Temperature: {sensor_data['temperature']:.1f}°C")
            print(f"   💧 Humidity: {sensor_data['humidity']:.1f}%")
            print(f"   💨 Air Quality: {sensor_data['air_quality']} PPM")
            print(f"   ⌚ Heart Rate: {watch_data['heart_rate']} bpm")
            print(f"   📊 Stress Level: {watch_data['stress_level']:.1f}%")
            print("   💜 Calming environment activated")
            print("   ✅ Stress levels normalizing")
            
            time.sleep(1.5)
        
        # Demo complete
        print("\n" + "="*70)
        print("✅ ALERT SYSTEM DEMO COMPLETE!")
        print("="*70)
        print("\nSummary:")
        print("   ✓ Normal operation: Green ambient lighting")
        print("   ✓ Critical alert: Red flashing + alarm sound")
        print("   ✓ Recovery: Calming purple + meditation music")
        print("\n👋 Demo finished. Cleaning up...\n")
        
        # Cleanup
        self.actuators.cleanup()

if __name__ == "__main__":
    print("\n🎬 Starting Alert System Demo in 3 seconds...")
    print("   Press Ctrl+C to stop at any time\n")
    time.sleep(3)
    
    try:
        demo = AlertSystemDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        demo.actuators.cleanup()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()