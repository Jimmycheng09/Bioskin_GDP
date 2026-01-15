import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import io
from datetime import datetime, timezone
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Mixed Sensor Dashboard")
st.title("🖐️ Mixed Sensor Dashboard")

# --- 2. CONSTANTS & MAPPINGS ---
# We map the Google Sheet headers to your Hand Coordinates here
SENSOR_MAPPING = {
    'Temp_Middle':      {'type': 'temp', 'name': 'Middle',   'x': 4.5, 'y': 7.0},
    'Temp_Ring_Tip':    {'type': 'temp', 'name': 'Ring Tip', 'x': 6.0, 'y': 6.2},
    'Pressure_Ring_Base': {'type': 'press', 'name': 'Ring Base','x': 5.8, 'y': 4.5}
}

RIGHT_HAND_X = [4.50, 4.00, 3.50, 3.00, 2.50, 2.00, 1.50, 1.20, 1.00, 0.90, 0.85, 0.90, 1.10, 1.40, 1.70, 2.00, 2.30, 2.50, 2.60, 2.70, 2.80, 2.90, 3.05, 3.20, 3.30, 3.40, 3.50, 3.70, 3.80, 3.90, 4.10, 4.30, 4.50, 4.70, 4.90, 5.00, 5.10, 5.20, 5.40, 5.50, 5.60, 5.80, 6.00, 6.20, 6.40, 6.50, 6.60, 6.80, 6.90, 7.10, 7.30, 7.50, 7.70, 7.80, 7.85, 7.80, 7.70, 7.50, 7.20, 6.80, 6.20, 5.50, 5.00, 4.50]
HAND_OUTLINE_Y = [0.00, 0.05, 0.15, 0.30, 0.55, 0.90, 1.40, 1.80, 2.50, 3.20, 3.80, 4.20, 4.40, 4.40, 4.20, 3.80, 3.20, 2.90, 3.50, 5.00, 6.00, 6.80, 7.00, 6.80, 6.00, 5.00, 3.90, 4.50, 6.00, 7.00, 7.50, 7.60, 7.50, 7.00, 6.00, 5.00, 4.50, 4.10, 4.80, 5.50, 6.20, 6.70, 6.80, 6.70, 6.20, 5.50, 4.50, 3.80, 4.80, 5.20, 5.40, 5.20, 4.80, 4.20, 3.50, 3.00, 2.20, 1.50, 1.00, 0.60, 0.30, 0.10, 0.05, 0.00]

# --- 3. DATA FETCHING ---
def get_google_sheet_data():
    # 1. Connect to GSheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Read Data (ttl=5 means it refreshes cache every 5 seconds)
    try:
        df = conn.read(ttl=5)
        # Ensure timestamp is datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheet: {e}")
        return pd.DataFrame()

def check_connection_status(last_timestamp_entry):
    """Calculates if the device is 'alive' based on time difference"""
    if pd.isnull(last_timestamp_entry):
        return False, "No Data"
        
    # Get current time (ensure UTC to match Pandas usually)
    now = datetime.now()
    time_diff = (now - last_timestamp_entry).total_seconds()
    
    # THRESHOLD: If no data for 30 seconds, consider it OFFLINE
    is_connected = time_diff < 30 
    return is_connected, time_diff

def process_data_for_graph(last_row):
    """Transforms the flat sheet row into the format the Graph needs"""
    data_temp = []
    data_press = []
    
    for column_name, config in SENSOR_MAPPING.items():
        if column_name in last_row:
            val = last_row[column_name]
            
            # Pack it into the format Plotly expects
            sensor_data = {
                'Sensor': config['name'], 
                'X': config['x'], 
                'Y': config['y'], 
                'Value': val
            }
            
            if config['type'] == 'temp':
                data_temp.append(sensor_data)
            else:
                data_press.append(sensor_data)
                
    return pd.DataFrame(data_temp), pd.DataFrame(data_press)

# --- 4. VISUALIZATION (Your existing Chart function) ---
def create_combined_chart(df_temp, df_press):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=RIGHT_HAND_X, y=HAND_OUTLINE_Y, mode='lines', line=dict(color='#334155', width=3), hoverinfo='skip', showlegend=False))

    if not df_temp.empty:
        fig.add_trace(go.Scatter(
            x=df_temp['X'], y=df_temp['Y'], mode='markers+text', text=df_temp['Sensor'], textposition="top center",
            marker=dict(size=50, color=df_temp['Value'], colorscale='RdBu_r', cmin=-20, cmax=60, showscale=True,
                colorbar=dict(title="Temp (°C)", orientation='h', y=-0.25, x=0.5, xanchor='center', len=0.9, thickness=15, title_side='top'),
                opacity=0.9, line=dict(width=1, color='white')),
            hovertemplate="<b>%{text}</b><br>Temp: %{marker.color:.1f} °C<extra></extra>", showlegend=False
        ))

    if not df_press.empty:
        fig.add_trace(go.Scatter(
            x=df_press['X'], y=df_press['Y'], mode='markers+text', text=df_press['Sensor'], textposition="bottom center",
            marker=dict(size=50, symbol='circle', color=df_press['Value'], colorscale='Greens', cmin=0, cmax=50, showscale=True,
                colorbar=dict(title="Pressure", orientation='h', y=-0.55, x=0.5, xanchor='center', len=0.9, thickness=15, title_side='top'),
                opacity=0.9, line=dict(width=2, color='yellow')),
            hovertemplate="<b>%{text}</b><br>Pressure: %{marker.color:.1f}<extra></extra>", showlegend=False
        ))

    fig.update_layout(title="Live Sensor Map", xaxis=dict(range=[0, 9], visible=False), yaxis=dict(range=[0, 8], visible=False, scaleanchor="x", scaleratio=1), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=40, b=250), height=700)
    return fig

# --- 5. MAIN LOOP ---
placeholder = st.empty()

while True:
    # A. Fetch Data
    df_all = get_google_sheet_data()
    
    if not df_all.empty:
        # B. Get the very last entry (most recent)
        last_row = df_all.iloc[-1]
        last_time = last_row['Timestamp']
        
        # C. Check Health
        is_online, latency = check_connection_status(last_time)
        
        with placeholder.container():
            # STATUS HEADER
            if is_online:
                st.success(f"🟢 Device Online (Last update: {latency:.0f}s ago)")
                
                # Transform data for graph
                df_temp, df_press = process_data_for_graph(last_row)
                
                # Metrics
                c1, c2 = st.columns(2)
                if not df_temp.empty: c1.metric("Avg Temp", f"{df_temp['Value'].mean():.1f} °C")
                if not df_press.empty: c2.metric("Avg Pressure", f"{df_press['Value'].mean():.1f}")
                
                # Chart
                fig = create_combined_chart(df_temp, df_press)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                # OFFLINE SCREEN
                st.error(f"🔴 DEVICE DISCONNECTED")
                st.warning(f"Last data received: {last_time} ({latency:.0f} seconds ago). Please check ESP32 power.")
                
                # Show last known state (ghost data)
                st.caption("Showing last known data:")
                df_temp, df_press = process_data_for_graph(last_row)
                fig = create_combined_chart(df_temp, df_press)
                st.plotly_chart(fig, use_container_width=True)

    time.sleep(5) # Refresh every 5 seconds (Google API limits)
