import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import io

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Mixed Sensor Dashboard")

st.title("🖐️ Mixed Sensor Dashboard")
st.markdown("Visualizing **Temperature** and **Pressure** on a single hand.")

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
# We split them into two groups: Temperature Sensors and Pressure Sensors

TEMP_SENSORS = {
    'Middle':   {'x': 4.5, 'y': 7.0},
    'Ring Tip': {'x': 6.0, 'y': 6.2}
}

PRESSURE_SENSORS = {
    'Ring Base': {'x': 5.8, 'y': 4.5}
}

# --- 4. DATA GENERATION ---

def get_data():
    """Generates random data for the 3 specific sensors."""
    data_temp = []
    data_press = []
    t = time.time()
    
    # Generate Temperature Data
    for name, coords in TEMP_SENSORS.items():
        # Random Temp: -20 to 60
        base = 20 + np.sin(t + coords['x']) * 35 
        val = np.clip(base + np.random.normal(0, 2), -20, 60)
        data_temp.append({
            'Sensor': name, 'X': coords['x'], 'Y': coords['y'], 'Value': val
        })

    # Generate Pressure Data
    for name, coords in PRESSURE_SENSORS.items():
        # Random Pressure: 0 to 50
        base = np.abs(np.cos(t * 1.5 + coords['y'])) * 45
        val = np.clip(base + np.random.normal(0, 2), 0, 50)
        data_press.append({
            'Sensor': name, 'X': coords['x'], 'Y': coords['y'], 'Value': val
        })
            
    return pd.DataFrame(data_temp), pd.DataFrame(data_press)

def convert_to_excel(df_t, df_p):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_t.empty:
            df_t.to_excel(writer, index=False, sheet_name='Temperature')
        if not df_p.empty:
            df_p.to_excel(writer, index=False, sheet_name='Pressure')
    return output.getvalue()

# --- 5. VISUALIZATION ---

def create_combined_chart(df_temp, df_press):
    fig = go.Figure()

    # 1. Hand Outline
    fig.add_trace(go.Scatter(
        x=RIGHT_HAND_X, 
        y=HAND_OUTLINE_Y,
        mode='lines',
        line=dict(color='#334155', width=3),
        hoverinfo='skip',
        showlegend=False
    ))

    # 2. Temperature Sensors (Red/Blue Gradient)
    if not df_temp.empty:
        fig.add_trace(go.Scatter(
            x=df_temp['X'],
            y=df_temp['Y'],
            mode='markers+text',
            text=df_temp['Sensor'],
            textposition="top center",
            marker=dict(
                size=50, 
                color=df_temp['Value'],
                colorscale='RdBu_r',
                cmin=-20, cmax=60,
                showscale=True,
                # Colorbar Position 1 (Right side)
                colorbar=dict(title="Temp (°C)", x=1.0, len=0.7, y=0.5),
                opacity=0.9,
                line=dict(width=1, color='white')
            ),
            hovertemplate="<b>%{text}</b><br>Temp: %{marker.color:.1f} °C<extra></extra>",
            showlegend=False
        ))

    # 3. Pressure Sensors (Green Gradient)
    if not df_press.empty:
        fig.add_trace(go.Scatter(
            x=df_press['X'],
            y=df_press['Y'],
            mode='markers+text',
            text=df_press['Sensor'],
            textposition="bottom center", # Text below to avoid overlap
            marker=dict(
                size=50,
                symbol='circle', # You could change shape if you wanted
                color=df_press['Value'],
                colorscale='Greens',
                cmin=0, cmax=50,
                showscale=True,
                # Colorbar Position 2 (Further Right)
                colorbar=dict(title="Pressure", x=1.15, len=0.7, y=0.5),
                opacity=0.9,
                line=dict(width=2, color='yellow') # Yellow border to distinguish Pressure
            ),
            hovertemplate="<b>%{text}</b><br>Pressure: %{marker.color:.1f}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title="Live Sensor Map",
        xaxis=dict(range=[0, 9], visible=False),
        yaxis=dict(range=[0, 8], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=100, t=40, b=10), # Extra right margin for colorbars
        height=600
    )
    return fig

# --- 6. MAIN LOOP ---

placeholder = st.empty()
dl_btn_spot = st.sidebar.empty()

while True:
    df_temp, df_press = get_data()
    unique_key = int(time.time() * 1000)

    # Excel Download
    excel_data = convert_to_excel(df_temp, df_press)
    dl_btn_spot.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name=f"mixed_sensor_data_{unique_key}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{unique_key}"
    )

    with placeholder.container():
        # KPI Metrics
        c1, c2 = st.columns(2)
        if not df_temp.empty:
            avg_t = df_temp['Value'].mean()
            c1.metric("Avg Temp", f"{avg_t:.1f} °C")
        
        if not df_press.empty:
            avg_p = df_press['Value'].mean()
            c2.metric("Avg Pressure", f"{avg_p:.1f}")

        st.divider()

        # Single Combined Chart
        fig = create_combined_chart(df_temp, df_press)
        st.plotly_chart(fig, use_container_width=True, key=f"main_chart_{unique_key}")

    time.sleep(0.5)
