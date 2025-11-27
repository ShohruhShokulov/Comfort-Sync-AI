import streamlit as st
import pandas as pd
import time
import json
import os
import random
import plotly.graph_objects as go
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Cabin ComfortSync AI",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIG & PATHS ---
STATE_FILE = "../state.json"
COMMAND_FILE = "../cmd.json"

# --- LOAD CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")

# --- HELPER FUNCTIONS ---
def load_state():
    if not os.path.exists(STATE_FILE): return None
    try:
        with open(STATE_FILE, 'r') as f: return json.load(f)
    except: return None

def send_command(mode):
    try:
        with open(COMMAND_FILE, 'w') as f: json.dump({"mode": mode}, f)
    except: pass

# --- VISUALIZATION FUNCTIONS ---
def create_gauge_chart(value, title, max_val, thresholds):
    """Creates a futuristic arc gauge."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 14, 'color': "#94A3B8"}},
        number = {'suffix': "", 'font': {'size': 24, 'color': "white", 'family': "Orbitron"}},
        gauge = {
            'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "#333"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': thresholds,
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.75, 'value': value}
        }
    ))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def create_radar_v2v(status):
    """Simulates the V2V Safety Network Radar."""
    # Generate random traffic
    traffic = pd.DataFrame({
        'x': [0, random.uniform(-20, 20), random.uniform(-30, 30), random.uniform(-15, 15)],
        'y': [0, random.uniform(10, 50), random.uniform(20, 60), random.uniform(5, 30)],
        'type': ['MY CAR', 'VEHICLE', 'VEHICLE', 'VEHICLE'],
        'size': [25, 15, 15, 15]
    })
    
    color_map = {'MY CAR': '#38BDF8', 'VEHICLE': '#64748B'}
    if status == 'EMERGENCY': color_map['VEHICLE'] = '#EF4444' # Alert nearby cars

    fig = px.scatter(traffic, x='x', y='y', color='type', size='size', 
                     color_discrete_map=color_map, opacity=0.9)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[-40, 40], showgrid=True, gridcolor='#334155', zeroline=False, showticklabels=False),
        yaxis=dict(range=[-10, 80], showgrid=True, gridcolor='#334155', zeroline=False, showticklabels=False),
        showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=250
    )
    # Add radar rings
    fig.add_shape(type="circle", x0=-15, y0=-15, x1=15, y1=15, line_color="#38BDF8", opacity=0.3)
    fig.add_shape(type="circle", x0=-30, y0=-30, x1=30, y1=30, line_color="#38BDF8", opacity=0.1)
    
    return fig

# --- MAIN APP LOGIC ---

# 1. READ STATE
curr = load_state()
if curr is None:
    st.warning("⚠️ Waiting for Raspberry Pi Controller...")
    time.sleep(1)
    st.rerun()

# 2. EMERGENCY OVERLAY
if curr['status'] == 'EMERGENCY':
    st.markdown('<div class="emergency-overlay">🚨 CRITICAL DROWSINESS DETECTED - INITIATING SAFE STOP 🚨</div>', unsafe_allow_html=True)

# 3. HEADER & PROFILE
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("## 🚘 Cabin ComfortSync AI")
with c2:
    # Profile Selector (Simulates Personalization Requirement)
    profile = st.selectbox("Driver Profile", ["Shohruh (Owner)", "Guest"], label_visibility="collapsed")

# 4. MAIN TABS
tab_drive, tab_env, tab_debug = st.tabs(["🏎️ DRIVER COCKPIT", "🌡️ CLIMATE CONTROL", "⚙️ SYSTEM DIAGNOSTICS"])

with tab_drive:
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    
    with col_l:
        st.markdown("### 🧬 BIOMETRICS")
        st.metric("HEART RATE", f"{curr['bio'].get('heart_rate', 0)} BPM", "Normal")
        
        # HRV Metric (Simulated for depth)
        hrv = curr['bio'].get('heart_rate', 75) * 0.8
        st.metric("HRV SCORE", f"{int(hrv)} ms", "-2 ms")

    with col_m:
        st.markdown("<div style='text-align:center'><h3>FATIGUE MONITOR</h3></div>", unsafe_allow_html=True)
        
        # DYNAMIC GAUGE
        fatigue = curr['bio'].get('fatigue_index', 0)
        steps = [
            {'range': [0, 50], 'color': "#1e293b"}, 
            {'range': [50, 80], 'color': "#f59e0b"}, 
            {'range': [80, 100], 'color': "#ef4444"}
        ]
        st.plotly_chart(create_gauge_chart(fatigue, "FATIGUE LEVEL", 100, steps), use_container_width=True)
        
        # SIMULATION CONTROLS (Hidden in plain sight as "Test Mode")
        with st.expander("🛠️ SIMULATION TEST PANEL", expanded=True):
            b1, b2, b3 = st.columns(3)
            if b1.button("🟢 NORMAL"): send_command("NORMAL")
            if b2.button("🟡 DROWSY"): send_command("DROWSINESS_EVENT")
            if b3.button("🔴 STRESS"): send_command("STRESS_EVENT")

    with col_r:
        st.markdown("### 📡 V2V NETWORK")
        st.plotly_chart(create_radar_v2v(curr['status']), use_container_width=True)
        
        # Status Badge
        status_color = "#4ade80" # Green
        if curr['status'] == "WARNING": status_color = "#facc15"
        if curr['status'] == "EMERGENCY": status_color = "#ef4444"
        
        st.markdown(f"""
        <div style="background:{status_color}22; border:1px solid {status_color}; padding:5px; border-radius:5px; text-align:center; color:{status_color}; font-weight:bold;">
            SYSTEM STATUS: {curr['status']}
        </div>
        """, unsafe_allow_html=True)

with tab_env:
    e1, e2, e3 = st.columns(3)
    
    with e1:
        st.markdown("### 🌡️ THERMAL")
        real_temp = curr['env'].get('temp', 22.0)
        target_temp = 24.0 if profile == "Guest" else 22.0 # Personalization Logic
        
        st.metric("TARGET TEMP", f"{target_temp}°C")
        st.metric("ACTUAL TEMP", f"{real_temp}°C", f"{real_temp - target_temp:.1f}°C")
        
    with e2:
        st.markdown("### 💨 AIR QUALITY")
        aqi = curr['env'].get('air_quality', 'Good')
        st.metric("CO2 STATUS", aqi)
        st.progress(0.9 if aqi == "Good" else 0.4)
        
    with e3:
        st.markdown("### 💡 AMBIENT")
        # REAL HARDWARE FEEDBACK
        hw = curr.get('hardware', {})
        light_c = hw.get('light_color', 'OFF')
        audio_s = hw.get('audio_status', 'SILENT')
        
        # Styling based on state
        l_class = "status-off"
        if "WARM" in light_c: l_class = "status-warn"
        if "COOL" in light_c: l_class = "status-on"
        if "RED" in light_c: l_class = "status-crit"
        
        st.markdown(f"""
        <div class="hw-panel">
            <div class="status-indicator {l_class}">LIGHTS: {light_c}</div>
            <div class="status-indicator status-off">AUDIO: {audio_s}</div>
        </div>
        """, unsafe_allow_html=True)

with tab_debug:
    st.json(curr)
    st.info(f"Connected to Local Controller | Latency: {time.time() - curr['timestamp']:.3f}s")

# Auto-refresh
time.sleep(0.5)
st.rerun()