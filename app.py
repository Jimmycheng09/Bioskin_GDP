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
                # --- FIX: Move to Bottom (Horizontal) ---
                colorbar=dict(
                    title="Temp (°C)", 
                    orientation='h',  # Horizontal
                    y=-0.15,          # Position below the chart
                    x=0.5,            # Center it
                    xanchor='center',
                    len=0.9,          # Length relative to chart width
                    thickness=15,
                    title_side='top'  # Title above the bar
                ),
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
            textposition="bottom center", 
            marker=dict(
                size=50,
                symbol='circle', 
                color=df_press['Value'],
                colorscale='Greens',
                cmin=0, cmax=50,
                showscale=True,
                # --- FIX: Move to Bottom (Stacked below Temp) ---
                colorbar=dict(
                    title="Pressure", 
                    orientation='h',  # Horizontal
                    y=-0.35,          # Position further below Temp bar
                    x=0.5,            # Center it
                    xanchor='center',
                    len=0.9,
                    thickness=15,
                    title_side='top'
                ),
                opacity=0.9,
                line=dict(width=2, color='yellow') 
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
        # --- FIX: Increase Bottom Margin for the new bars ---
        margin=dict(l=10, r=10, t=40, b=180), 
        height=600
    )
    return fig
