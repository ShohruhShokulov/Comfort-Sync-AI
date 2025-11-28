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
BEEP_FILE      = "data/alert.mp3"
CALM_FILE      = "data/calm.mp3"

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
        
        # Track current state to avoid restarting same music/light
        self.current_color_scheme = None
        self.current_brightness = None
        self.current_audio = None
        self.current_volume = None
        
        # Realistic cabin/salon lighting color schemes with CLEAR DIFFERENCES (RGB values)
        self.cabin_colors = {
            # Normal comfortable cabin lighting (Warm tones)
            'cabin_day': (255, 235, 200),           # Bright warm white daylight
            'cabin_evening': (255, 180, 120),       # Sunset orange-amber
            'cabin_night': (180, 140, 100),         # Dim warm amber for night
            
            # Calming colors for stress relief (Blue tones)
            'calming_blue': (80, 180, 255),         # Sky blue (cooling effect)
            'calming_soft': (150, 200, 255),        # Soft light blue
            'calming_purple': (160, 120, 255),      # Gentle lavender purple
            
            # Nature-inspired colors (Green tones)
            'nature_green': (100, 255, 150),        # Fresh spring green
            'ocean_blue': (80, 200, 240),           # Deep ocean blue
            'forest_green': (80, 180, 120),         # Deep forest green
            
            # Temperature-based colors (Strong contrast)
            'cooling': (100, 200, 255),             # Cool cyan-blue
            'cooling_intense': (50, 150, 255),      # Intense cool blue
            'warming': (255, 160, 80),              # Warm sunset orange
            'warming_intense': (255, 120, 50),      # Intense warm orange-red
            
            # Neutral states
            'neutral_warm': (255, 220, 180),        # Soft warm beige
            'neutral_cool': (200, 220, 255),        # Soft cool white-blue
            
            # Emotional support colors (Unique tones)
            'energizing_yellow': (255, 230, 100),   # Bright sunny yellow
            'sunset_orange': (255, 140, 60),        # Deep sunset orange
            'soft_pink': (255, 180, 200),           # Gentle rose pink
            'deep_red': (255, 80, 80),              # Warm deep red
        }
        
        # Enhanced sound profiles mapped to actual audio files
        self.sound_profiles = {
            # Existing basic profiles
            'calming_deep': 'data/meditation.mp3',
            'nature_calm': 'data/ocean_waves.mp3',
            'ambient_soft': 'data/calm.mp3',
            'white_noise_cooling': 'data/ocean_waves.mp3',
            'alert': BEEP_FILE,
            
            # Decision model profiles (now using your actual files)
            'ocean_waves': 'data/ocean_waves.mp3',
            'fireplace_crackling': 'data/fireplace.mp3',
            'uplifting_ambient': 'data/uplifting.mp3',
            'meditation_calm': 'data/meditation.mp3',
        }

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
    
    def set_cabin_lighting(self, color_scheme, brightness=150):
        """
        Set cabin lighting with realistic color scheme for main controller
        Only changes if different from current
        """
        if self.emergency_active: return
        
        # Check if this is the same as current state
        if self.current_color_scheme == color_scheme and self.current_brightness == brightness:
            print(f"   💡 Lighting: Already set to {color_scheme} (skipping)")
            return
        
        if color_scheme not in self.cabin_colors:
            print(f"⚠️  Unknown color scheme: {color_scheme}, using cabin_day")
            color_scheme = 'cabin_day'
        
        rgb = self.cabin_colors[color_scheme]
        
        # Apply brightness scaling
        scale = brightness / 255.0
        r = int(rgb[0] * scale)
        g = int(rgb[1] * scale)
        b = int(rgb[2] * scale)
        
        try:
            if not self.strip: return
            
            # Set all LEDs to the same color for cabin ambiance
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(r, g, b))
            self.strip.show()
            
            self.current_state["light_mode"] = color_scheme
            self.current_state["light_color"] = f"RGB({r},{g},{b})"
            
            # Update tracking
            self.current_color_scheme = color_scheme
            self.current_brightness = brightness
            
            print(f"   💡 Lighting CHANGED: {color_scheme.replace('_', ' ').title()} "
                  f"(RGB: {r},{g},{b}, Brightness: {brightness})")
            
        except Exception as e:
            print(f"❌ LED error: {e}")

    def play_sound(self, sound_type, volume=50):
        """
        Play sound using mpg123 with looping
        Only changes if different from current
        """
        # Check if this is the same as current audio
        if self.current_audio == sound_type and self.current_volume == volume:
            print(f"   🎵 Audio: Already playing {sound_type} (skipping)")
            return
        
        try:
            # Map sound profiles to files
            if sound_type in self.sound_profiles:
                audio_file = self.sound_profiles[sound_type]
            elif sound_type == "BEEP":
                audio_file = BEEP_FILE
            elif sound_type == "CALM":
                audio_file = CALM_FILE
            else:
                print(f"⚠️  Unknown sound type: {sound_type}, using default")
                audio_file = CALM_FILE
            
            # Check if file exists
            if not os.path.exists(audio_file):
                print(f"⚠️  Audio file not found: {audio_file}, using {CALM_FILE}")
                audio_file = CALM_FILE
            
            # Stop current music first
            os.system("pkill mpg123 2>/dev/null")
            time.sleep(0.2)  # Wait for process to stop
            
            self.current_state["audio_status"] = f"PLAYING {sound_type}"
            
            # Play with infinite loop (-1)
            os.system(f'mpg123 -a {AUDIO_DEVICE} --loop -1 "{audio_file}" >/dev/null 2>&1 &')
            
            # Update tracking
            self.current_audio = sound_type
            self.current_volume = volume
            
            print(f"   🎵 Audio CHANGED: {sound_type} → {os.path.basename(audio_file)} (Volume: {volume}%, Looping)")
            
        except Exception as e:
            print(f"❌ Audio error: {e}")
            self.current_state["audio_status"] = "ERROR"

    def stop_sound(self):
        """Stop any playing sound"""
        try:
            os.system("pkill mpg123 2>/dev/null")
            if self.current_audio:
                print(f"   🔇 Audio: Stopped ({self.current_audio})")
                self.current_audio = None
                self.current_volume = None
            self.current_state["audio_status"] = "SILENT"
        except Exception as e:
            print(f"❌ Audio stop error: {e}")
    
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
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up actuators...")
        self.stop_sound()
        if self.strip:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
        self.current_color_scheme = None
        self.current_brightness = None
        self.current_audio = None

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
            actuators.activate_emergency_protocol(False)
    except KeyboardInterrupt:
        actuators.set_mood_lighting("OFF")
        print("\n✅ Actuator test ended.")