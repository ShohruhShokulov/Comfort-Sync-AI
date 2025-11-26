import time
import threading
import os
from rpi_ws281x import *

# --- LED STRIP CONFIGURATION ---
LED_COUNT      = 30
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 65
LED_INVERT     = False
LED_CHANNEL    = 0

# --- AUDIO CONFIGURATION ---
# USB speaker hardware (find yours via `aplay -l`)
AUDIO_DEVICE = "hw:1,0"

# MP3 file paths
BEEP_FILE = "alert.mp3"
ALARM_FILE = "alarm.mp3"

class ActuatorSystem:
    def __init__(self):
        # --- 1. SETUP LEDS ---
        try:
            self.strip = Adafruit_NeoPixel(
                LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
            )
            self.strip.begin()
            print("✅ LED Strip Initialized")
        except Exception as e:
            print(f"❌ Error initializing LEDs: {e}")
            self.strip = None

        # Control flags for threading
        self.emergency_active = False
        self.emergency_thread = None

    # --- LIGHTING HELPERS ---
    def _color_wipe(self, color):
        if not self.strip: return
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def set_mood_lighting(self, mode):
        if self.emergency_active: return

        print(f"💡 Lights set to mode: {mode}")
        if mode == "CALM":
            self._color_wipe(Color(0, 100, 255))
        elif mode == "WARM":
            self._color_wipe(Color(255, 147, 41))
        elif mode == "ALERT":
            self._color_wipe(Color(255, 200, 0))
        else:
            self._color_wipe(Color(0, 0, 0))

    # --- AUDIO HELPERS ---
    def play_sound(self, sound_type):
        """
        Plays MP3 files via USB speaker using mpg123.
        Works under sudo.
        """
        try:
            if sound_type == "BEEP":
                os.system(f'mpg123 -a {AUDIO_DEVICE} "{BEEP_FILE}" >/dev/null 2>&1 &')
            elif sound_type == "ALARM":
                os.system(f'mpg123 -a {AUDIO_DEVICE} "{ALARM_FILE}" >/dev/null 2>&1 &')
        except Exception as e:
            print(f"Audio Error: {e}")

    # --- EMERGENCY PROTOCOL ---
    def activate_emergency_protocol(self, active=True):
        if active:
            if not self.emergency_active:
                self.emergency_active = True
                self.emergency_thread = threading.Thread(target=self._emergency_loop)
                self.emergency_thread.start()
        else:
            self.emergency_active = False
            self.set_mood_lighting("WARM")

    def _emergency_loop(self):
        print("🚨 EMERGENCY PROTOCOL ACTIVE 🚨")
        while self.emergency_active:
            # ON PHASE
            self._color_wipe(Color(255, 0, 0))  # Red
            self.play_sound("BEEP")
            time.sleep(0.15)
            # OFF PHASE
            self._color_wipe(Color(0, 0, 0))
            time.sleep(0.15)
        print("✅ Emergency Protocol Deactivated")

# --- Quick Test ---
if __name__ == "__main__":
    actors = ActuatorSystem()
    print("Testing Lights & Sound...")

    # 1. Test Calm Mode
    actors.set_mood_lighting("CALM")
    time.sleep(2)

    # 2. Test Emergency Strobe
    print("Triggering Emergency Strobe (3 seconds)...")
    actors.activate_emergency_protocol(True)
    time.sleep(3)
    actors.activate_emergency_protocol(False)

    # 3. Cleanup
    actors.set_mood_lighting("OFF")
