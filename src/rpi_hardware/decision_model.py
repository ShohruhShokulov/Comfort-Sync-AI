import time
from collections import deque
from datetime import datetime
import numpy as np

class EnvironmentDecisionModel:
    def __init__(self, window_seconds=20):
        """
        Decision model that analyzes data over a time window
        
        Args:
            window_seconds: Time window for analysis (default 20 seconds)
        """
        self.window_seconds = window_seconds
        
        # Data buffers (store last 20 seconds of readings)
        self.temperature_buffer = deque(maxlen=10)  # ~10 readings in 20s
        self.humidity_buffer = deque(maxlen=10)
        self.air_quality_buffer = deque(maxlen=10)
        self.heart_rate_buffer = deque(maxlen=10)
        self.stress_buffer = deque(maxlen=10)
        self.emotion_buffer = deque(maxlen=10)
        
        # Current environment state - Default calming blue with music
        self.current_environment = {
            'color_scheme': 'calming_soft',
            'brightness': 160,
            'audio': 'ambient_soft',
            'volume': 35,
            'description': 'Default calming environment (waiting for data)'
        }
        
        # Last decision time
        self.last_decision_time = 0
        self.decision_cooldown = 20  # Don't change environment more than once per 20s
        
    def add_data_point(self, sensor_data, watch_data, emotion):
        """Add new data point to buffers"""
        self.temperature_buffer.append(sensor_data['temperature'])
        self.humidity_buffer.append(sensor_data['humidity'])
        self.air_quality_buffer.append(sensor_data['air_quality'])
        self.heart_rate_buffer.append(watch_data['heart_rate'])
        self.stress_buffer.append(watch_data['stress_level'])
        self.emotion_buffer.append(emotion)
    
    def get_dominant_emotion(self):
        """Get the most frequent emotion in the last 20 seconds"""
        if not self.emotion_buffer:
            return 'neutral'
        
        # Count occurrences
        emotion_counts = {}
        for emotion in self.emotion_buffer:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Return most common
        return max(emotion_counts, key=emotion_counts.get)
    
    def calculate_averages(self):
        """Calculate average values from buffers"""
        return {
            'avg_temp': np.mean(self.temperature_buffer) if self.temperature_buffer else 0,
            'avg_humidity': np.mean(self.humidity_buffer) if self.humidity_buffer else 0,
            'avg_air_quality': np.mean(self.air_quality_buffer) if self.air_quality_buffer else 0,
            'avg_heart_rate': np.mean(self.heart_rate_buffer) if self.heart_rate_buffer else 0,
            'avg_stress': np.mean(self.stress_buffer) if self.stress_buffer else 0,
            'dominant_emotion': self.get_dominant_emotion()
        }
    
    def calculate_trend(self, buffer):
        """Calculate if values are increasing, decreasing, or stable"""
        if len(buffer) < 3:
            return 'stable'
        
        recent = list(buffer)[-3:]
        first_half = np.mean(recent[:2])
        second_half = recent[-1]
        
        diff = second_half - first_half
        
        if diff > 5:
            return 'increasing'
        elif diff < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def make_decision(self):
        """
        Analyze last 20 seconds and decide on environment settings
        Returns: dict with color_scheme, brightness, audio, volume
        """
        # Check cooldown
        if time.time() - self.last_decision_time < self.decision_cooldown:
            return None  # Don't change yet
        
        # Not enough data yet
        if len(self.stress_buffer) < 5:
            return None
        
        # Calculate averages
        avg = self.calculate_averages()
        
        # Calculate trends
        stress_trend = self.calculate_trend(self.stress_buffer)
        temp_trend = self.calculate_trend(self.temperature_buffer)
        
        # Decision scoring system
        decision_scores = {
            'calming_cool': 0,
            'calming_warm': 0,
            'energizing': 0,
            'neutral_comfort': 0,
            'deep_relax': 0
        }
        
        # Factor 1: Stress Level (Most Important)
        if avg['avg_stress'] > 70:
            decision_scores['deep_relax'] += 4
            decision_scores['calming_cool'] += 3
        elif avg['avg_stress'] > 50:
            decision_scores['calming_cool'] += 3
            decision_scores['calming_warm'] += 2
        elif avg['avg_stress'] < 30:
            decision_scores['energizing'] += 2
            decision_scores['neutral_comfort'] += 3
        else:
            decision_scores['neutral_comfort'] += 3
        
        # Factor 2: Emotion (High Priority)
        emotion = avg['dominant_emotion']
        if emotion == 'angry':
            decision_scores['calming_cool'] += 4
            decision_scores['deep_relax'] += 2
        elif emotion == 'sad':
            decision_scores['calming_warm'] += 4
            decision_scores['energizing'] += 2
        elif emotion == 'fear':
            decision_scores['calming_warm'] += 3
            decision_scores['deep_relax'] += 3
        elif emotion == 'happy':
            decision_scores['energizing'] += 3
            decision_scores['neutral_comfort'] += 2
        else:  # neutral
            decision_scores['neutral_comfort'] += 2
        
        # Factor 3: Temperature
        if avg['avg_temp'] > 26:
            decision_scores['calming_cool'] += 3
        elif avg['avg_temp'] < 20:
            decision_scores['calming_warm'] += 3
        
        # Factor 4: Heart Rate
        if avg['avg_heart_rate'] > 100:
            decision_scores['deep_relax'] += 2
            decision_scores['calming_cool'] += 2
        
        # Factor 5: Trends (are things getting worse?)
        if stress_trend == 'increasing':
            decision_scores['deep_relax'] += 2
            decision_scores['calming_cool'] += 1
        
        # Choose best decision
        best_decision = max(decision_scores, key=decision_scores.get)
        
        # Map decision to actual settings - All decisions now have audio
        environment_map = {
            'calming_cool': {
                'color_scheme': 'calming_blue',
                'brightness': 200,
                'audio': 'ocean_waves',
                'volume': 50,
                'description': 'Cool calming environment'
            },
            'calming_warm': {
                'color_scheme': 'warming',
                'brightness': 190,
                'audio': 'fireplace_crackling',
                'volume': 45,
                'description': 'Warm comforting environment'
            },
            'energizing': {
                'color_scheme': 'cabin_evening',
                'brightness': 180,
                'audio': 'uplifting_ambient',
                'volume': 40,
                'description': 'Energizing positive environment'
            },
            'neutral_comfort': {
                'color_scheme': 'cabin_day',
                'brightness': 140,
                'audio': 'ambient_soft',
                'volume': 30,
                'description': 'Neutral comfortable environment'
            },
            'deep_relax': {
                'color_scheme': 'calming_soft',
                'brightness': 220,
                'audio': 'meditation_calm',
                'volume': 55,
                'description': 'Deep relaxation mode'
            }
        }
        
        decision = environment_map[best_decision]
        decision['score_details'] = decision_scores
        decision['analytics'] = avg
        
        # Update last decision time
        self.last_decision_time = time.time()
        self.current_environment = decision
        
        return decision
    
    def get_current_environment(self):
        """Get current environment without making new decision"""
        return self.current_environment
