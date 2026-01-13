import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# --- 1. CONFIGURATION & PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Biometric Hand Monitor")

st.title("🖐️ Biometric Palm Dashboard")
st.markdown("Real-time monitoring of **Left Hand** sensor data.")

# Custom CSS to center things
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. HIGH PRECISION HAND OUTLINE (Left Hand) ---

# Coordinates for Right Hand (Wrist -> Thumb -> Fingers -> Pinky -> Wrist)
RIGHT_HAND_X = [
    4.50, 4.00, 3.50, 3.00, 2.50, 2.00, 1.50, 
    1.20, 1.00, 0.90, 0.85, 0.90, 1.10, 
    1.40, 1.70, 2.00, 2.30, 2.50, 
    2.60, 2.70, 2.80, 2.90, 3.05, 3.20, 3.30, 3.40, 3.50, 
    3.70, 3.80, 3.90, 4.10, 4.30, 4.50, 4.70, 4.90, 5.00, 5.10, 5.20, 
    5.40, 5.50, 5.60, 5.80, 6.00, 6.20, 6.40, 6.50, 6.60, 
    6.80, 6.90, 7.10, 7.30, 7.50, 7.70, 7.80, 7.85, 
    7.80, 7.70, 7.50, 7.20, 6.80, 6.20, 5.50, 5.00, 4.50
]

HAND_OUTLINE_Y = [
    0.00, 0.05, 0.15, 0.30, 0.55, 0.90, 1.40, 
    1.80, 2.50, 3.20, 3.80, 4.20, 4.40, 
    4.40, 4.20, 3.80, 3.20, 2.90, 
    3.50, 5.00, 6.00, 6.80, 7.00, 6.80, 6.00, 5.00, 3.90, 
    4.50, 6.00, 7.00, 7.50, 7.60, 7.50, 7.00, 6.00, 5.00, 4.50, 4.10, 
    4.80, 5.50, 6.20, 6.70, 6.80, 6.70, 6.20, 5.50, 4.50, 
    3.80, 4.80, 5.20, 5.40, 5.20, 4.80, 4.20, 3.50, 
    3.00, 2.20, 1.50, 1.00, 0.60, 0.30, 0.10, 0.05, 0.00
]

# Generate Left Hand X coordinates by mirroring (10 - X)
LEFT_HAND_X = [10 - x for x in RIGHT_HAND_X]

# Sensor Locations (X, Y) for Right Hand
SENSORS_RIGHT = {
    'Thumb':       {'x': 1.5, 'y': 3.5},
    'Index Tip':   {'x': 3.0, 'y': 6.5},
    'Middle Tip':  {'x': 4.5, 'y': 7.0},
    'Ring Tip':    {'x': 6.0, 'y': 6.2},
    'Pinky Tip':   {'x': 7.2, 'y': 4.5},
#    'Palm Center': {'x': 4.5, 'y': 3.0},
#    'Palm Base':   {'x': 4.5, 'y': 1.0}
}

def get_mock_data():
    """Simulate Left Hand Data for both Temp and Force."""
    data = []
    t = time.time()
    
    for sensor_name, coords in SENSORS_RIGHT.items():
        x_left = 10 - coords['x']
        y = coords['y']
        
        # Noise Generation
        # Temp: ~30-36 C
        temp_val = 33 + np.sin(t + x_left) * 3 + np.random.normal(0, 0.2)
        
        # Pressure/Force: ~0-20 Newtons
        # Increased multiplier from 12 to 15 to simulate Newton scale
        press_val = np.abs(np.sin(t * 1.5 + y)) * 15 + np.random.normal(0, 0.5)
        
        data.append({
            'Sensor': sensor_name,
            'X': x_left,
            'Y': y,
            'Temperature': temp_val, 
            'Pressure': max(0, press_val)
        })
        
    return pd.DataFrame(data)

# --- 3. VISUALIZATION ENGINE ---

def create_hand_chart(df, metric, colorscale, range_min, range_max, unit):
    fig = go.Figure()

    # 1. Hand Outline
    fig.add_trace(go.Scatter(
        x=LEFT_HAND_X, 
        y=HAND_OUTLINE_Y,
        mode='lines',
        line=dict(color='#334155', width=3),
        hoverinfo='skip',
        showlegend=False
    ))

    # 2. Sensor Heatmap
    fig.add_trace(go.Scatter(
        x=df['X'],
        y=df['Y'],
        mode='markers+text',
        text=df['Sensor'],
        textposition="top center",
        marker=dict(
            size=30, 
            color=df[metric],
            colorscale=colorscale,
            cmin=range_min,
            cmax=range_max,
            showscale=True,
            colorbar=dict(title=unit, thickness=15, x=1.02),
            opacity=0.9,
            line=dict(width=1, color='rgba(255,255,255,0.5)')
        ),
        hovertemplate=f"<b>%{{text}}</b><br>{metric}: %{{marker.color:.1f}} {unit}<extra></extra>",
        showlegend=False
    ))

    # Layout Polish
    fig.update_layout(
        title=f"Left Hand - {metric}",
        xaxis=dict(range=[0, 10], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 8], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=450
    )
    
    return fig

# --- 4. MAIN RUN LOOP ---

placeholder = st.empty()

while True:
    df = get_mock_data()
    unique_key = int(time.time() * 1000) # Key fix for duplication error
    
    with placeholder.container():
        kpi1, kpi2, kpi3 = st.columns(3)
        avg_temp = df['Temperature'].mean()
        avg_force = df['Pressure'].mean()
        
        kpi1.metric("Avg Temp", f"{avg_temp:.1f} °C", delta=f"{avg_temp-33:.1f}")
        kpi2.metric("Avg Force", f"{avg_force:.1f} N") # Changed unit to N
        kpi3.info("System Online | Stream Active")
        
        st.divider()

        col_temp, col_press = st.columns(2)
        
        with col_temp:
            # Temperature: Blue -> Red
            fig_temp = create_hand_chart(
                df, 
                metric='Temperature', 
                colorscale='RdBu_r', 
                range_min=28, 
                range_max=38, 
                unit='°C'
            )
            st.plotly_chart(fig_temp, use_container_width=True, key=f"temp_{unique_key}")
            
        with col_press:
            # Pressure/Force: Light Blue -> Deep Blue
            # Changed colorscale to 'Blues' and unit to 'N'
            fig_press = create_hand_chart(
                df, 
                metric='Pressure', 
                colorscale='Blues', 
                range_min=0, 
                range_max=20, 
                unit='N'
            )
            st.plotly_chart(fig_press, use_container_width=True, key=f"press_{unique_key}")

    time.sleep(0.1)
