import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Bioskin Dashboard")
st.title("🖐️ Bioskin Sensor Dashboard")

# Hand Outline Data
RIGHT_HAND_X = [4.50, 4.00, 3.50, 3.00, 2.50, 2.00, 1.50, 1.20, 1.00, 0.90, 0.85, 0.90, 1.10, 1.40, 1.70, 2.00, 2.30, 2.50, 2.60, 2.70, 2.80, 2.90, 3.05, 3.20, 3.30, 3.40, 3.50, 3.70, 3.80, 3.90, 4.10, 4.30, 4.50, 4.70, 4.90, 5.00, 5.10, 5.20, 5.40, 5.50, 5.60, 5.80, 6.00, 6.20, 6.40, 6.50, 6.60, 6.80, 6.90, 7.10, 7.30, 7.50, 7.70, 7.80, 7.85, 7.80, 7.70, 7.50, 7.20, 6.80, 6.20, 5.50, 5.00, 4.50]
HAND_OUTLINE_Y = [0.00, 0.05, 0.15, 0.30, 0.55, 0.90, 1.40, 1.80, 2.50, 3.20, 3.80, 4.20, 4.40, 4.40, 4.20, 3.80, 3.20, 2.90, 3.50, 5.00, 6.00, 6.80, 7.00, 6.80, 6.00, 5.00, 3.90, 4.50, 6.00, 7.00, 7.50, 7.60, 7.50, 7.00, 6.00, 5.00, 4.50, 4.10, 4.80, 5.50, 6.20, 6.70, 6.80, 6.70, 6.20, 5.50, 4.50, 3.80, 4.80, 5.20, 5.40, 5.20, 4.80, 4.20, 3.50, 3.00, 2.20, 1.50, 1.00, 0.60, 0.30, 0.10, 0.05, 0.00]

# --- 2. DATA FETCHING ---
def get_data_from_sheet():
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # Read the sheet. ttl=2 means "refresh cache every 2 seconds"
        df = conn.read(ttl=2)
        return df
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame()

def process_bioskin_data(df):
    """
    Looks specifically for ID 2 (Temp) and ID 3 (Pressure)
    based on your screenshot structure.
    """
    data_temp = []
    data_press = []

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # --- 1. GET TEMPERATURE (ID = 2) ---
    # We filter the sheet for rows where 'id' is 2
    temp_rows = df[df['id'] == 2]
    
    if not temp_rows.empty:
        # Get the very last reading
        last_reading = temp_rows.iloc[-1]
        val = last_reading['val_c'] # Column C in your image
        
        data_temp.append({
            'Sensor': 'Middle Finger', # Naming it arbitrarily
            'X': 4.5, 'Y': 7.0,        # Location on hand map
            'Value': val
        })

    # --- 2. GET PRESSURE (ID = 3) ---
    # We filter the sheet for rows where 'id' is 3
    press_rows = df[df['id'] == 3]
    
    if not press_rows.empty:
        last_reading = press_rows.iloc[-1]
        val = last_reading['val_d'] # Column D in your image
        
        # Scale it down? 1140 is huge for the graph (0-50 range).
        # Let's divide by 20 to fit the color scale, or adjust the scale.
        # For now, I will map it raw but change the graph max limit.
        
        data_press.append({
            'Sensor': 'Ring Base', 
            'X': 5.8, 'Y': 4.5, 
            'Value': val
        })

    return pd.DataFrame(data_temp), pd.DataFrame(data_press)

# --- 3. VISUALIZATION ---
def create_chart(df_temp, df_press):
    fig = go.Figure()
    
    # Hand Outline
    fig.add_trace(go.Scatter(x=RIGHT_HAND_X, y=HAND_OUTLINE_Y, mode='lines', line=dict(color='#334155', width=3), hoverinfo='skip', showlegend=False))

    # Temp Points
    if not df_temp.empty:
        fig.add_trace(go.Scatter(
            x=df_temp['X'], y=df_temp['Y'], mode='markers+text', text=df_temp['Value'], textposition="top center",
            marker=dict(size=50, color=df_temp['Value'], colorscale='RdBu_r', cmin=20, cmax=40, showscale=True,
                colorbar=dict(title="Temp (°C)", orientation='h', y=-0.25, x=0.5, len=0.9, thickness=15),
                line=dict(width=1, color='white')),
            showlegend=False
        ))

    # Pressure Points (Updated Range for 1140+ values)
    if not df_press.empty:
        fig.add_trace(go.Scatter(
            x=df_press['X'], y=df_press['Y'], mode='markers+text', text=df_press['Value'], textposition="bottom center",
            marker=dict(size=50, symbol='circle', color=df_press['Value'], colorscale='Greens', 
                cmin=0, cmax=2000, # UPDATED SCALE: 0 to 2000 because your screenshot shows 1140
                showscale=True,
                colorbar=dict(title="Pressure", orientation='h', y=-0.55, x=0.5, len=0.9, thickness=15),
                line=dict(width=2, color='yellow')),
            showlegend=False
        ))

    fig.update_layout(
        title="Bioskin Live Map", 
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1), 
        margin=dict(l=10, r=10, t=40, b=250), height=700
    )
    return fig

# --- 4. MAIN LOOP ---
placeholder = st.empty()

while True:
    df = get_data_from_sheet()
    
    # Process logic
    df_temp, df_press = process_bioskin_data(df)
    
    with placeholder.container():
        if df.empty:
            st.warning("Waiting for Google Sheet connection...")
        else:
            # Metrics
            c1, c2 = st.columns(2)
            if not df_temp.empty: 
                c1.metric("Temperature", f"{df_temp['Value'].iloc[0]} °C")
            if not df_press.empty: 
                c2.metric("Pressure", f"{df_press['Value'].iloc[0]}")
            
            # Graph
            fig = create_chart(df_temp, df_press)
            st.plotly_chart(fig, use_container_width=True)
            
    time.sleep(3) # Refresh speed
