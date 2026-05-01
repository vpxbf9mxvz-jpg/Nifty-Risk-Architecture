import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration for a Professional Institutional Look
st.set_page_config(layout="wide", page_title="Nifty 50 Risk Architecture")

# Injecting a dark theme feel
st.markdown("<style>.main {background-color: #000000;}</style>", unsafe_allow_index=True)

st.title("Nifty 50 Structural Risk Architecture")
st.write("20-Year Topological Analysis: Price Greed vs. VIX Fear (2005-2026)")

# 2. Data Loading & Quantitative Analysis
@st.cache_data
def load_data():
    # These point to the files you uploaded to your GitHub repository
    df_nifty = pd.read_csv("Nifty50_Historical_2005_2026.csv")
    df_vix = pd.read_csv("India_VIX_Historical_2005_2026.csv")
    
    # Standardize column names to remove any leading/trailing spaces
    df_nifty.columns = [c.strip().capitalize() for c in df_nifty.columns]
    df_vix.columns = [c.strip().capitalize() for c in df_vix.columns]
    
    # Handling variations in CSV headers
    if 'Price' in df_nifty.columns: df_nifty.rename(columns={'Price': 'Close'}, inplace=True)
    if 'Price' in df_vix.columns: df_vix.rename(columns={'Price': 'Vix_Close'}, inplace=True)
    elif 'Close' in df_vix.columns: df_vix.rename(columns={'Close': 'Vix_Close'}, inplace=True)
    
    # Date conversion for alignment
    df_nifty['Date'] = pd.to_datetime(df_nifty['Date'], dayfirst=True)
    df_vix['Date'] = pd.to_datetime(df_vix['Date'], dayfirst=True)
    
    # Merge datasets on the Date column
    df = pd.merge(df_nifty, df_vix[['Date', 'Vix_Close']], on='Date', how='inner').sort_values('Date')
    
    # --- Quantitative Risk Metrics (Z-Scores) ---
    # Price Z-Score measures "Greed" (deviation from the 200-day mean)
    df['Price_Z'] = (df['Close'] - df['Close'].rolling(200).mean()) / df['Close'].rolling(200).std()
    
    # VIX Z-Score measures "Fear" (volatility elevation)
    df['Vix_Z'] = (df['Vix_Close'] - df['Vix_Close'].rolling(200).mean()) / df['Vix_Close'].rolling(200).std()
    
    return df.dropna()

# 3. Visualization Logic
try:
    df = load_data()
    # Downsample slightly for buttery-smooth 3D rotation in the browser
    df_plot = df.iloc[::2] 

    # Create the 3D Coordinate Grid
    date_indices = np.arange(len(df_plot))
    y_axis = np.linspace(0, 1, 10)
    X, Y = np.meshgrid(date_indices, y_axis)
    
    # Z-Axis (Height) is determined by VIX Fear
    # Color is determined by Price Greed (Euphoria)
    Z_terrain = np.tile(df_plot['Vix_Z'].values, (10, 1))
    Color_Data = np.tile(df_plot['Price_Z'].values, (10, 1))

    fig = go.Figure()

    # The 3D Risk Surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_terrain,
        surfacecolor=Color_Data,
        colorscale=[
            [0, '#1a1c23'],      # Deep Midnight (Stable/Fearless)
            [0.85, '#e74c3c'],    # Vibrant Red (Statistical Euphoria)
            [1.0, '#ff0000']      # Pure Red (Structural Crash Risk)
        ],
        colorbar=dict(title="Price Greed (Z-Score)", thickness=20)
    ))

    # Layout Styling for LinkedIn Visuals
    fig.update_layout(
        template="plotly_dark",
        scene=dict(
            xaxis=dict(title='Timeline', tickvals=date_indices[::500], 
                       ticktext=df_plot['Date'].dt.strftime('%Y').values[::500]),
            yaxis=dict(visible=False),
            zaxis=dict(title='Fear Elevation (VIX Z)'),
            camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2))
        ),
        height=800,
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Critical Error: {e}")
    st.info("Check if your CSV filenames match exactly in GitHub.")
