import json
import os
import time
from collections import defaultdict
import numpy as np

class PersonalizationModel:
    def __init__(self, user_id="user_default", data_file="data/user_preferences.json"):
        """
        Personalization model that learns user preferences over time
        
        Args:
            user_id: Unique identifier for the user
            data_file: Path to store user preference data
        """
        self.user_id = user_id
        self.data_file = data_file
        
        # User preference profile
        self.user_profile = {
            'user_id': user_id,
            'total_sessions': 0,
            'preferences': {
                # Emotion -> preferred environment
                'happy': {'color': 'cabin_evening', 'brightness': 180, 'audio': 'uplifting_ambient', 'volume': 40},
                'neutral': {'color': 'cabin_day', 'brightness': 130, 'audio': 'ambient_soft', 'volume': 30},
                'sad': {'color': 'warming', 'brightness': 190, 'audio': 'fireplace_crackling', 'volume': 45},
                'angry': {'color': 'calming_blue', 'brightness': 200, 'audio': 'ocean_waves', 'volume': 50},
                'fear': {'color': 'calming_soft', 'brightness': 220, 'audio': 'meditation_calm', 'volume': 55},
                'surprise': {'color': 'neutral_warm', 'brightness': 160, 'audio': 'ambient_soft', 'volume': 35},
                'disgust': {'color': 'nature_green', 'brightness': 150, 'audio': 'ambient_soft', 'volume': 30},
            },
            'comfort_zones': {
                # Learned comfort ranges
                'temperature': {'min': 20, 'max': 26, 'preferred': 23},
                'humidity': {'min': 40, 'max': 60, 'preferred': 50},
                'stress': {'comfortable_max': 40},
                'heart_rate': {'comfortable_max': 85}
            },
            'learning_history': []
        }
        
        # Load existing profile if available
        self.load_profile()
        
        # Learning buffer for current session
        self.session_data = []
        
    def load_profile(self):
        """Load user profile from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    loaded_profile = json.load(f)
                    if loaded_profile['user_id'] == self.user_id:
                        self.user_profile = loaded_profile
                        print(f"✅ Loaded personalization profile for {self.user_id}")
                        print(f"   Total sessions: {self.user_profile['total_sessions']}")
            except Exception as e:
                print(f"⚠️  Could not load profile: {e}, using defaults")
        else:
            print(f"📝 Creating new personalization profile for {self.user_id}")
    
    def save_profile(self):
        """Save user profile to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.user_profile, f, indent=2)
            print(f"💾 Saved personalization profile")
        except Exception as e:
            print(f"⚠️  Could not save profile: {e}")
    
    def record_feedback(self, environment_state, sensor_data, watch_data, emotion, comfort_improved):
        """
        Record feedback about an environment adjustment
        
        Args:
            environment_state: dict with color_scheme, brightness, audio, volume
            sensor_data: current sensor readings
            watch_data: current watch data
            emotion: current emotion
            comfort_improved: bool indicating if user became more comfortable
        """
        feedback_entry = {
            'timestamp': time.time(),
            'emotion': emotion,
            'environment': environment_state.copy(),
            'sensor_data': {
                'temperature': sensor_data['temperature'],
                'humidity': sensor_data['humidity'],
                'air_quality': sensor_data['air_quality']
            },
            'watch_data': {
                'heart_rate': watch_data['heart_rate'],
                'stress_level': watch_data['stress_level']
            },
            'comfort_improved': comfort_improved
        }
        
        self.session_data.append(feedback_entry)
    
    def learn_from_session(self):
        """Analyze session data and update preferences"""
        if len(self.session_data) < 5:
            return  # Not enough data to learn
        
        print("\n🧠 Learning from session data...")
        
        # Group by emotion
        emotion_groups = defaultdict(list)
        for entry in self.session_data:
            if entry['comfort_improved']:
                emotion_groups[entry['emotion']].append(entry)
        
        # Update preferences for each emotion
        for emotion, entries in emotion_groups.items():
            if len(entries) < 2:
                continue
            
            # Calculate average successful environment settings
            avg_brightness = np.mean([e['environment']['brightness'] for e in entries])
            avg_volume = np.mean([e['environment']['volume'] for e in entries])
            
            # Find most common successful color and audio
            colors = [e['environment']['color_scheme'] for e in entries]
            audios = [e['environment']['audio'] for e in entries]
            
            most_common_color = max(set(colors), key=colors.count)
            most_common_audio = max(set(audios), key=audios.count)
            
            # Update preferences (weighted average with existing)
            old_pref = self.user_profile['preferences'][emotion]
            new_pref = {
                'color': most_common_color,
                'brightness': int(0.7 * old_pref['brightness'] + 0.3 * avg_brightness),
                'audio': most_common_audio,
                'volume': int(0.7 * old_pref['volume'] + 0.3 * avg_volume)
            }
            
            self.user_profile['preferences'][emotion] = new_pref
            print(f"   Updated preference for {emotion}: {new_pref}")
        
        # Update comfort zones
        comfortable_entries = [e for e in self.session_data if e['comfort_improved']]
        if comfortable_entries:
            temps = [e['sensor_data']['temperature'] for e in comfortable_entries]
            hums = [e['sensor_data']['humidity'] for e in comfortable_entries]
            
            self.user_profile['comfort_zones']['temperature']['preferred'] = round(np.mean(temps), 1)
            self.user_profile['comfort_zones']['humidity']['preferred'] = round(np.mean(hums), 1)
            
            print(f"   Updated comfort zones: Temp={self.user_profile['comfort_zones']['temperature']['preferred']}°C, "
                  f"Humidity={self.user_profile['comfort_zones']['humidity']['preferred']}%")
        
        # Save learning history
        self.user_profile['learning_history'].append({
            'timestamp': time.time(),
            'entries_analyzed': len(self.session_data),
            'improvements_found': len(comfortable_entries)
        })
        
        # Increment session counter
        self.user_profile['total_sessions'] += 1
        
        # Save to file
        self.save_profile()
        
        # Clear session data
        self.session_data = []
    
    def get_personalized_environment(self, emotion, sensor_data, watch_data):
        """
        Get personalized environment recommendation based on learned preferences
        
        Returns: dict with color_scheme, brightness, audio, volume
        """
        # Get base preference for this emotion
        if emotion in self.user_profile['preferences']:
            base_env = self.user_profile['preferences'][emotion].copy()
        else:
            # Fallback to neutral
            base_env = self.user_profile['preferences']['neutral'].copy()
        
        # Adjust based on current conditions
        adjustments = {}
        
        # Temperature adjustment
        current_temp = sensor_data['temperature']
        preferred_temp = self.user_profile['comfort_zones']['temperature']['preferred']
        
        if current_temp > preferred_temp + 2:
            # Too hot, prefer cooler colors
            if 'warming' in base_env['color']:
                adjustments['color'] = 'calming_blue'
            adjustments['brightness'] = min(base_env['brightness'] + 20, 255)
        elif current_temp < preferred_temp - 2:
            # Too cold, prefer warmer colors
            if 'cooling' in base_env['color'] or 'calming_blue' in base_env['color']:
                adjustments['color'] = 'warming'
            adjustments['brightness'] = max(base_env['brightness'] - 20, 100)
        
        # Stress adjustment
        if watch_data['stress_level'] > 70:
            # High stress, increase calming
            adjustments['audio'] = 'meditation_calm'
            adjustments['volume'] = min(base_env['volume'] + 10, 70)
        
        # Merge adjustments
        final_env = {**base_env, **adjustments}
        final_env['description'] = f"Personalized for {emotion} (Session #{self.user_profile['total_sessions']})"
        
        return final_env
    
    def get_comfort_score(self, sensor_data, watch_data):
        """Calculate how close current conditions are to user's comfort zones"""
        score = 100
        
        # Temperature deviation
        temp_pref = self.user_profile['comfort_zones']['temperature']['preferred']
        temp_diff = abs(sensor_data['temperature'] - temp_pref)
        score -= temp_diff * 5
        
        # Humidity deviation
        hum_pref = self.user_profile['comfort_zones']['humidity']['preferred']
        hum_diff = abs(sensor_data['humidity'] - hum_pref)
        score -= hum_diff * 2
        
        # Stress level
        if watch_data['stress_level'] > self.user_profile['comfort_zones']['stress']['comfortable_max']:
            score -= (watch_data['stress_level'] - self.user_profile['comfort_zones']['stress']['comfortable_max']) * 0.5
        
        return max(0, min(100, score))
