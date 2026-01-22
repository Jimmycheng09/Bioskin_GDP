import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import io
import datetime

# --- 1. CONFIGURATION ---
BASE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRzNUEwTvcdaOms8gu9f9zwVMGRztyOzc1JQ2vG9jc1RjTYhpRS9b2P8KWEEp7GjWJRvtURMhhQtKvj/pub?gid=0&single=true&output=csv"

st.set_page_config(layout="wide", page_title="Mixed Sensor Dashboard")
st.title("🖐️ Mixed Sensor Dashboard")
st.markdown("Visualising **Temperature** and **Force (Capacitive & Resistive)** on a single hand.")

# Custom CSS
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

# --- 3. SENSOR DEFINITIONS ---
RESISTIVE_SENSORS = {
    'Force (Resistive)': {'x': 3.1, 'y': 6.5, 'finger_id' : 4}
}
PRESSURE_SENSORS = {
    'Force (Capacitive)':  {'x': 4.4, 'y': 4.5, 'finger_id' : 3} 
}
TEMP_SENSORS = {
    'Temp': {'x': 4.4, 'y': 6.5, 'finger_id' : 3}
}

# --- 4. DATA GENERATION ---
def get_data():
    try:
        # Cache Busting
        unique_url = f"{BASE_SHEET_URL}&t={int(time.time())}"
        
        # --- THE FIX: Load all data, but slice IMMEDIATELY to last 5 rows ---
        # Note: We can't use 'skiprows' easily with GSheets URL because header row varies
        # So we read it, then tail(5) it immediately.
        df = pd.read_csv(unique_url)
        
        # Only keep the last 5 rows to ensure we are looking at recent data
        df = df.tail(5)
        
        # Clean Data
        cols_to_num = ['Finger Number', 'Temperature', 'Capacitive', 'Resistive']
        for col in cols_to_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'Finger Number' not in df.columns:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), "Column 'Finger Number' missing"
            
        # Group by Finger Number and get the single latest entry for each finger
        # This prevents "looping" duplicates
        latest_df = df.groupby('Finger Number').tail(1).set_index('Finger Number')
        
        data_temp, data_press, data_resistive = [], [], []

        def get_val(df, finger_id, col_name):
            if df.empty or finger_id not in df.index: return 0.0
            return float(df.loc[finger_id, col_name])

        # Map Sensors (No outer loop here!)
        for name, coords in TEMP_SENSORS.items():
            val = get_val(latest_df, coords['finger_id'], 'Temperature')
            data_temp.append({'Sensor': name, 'X': coords['x'], 'Y': coords['y'], 'Value': val})

        for name, coords in PRESSURE_SENSORS.items():
            val = get_val(latest_df, coords['finger_id'], 'Capacitive')
            data_press.append({'Sensor': name, 'X': coords['x'], 'Y': coords['y'], 'Value': val})

        for name, coords in RESISTIVE_SENSORS.items():
            val = get_val(latest_df, coords['finger_id'], 'Resistive')
            data_resistive.append({'Sensor': name, 'X': coords['x'], 'Y': coords['y'], 'Value': val})
            
        return pd.DataFrame(data_temp), pd.DataFrame(data_press), pd.DataFrame(data_resistive), None

    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), str(e)

def convert_to_excel(df_t, df_p, df_r):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_t.empty: df_t.to_excel(writer, index=False, sheet_name='Temperature')
        if not df_p.empty: df_p.to_excel(writer, index=False, sheet_name='Force_Capacitive')
        if not df_r.empty: df_r.to_excel(writer, index=False, sheet_name='Force_Resistive')
    return output.getvalue()

# --- 5. VISUALIZATION ---
def create_combined_chart(df_temp, df_press, df_resistive):
    fig = go.Figure()

    # Hand Outline
    fig.add_trace(go.Scatter(
        x=RIGHT_HAND_X, y=HAND_OUTLINE_Y,
        mode='lines', line=dict(color='#334155', width=3),
        hoverinfo='skip', showlegend=False
    ))

    # Temp
    if not df_temp.empty:
        fig.add_trace(go.Scatter(
            x=df_temp['X'], y=df_temp['Y'], mode='markers+text',
            text=df_temp['Sensor'], textposition="top center",
            marker=dict(size=50, color=df_temp['Value'], colorscale='RdBu_r', cmin=-20, cmax=60, showscale=True,
                        colorbar=dict(title="Temp (°C)", orientation='h', y=-0.20, x=0.5, len=0.9, thickness=15),
                        opacity=0.9, line=dict(width=1, color='white')),
            hovertemplate="<b>%{text}</b><br>Temp: %{marker.color:.1f} °C<extra></extra>"
        ))

    # Pressure
    if not df_press.empty:
        fig.add_trace(go.Scatter(
            x=df_press['X'], y=df_press['Y'], mode='markers+text',
            text=df_press['Sensor'], textposition="bottom center", 
            marker=dict(size=50, symbol='circle', color=df_press['Value'], colorscale='RdBu_r', cmin=0, cmax=50, showscale=True,
                        colorbar=dict(title="Force (Cap)", orientation='h', y=-0.40, x=0.5, len=0.9, thickness=15),
                        opacity=0.9, line=dict(width=2, color='yellow')),
            hovertemplate="<b>%{text}</b><br>Force: %{marker.color:.1f}<extra></extra>"
        ))

    # Resistive
    if not df_resistive.empty:
        fig.add_trace(go.Scatter(
            x=df_resistive['X'], y=df_resistive['Y'], mode='markers+text',
            text=df_resistive['Sensor'], textposition="bottom center", 
            marker=dict(size=50, symbol='square', color=df_resistive['Value'], colorscale='RdBu_r', cmin=0, cmax=100, showscale=True,
                        colorbar=dict(title="Force (Res)", orientation='h', y=-0.60, x=0.5, len=0.9, thickness=15),
                        opacity=0.9, line=dict(width=2, color='black')),
            hovertemplate="<b>%{text}</b><br>Resistive: %{marker.color:.1f}<extra></extra>"
        ))

    fig.update_layout(
        title="Live Sensor Map",
        xaxis=dict(range=[0, 9], visible=False),
        yaxis=dict(range=[0, 8], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=380), height=850
    )
    return fig

# --- 6. MAIN LOOP ---
placeholder = st.empty()
dl_btn_spot = st.sidebar.empty()
last_update_spot = st.sidebar.empty()

while True:
    df_temp, df_press, df_resistive, error_msg = get_data()
    unique_key = int(time.time() * 1000)
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    last_update_spot.markdown(f"**Last Fetch:** {current_time}")

    excel_data = convert_to_excel(df_temp, df_press, df_resistive)
    dl_btn_spot.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name=f"mixed_sensor_data_{unique_key}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{unique_key}"
    )

    with placeholder.container():
        if error_msg:
            st.error(f"⚠️ Error: {error_msg}")
        else:
            c1, c2, c3 = st.columns(3)
            val_t = f"{df_temp['Value'].mean():.1f} °C" if not df_temp.empty else "No Data"
            val_p = f"{df_press['Value'].mean():.1f} N" if not df_press.empty else "No Data"
            val_r = f"{df_resistive['Value'].mean():.1f} N" if not df_resistive.empty else "No Data"

            c1.metric("Temp Sensor", val_t)
            c2.metric("Force (Cap)", val_p)
            c3.metric("Force (Resistive)", val_r)
            
            st.divider()

            fig = create_combined_chart(df_temp, df_press, df_resistive)
            st.plotly_chart(fig, use_container_width=True, key=f"main_chart_{unique_key}")

    time.sleep(2)
