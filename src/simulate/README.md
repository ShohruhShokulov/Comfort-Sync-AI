# Smartwatch Data Simulator

Generates realistic heart rate and stress level data for testing Comfort Sync AI.

## Quick Start

```python
from data_generator import SmartWatchSimulator, StressScenario

# Initialize
smartwatch = SmartWatchSimulator()

# Set scenario
smartwatch.set_scenario(StressScenario.NORMAL)

# Get data
data = smartwatch.get_data()
print(f"Heart Rate: {data['heart_rate']} bpm")
print(f"Stress: {data['stress_level']}%")
```

## Testing

Run the simulator directly:
```bash
cd /home/shohruh/University/Capstone/Comfort_Sync_AI/src/simulate
python data_generator.py
```

Run the example integration:
```bash
python example_usage.py
```

## Scenarios

### Normal
- Heart Rate: 64-80 bpm
- Stress: 15-35%
- Comfortable and relaxed

### Moderate
- Heart Rate: 83-107 bpm
- Stress: 45-75%
- Slightly uncomfortable

### Bad
- Heart Rate: 97-133 bpm
- Stress: 75-95%
- Very uncomfortable, needs immediate action

## Data Format

```python
{
    "timestamp": "2024-01-15T10:30:45.123456",
    "heart_rate": 75,
    "stress_level": 32.5,
    "stress_category": "low",  # low/moderate/high
    "scenario": "normal",
    "description": "Relaxed and comfortable state"
}
```

## Integration with Your Sensors

```python
from data_generator import SmartWatchSimulator, StressScenario

smartwatch = SmartWatchSimulator()
smartwatch.set_scenario(StressScenario.NORMAL)

while True:
    # Get all sensor data
    watch_data = smartwatch.get_data()
    temp, humidity = read_dht22()  # Your DHT22 code
    air_quality = read_mq135()     # Your MQ135 code
    
    # Make decisions based on combined data
    if watch_data['stress_level'] > 70:
        control_led_strip('blue')  # Cooling
        play_calming_music()
    
    time.sleep(2)
```
