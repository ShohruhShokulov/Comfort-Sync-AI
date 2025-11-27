import time
import threading
import os
from rpi_ws281x import *

# --- CONFIGURATION ---
LED_COUNT      = 30
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 65
LED_INVERT     = False
LED_CHANNEL    = 0
AUDIO_DEVICE   = "hw:3,0"
BEEP_FILE      = "alert.mp3"
CALM_FILE      = "calm.mp3"

class ActuatorSystem:
    def __init__(self):
        # State Tracking (For Dashboard)
        self.current_state = {
            "light_color": "OFF",
            "light_mode": "IDLE",
            "audio_status": "SILENT",
            "emergency_active": False
        }

        # Setup LEDs
        try:
            self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
            self.strip.begin()
        except:
            self.strip = None

        self.emergency_active = False
        self.emergency_thread = None

    def get_state(self):
        """Returns the real-time status of lights and sound."""
        return self.current_state

    def _color_wipe(self, color, name):
        """Helper to set color and update state name."""
        if not self.strip: return
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()
        
        # Update State
        self.current_state["light_color"] = name

    def set_mood_lighting(self, mode):
        if self.emergency_active: return

        self.current_state["light_mode"] = mode
        
        if mode == "CALM":
            self._color_wipe(Color(0, 100, 255), "COOL BLUE")
        elif mode == "WARM":
            self._color_wipe(Color(255, 147, 41), "WARM AMBER")
        elif mode == "ALERT":
            self._color_wipe(Color(255, 200, 0), "WARNING ORANGE")
        else:
            self._color_wipe(Color(0, 0, 0), "OFF")

    def play_sound(self, sound_type):
        try:
            self.current_state["audio_status"] = f"PLAYING {sound_type}"
            if sound_type == "BEEP":
                os.system(f'mpg123 -a {AUDIO_DEVICE} "{BEEP_FILE}" >/dev/null 2>&1 &')
            elif sound_type == "CALM":
                os.system(f'mpg123 -a {AUDIO_DEVICE} "{CALM_FILE}" >/dev/null 2>&1 &')
            # Reset status after short delay (approx length of sound)
            threading.Timer(1.0, lambda: self.current_state.update({"audio_status": "SILENT"})).start()
        except:
            pass
        self.current_state["audio_status"] = "SILENT"

    def stop_sound(self):
        os.system("pkill mpg123")
        self.current_state["audio_status"] = "SILENT"
    
    def activate_emergency_protocol(self, active=True):
        if active:
            if not self.emergency_active:
                self.emergency_active = True
                self.current_state["emergency_active"] = True
                self.current_state["light_mode"] = "EMERGENCY"
                self.emergency_thread = threading.Thread(target=self._emergency_loop)
                self.emergency_thread.start()
        else:
            self.emergency_active = False
            self.current_state["emergency_active"] = False
            self.set_mood_lighting("WARM")

    def _emergency_loop(self):
        while self.emergency_active:
            # ON
            self._color_wipe(Color(255, 0, 0), "RED STROBE")
            self.play_sound("BEEP")
            time.sleep(0.15)
            # OFF
            self._color_wipe(Color(0, 0, 0), "OFF")
            time.sleep(0.15)

# --- Quick Test to verify functionality ---
if __name__ == "__main__":
    actuators = ActuatorSystem()
    print("🔎 Testing Actuators... (Press Ctrl+C to stop)")
    try:
        while True:
            actuators.set_mood_lighting("CALM")
            actuators.play_sound("CALM")
            time.sleep(20)
            actuators.stop_sound()
            actuators.set_mood_lighting("WARM")
            time.sleep(5)
            actuators.set_mood_lighting("ALERT")
            time.sleep(5)
            actuators.activate_emergency_protocol(True)
            time.sleep(10)
            actuators.stop_sound()
            actuators.activate_emergency_protocol(False)
            actuators.stop_sound()
    except KeyboardInterrupt:
        actuators.set_mood_lighting("OFF")
        print("\n✅ Actuator test ended.")