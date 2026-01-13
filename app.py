import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import io

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Right Hand Monitor")

st.title("🖐️ Right Hand Sensor Dashboard")
st.markdown("Sensors controlled via code. Visualizing **Temperature** and **Pressure**.")

# Custom CSS for centering
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. HAND OUTLINE (Right Hand) ---
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

# --- 3. SENSOR MAPPING & CONTROL ---

# Define locations for all possible sensors
ALL_SENSORS = {
    'Thumb':      {'x': 1.5, 'y': 3.5},
    'Index':      {'x': 3.0, 'y': 6.5},
    'Middle':     {'x': 4.5, 'y': 7.0},
    'Ring Tip':   {'x': 6.0, 'y': 6.2},
    'Ring Base':  {'x': 5.8, 'y': 4.5}, # Second sensor for Ring Finger
    'Pinky':      {'x': 7.2, 'y': 4.5},
}

# --- CONTROL PANEL (EDIT THIS LIST TO TURN SENSORS ON/OFF) ---
# If you comment out a line, that sensor will disappear from the map.
ENABLED_SENSORS = [
    'Thumb',
    'Index',
    'Middle',
    'Ring Tip',
    'Ring Base',
    'Pinky'
]

# --- 4. DATA GENERATION ---

def get_data():
    """Generates random data for enabled sensors only."""
    data = []
    t = time.time()
    
    for name in ENABLED_SENSORS:
        if name in ALL_SENSORS:
            coords = ALL_SENSORS[name]
            
            # Random Temp: -20 to 60
            base_temp = 20 + np.sin(t + coords['x']) * 35 
            temp = np.clip(base_temp + np.random.normal(0, 2), -20, 60)

            # Random Pressure: 0 to 50
            base_press = np.abs(np.cos(t * 1.5 + coords['y'])) * 45
            press = np.clip(base_press + np.random.normal(0, 2), 0, 50)

            data.append({
                'Sensor': name,
                'X': coords['x'],
                'Y': coords['y'],
                'Temperature': temp,
                'Pressure': press
            })
            
    return pd.DataFrame(data)

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='SensorData')
    return output.getvalue()

# --- 5. VISUALIZATION ---

def create_chart(df, metric, colorscale, v_min, v_max, unit):
    fig = go.Figure()

    # Draw Right Hand Outline
    fig.add_trace(go.Scatter(
        x=RIGHT_HAND_X, 
        y=HAND_OUTLINE_Y,
        mode='lines',
        line=dict(color='#334155', width=3),
        hoverinfo='skip',
        showlegend=False
    ))

    # Draw Sensors
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['X'],
            y=df['Y'],
            mode='markers+text',
            text=df['Sensor'],
            textposition="top center",
            marker=dict(
                size=45, 
                color=df[metric],
                colorscale=colorscale,
                cmin=v_min,
                cmax=v_max,
                showscale=True,
                colorbar=dict(title=unit, thickness=15, x=1.02),
                opacity=0.9,
                line=dict(width=1, color='white')
            ),
            hovertemplate=f"<b>%{{text}}</b><br>{metric}: %{{marker.color:.1f}} {unit}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title=f"Right Hand - {metric}",
        xaxis=dict(range=[0, 9], visible=False),
        yaxis=dict(range=[0, 8], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=450
    )
    return fig

# --- 6. MAIN LOOP ---

placeholder = st.empty()
dl_btn_spot = st.sidebar.empty()

while True:
    df = get_data()
    unique_key = int(time.time() * 1000)

    # Excel Download Button
    if not df.empty:
        excel_data = convert_df_to_excel(df)
        dl_btn_spot.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"sensor_data_{unique_key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{unique_key}"
        )

    with placeholder.container():
        # KPI Metrics
        k1, k2 = st.columns(2)
        if not df.empty:
            avg_t = df['Temperature'].mean()
            avg_p = df['Pressure'].mean()
            k1.metric("Avg Temp", f"{avg_t:.1f} °C")
            k2.metric("Avg Pressure", f"{avg_p:.1f}")
        
        st.divider()

        # Visualization Columns
        c1, c2 = st.columns(2)
        
        with c1:
            # Temperature (Blue -> Red)
            fig_t = create_chart(df, 'Temperature', 'RdBu_r', -20, 60, '
