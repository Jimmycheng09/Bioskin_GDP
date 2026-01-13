import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import io

# --- 1. CONFIGURATION & PAGE SETUP ---
st.set_page_config(layout="wide", page_title="Right Hand Sensor Monitor")

st.title("🖐️ Right Hand Sensor Dashboard")
st.markdown("Monitoring **Temperature (-20 to 60°C)** and **Pressure (0 to 50)**.")

# Custom CSS
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. HAND COORDINATES (Right Hand Only) ---

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

# --- 3. SENSOR CONFIGURATION ---
# 1 sensor per finger, except Ring which has 2.
SENSORS_CONFIG = {
    'Thumb':      {'x': 1.5, 'y': 3.5},
    'Index':      {'x': 3.0, 'y': 6.5},
    'Middle':     {'x': 4.5, 'y': 7.0},
    'Ring Tip':   {'x': 6.0, 'y': 6.2},
    'Ring Base':  {'x': 5.8, 'y': 4.5}, # 2nd sensor for Ring
    'Pinky':      {'x': 7.2, 'y': 4.5},
}

# Sidebar Controls to Turn Sensors On/Off
st.sidebar.header("Sensor Controls")
active_sensors = []
for name in SENSORS_CONFIG.keys():
    # Default all to True (On)
    if st.sidebar.checkbox(f"{name} Sensor", value=True):
        active_sensors.append(name)

# --- 4. DATA HANDLING ---

def get_data():
    """
    Currently generates RANDOM data.
    Replace the logic inside the 'else' block to read from Excel later.
    """
    # ---------------------------------------------------------
    # OPTION A: MOCK DATA (Current)
    # ---------------------------------------------------------
    data = []
    t = time.time()
    
    for name, coords in SENSORS_CONFIG.items():
        # Only generate data if the sensor is turned ON
        if name in active_sensors:
            # Random Temp between -20 and 60
            # We use sine waves + random noise to make it look "alive"
            base_temp = 20 + np.sin(t + coords['x']) * 40 # fluctuation
            temp = np.clip(base_temp + np.random.normal(0, 2), -20, 60)

            # Random Pressure between 0 and 50
            base_press = np.abs(np.cos(t * 1.5 + coords['y'])) * 50
            press = np.clip(base_press + np.random.normal(0, 2), 0, 50)

            data.append({
                'Sensor': name,
                'X': coords['x'],
                'Y': coords['y'],
                'Temperature': temp,
                'Pressure': press
            })
    
    return pd.DataFrame(data)

    # ---------------------------------------------------------
    # OPTION B: REAL EXCEL DATA (Future Use)
    # ---------------------------------------------------------
    # Uncomment lines below when you have the file 'sensor_data.xlsx'
    # df = pd.read_excel("sensor_data.xlsx")
    # # Filter for active sensors
    # df = df[df['Sensor'].isin(active_sensors)]
    # return df

# --- 5. EXCEL DOWNLOADER FUNCTION ---
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='SensorData')
    return output.getvalue()

# --- 6. VISUALIZATION ENGINE ---

def create_chart(df, metric, colorscale, v_min, v_max, unit):
    fig = go.Figure()

    # Hand Outline (Right Hand)
    fig.add_trace(go.Scatter(
        x=RIGHT_HAND_X, 
        y=HAND_OUTLINE_Y,
        mode='lines',
        line=dict(color='#334155', width=3),
        hoverinfo='skip',
        showlegend=False
    ))

    # Sensor Blobs
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
        xaxis=dict(range=[0, 9], visible=False), # Adjusted range for Right Hand
        yaxis=dict(range=[0, 8], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=450
    )
    return fig

# --- 7. MAIN APP LOOP ---

placeholder = st.empty()
download_btn_place = st.sidebar.empty() # Placeholder for download button

while True:
    # 1. Get Data
    df = get_data()
    unique_key = int(time.time() * 1000)

    # 2. Update Download Button in Sidebar
    # We update this every loop so the Excel file has the latest timestamped data
    if not df.empty:
        excel_data = convert_df_to_excel(df)
        download_btn_place.download_button(
            label="📥 Download Current Data (Excel)",
            data=excel_data,
            file_name=f"hand_sensor_data_{unique_key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_btn_{unique_key}"
        )

    # 3. Render Dashboard
    with placeholder.container():
        # KPI Row
        k1, k2 = st.columns(2)
        if not df.empty:
            avg_temp = df['Temperature'].mean()
            avg_press = df['Pressure'].mean()
            k1.metric("Avg Temp", f"{avg_temp:.1f} °C")
            k2.metric("Avg Pressure", f"{avg_press:.1f}")
        else:
            st.warning("All sensors are turned off.")

        st.divider()

        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            # Temperature: -20 to 60 (Blue -> Red)
            fig_t = create_chart(df, 'Temperature', 'RdBu_r', -20, 60, '°C')
            st.plotly_chart(fig_t, use_container_width=True, key=f"t_{unique_key}")

        with c2:
            # Pressure: 0 to 50 (Light Green -> Dark Green)
            # Using 'Viridis' or 'Greens' usually looks good for pressure
            fig_p = create_chart(df, 'Pressure', 'Greens', 0, 50, 'Psi')
            st.plotly_chart(fig_p, use_container_width=True, key=f"p_{unique_key}")

    time.sleep(0.5) # Slower refresh to allow clicking download
