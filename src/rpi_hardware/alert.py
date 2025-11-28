import time
import sys
sys.path.append('../simulate')
from actuators import ActuatorSystem

class AlertSystemDemo:
    def __init__(self):
        self.actuators = ActuatorSystem()
        
    def run_demo(self):
        """Run the alert system demonstration"""
        print("="*70)
        print("🚨 COMFORT SYNC AI - ALERT SYSTEM DEMO")
        print("="*70)
        print("\nShowing environment change from normal to alert mode")
        print("Duration: 20 seconds total\n")
        
        # Phase 1: Normal Environment (10 seconds)
        print("─"*70)
        print("✅ NORMAL MODE - Ocean Blue + Uplifting Music")
        print("─"*70)
        
        self.actuators.set_cabin_lighting('ocean_blue', brightness=180)
        self.actuators.play_sound('uplifting_ambient', volume=40)
        
        print("   💙 Ocean blue lighting activated")
        print("   🎵 Uplifting ambient music playing")
        print("\n   Waiting 10 seconds...\n")
        
        for i in range(10, 0, -1):
            print(f"   ⏱️  {i} seconds remaining...", end='\r')
            time.sleep(1)
        
        print("\n")
        
        # Phase 2: ALERT MODE (10 seconds)
        print("─"*70)
        print("🚨 ALERT MODE ACTIVATED!")
        print("─"*70)
        
        self.actuators.activate_emergency_protocol()
        
        print("   🔴 RED FLASHING LIGHTS activated")
        print("   🔊 ALERT SOUND playing")
        print("   ⚠️  EMERGENCY PROTOCOL ACTIVE")
        print("\n   Alert will run for 10 seconds...\n")
        
        for i in range(10, 0, -1):
            print(f"   🚨 ALERT ACTIVE - {i} seconds remaining...", end='\r')
            time.sleep(1)
        
        print("\n")
        
        # Demo Complete
        print("─"*70)
        print("✅ DEMO COMPLETE!")
        print("─"*70)
        print("\nWhat you saw:")
        print("   1️⃣  Normal: Ocean Blue + Uplifting Music (10 sec)")
        print("   2️⃣  Alert: Red Flashing + Alert Sound (10 sec)")
        print("\n👋 Cleaning up...\n")
        
        # Cleanup
        self.actuators.emergency_active = False
        self.actuators.cleanup()

if __name__ == "__main__":
    print("\n🎬 Starting Alert Demo in 3 seconds...")
    print("   Press Ctrl+C to stop\n")
    time.sleep(3)
    
    try:
        demo = AlertSystemDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo stopped by user")
        demo = AlertSystemDemo()
        demo.actuators.emergency_active = False
        demo.actuators.cleanup()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()