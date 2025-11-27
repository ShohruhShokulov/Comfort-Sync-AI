import cv2
import config
import threading
import time
import json
import paho.mqtt.client as mqtt
from deepface import DeepFace


# --- GLOBAL VARIABLES ---
current_emotion = "neutral"
latest_frame = None
lock = threading.Lock()
running = True

# --- MQTT SETUP ---
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to Pi Broker at {MQTT_BROKER}")
    else:
        print(f"❌ Connection failed with code {rc}")

client.on_connect = on_connect

# --- AI WORKER THREAD (The "Brain") ---
def emotion_analysis_loop():
    global current_emotion, latest_frame, running

    while running:
        with lock:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            # Make a copy so we don't conflict with the main video loop
            frame_to_analyze = latest_frame.copy()

        try:
            # DeepFace analyzes the whole frame to find the dominant emotion
            # We use 'opencv' backend for speed
            objs = DeepFace.analyze(
                img_path=frame_to_analyze, 
                actions=['emotion'], 
                enforce_detection=False, 
                detector_backend='opencv',
                silent=True
            )
            
            if len(objs) > 0:
                current_emotion = objs[0]['dominant_emotion']
                
                # Publish to MQTT
                payload = json.dumps({"emotion": current_emotion, "ts": time.time()})
                client.publish(TOPIC_EMOTION, payload)
                # print(f"Output: {current_emotion}") # Optional debug

        except Exception as e:
            pass # Ignore frames where face isn't clear
        
        # Pause briefly to save CPU (2-4 analyses per second is enough)
        time.sleep(0.3) 

# --- MAIN VIDEO LOOP (The "Eyes") ---
def start_vision_system():
    global latest_frame, running

    # 1. Connect MQTT
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"❌ MQTT Error: {e}")
        return

    # 2. Setup Camera & Face Detector (Haar Cascade)
    # Haar is old but extremely fast for drawing boxes
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    
    # 3. Start the AI Thread
    ai_thread = threading.Thread(target=emotion_analysis_loop, daemon=True)
    ai_thread.start()

    print("🎥 System Started. Drawing boxes locally, analyzing emotion in background...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Send frame to background thread
        with lock:
            latest_frame = frame

        # --- DRAWING LOGIC (Fast, Real-time) ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces for VISUALS only (Fast)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Draw the box (Green)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw the emotion label (Yellow)
            # We use the 'current_emotion' variable which comes from the background thread
            label = f"{current_emotion.upper()}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        # Show the frame
        cv2.imshow('Cabin ComfortSync Vision', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    running = False
    cap.release()
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    start_vision_system()