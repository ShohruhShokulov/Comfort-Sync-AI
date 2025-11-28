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
        
        # Enhanced realistic cabin lighting color schemes (RGB values)
        self.cabin_colors = {
            # Normal comfortable cabin lighting
            'cabin_day': (255, 240, 220),          # Warm white daylight
            'cabin_evening': (255, 200, 150),      # Warmer evening light
            'cabin_night': (100, 80, 60),          # Dim warm for night
            
            # Calming colors for stress relief
            'calming_blue': (100, 150, 255),       # Soft blue (cooling effect)
            'calming_soft': (200, 220, 255),       # Very soft blue-white
            'calming_purple': (180, 150, 255),     # Gentle lavender
            
            # Nature-inspired colors
            'nature_green': (150, 255, 180),       # Natural green (disgust/refresh)
            'ocean_blue': (120, 200, 255),         # Ocean blue (calming)
            'forest_green': (100, 200, 150),       # Deep forest (grounding)
            
            # Temperature-based colors
            'cooling': (150, 200, 255),            # Cool blue-white
            'cooling_intense': (80, 150, 255),     # Strong cool blue
            'warming': (255, 180, 100),            # Warm orange-yellow
            'warming_intense': (255, 150, 80),     # Strong warm orange
            
            # Neutral states
            'neutral_warm': (255, 220, 180),       # Neutral warm white
            'neutral_cool': (220, 235, 255),       # Neutral cool white
            
            # Emotional support colors
            'energizing_yellow': (255, 240, 150),  # Bright energizing (happy)
            'sunset_orange': (255, 160, 100),      # Sunset warmth (comforting)
            'soft_pink': (255, 200, 220),          # Gentle pink (soothing)
        }
        
        # Enhanced sound profiles mapped to actual audio files
        self.sound_profiles = {
            # Existing
            'calming_deep': CALM_FILE,
            'nature_calm': CALM_FILE,
            'ambient_soft': CALM_FILE,
            'white_noise_cooling': CALM_FILE,
            'alert': BEEP_FILE,
            
            # New profiles for decision model
            'ocean_waves': 'data/ocean_waves.mp3',          # Cool calming
            'fireplace_crackling': 'data/fireplace.mp3',    # Warm comforting
            'uplifting_ambient': 'data/uplifting.mp3',      # Energizing
            'meditation_calm': 'data/meditation.mp3',       # Deep relaxation
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
        
        Args:
            color_scheme: Name from self.cabin_colors
            brightness: 0-255
        """
        if self.emergency_active: return
        
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
            
            print(f"   💡 Lighting: {color_scheme.replace('_', ' ').title()} "
                  f"(RGB: {r},{g},{b}, Brightness: {brightness})")
            
        except Exception as e:
            print(f"❌ LED error: {e}")

    def play_sound(self, sound_type, volume=50):
        """
        Play sound using mpg123 - Changes track smoothly
        
        Args:
            sound_type: either old style ("BEEP", "CALM") or new profile names
            volume: 0-100
        """
        try:
            # Map new sound profiles to files, or use direct file for old style
            if sound_type in self.sound_profiles:
                audio_file = self.sound_profiles[sound_type]
            elif sound_type == "BEEP":
                audio_file = BEEP_FILE
            elif sound_type == "CALM":
                audio_file = CALM_FILE
            else:
                print(f"⚠️  Unknown sound type: {sound_type}")
                return
            
            # Stop current music first for smooth transition
            if pygame.mixer.music.get_busy():
                self.stop_sound()
                time.sleep(0.2)  # Brief pause for smooth transition
            
            self.current_state["audio_status"] = f"PLAYING {sound_type}"
            os.system(f'mpg123 -a {AUDIO_DEVICE} --loop -1 "{audio_file}" >/dev/null 2>&1 &')
            
            self.current_sound = sound_type
            print(f"   🎵 Audio: {sound_type} (File: {os.path.basename(audio_file)}, Volume: {volume}%, Looping)")
            
        except Exception as e:
            print(f"❌ Audio error: {e}")
            self.current_state["audio_status"] = "ERROR"
    
    def stop_sound(self):
        os.system("pkill mpg123")
        self.current_state["audio_status"] = "SILENT"
        print(f"   🔇 Audio: Stopped")
    
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
        self.stop_sound()
        if self.strip:
            self._color_wipe(Color(0, 0, 0), "OFF")

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