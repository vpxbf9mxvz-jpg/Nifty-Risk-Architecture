import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration for an Institutional Look
st.set_page_config(layout="wide", page_title="Nifty 50 Risk Architecture")

# Custom CSS to force the app background to black and ensure text remains visible
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# High-Visibility Titles (White on Black)
st.markdown("<h1 style='text-align: left; color: white;'>Nifty 50 Structural Risk Architecture</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: left; color: #d3d3d3;'>20-Year Topological Analysis: Price Greed vs. VIX Fear (2005-2026)</h3>", unsafe_allow_html=True)

# 2. Data Loading & Quantitative Analysis
@st.cache_data
def load_data():
    # Loading the files uploaded to your GitHub repository
    df_nifty = pd.read_csv("Nifty50_Historical_2005_2026.csv")
    df_vix = pd.read_csv("India_VIX_Historical_2005_2026.csv")
    
    # Standardize column names (remove spaces and capitalize)
    df_nifty.columns = [c.strip().capitalize() for c in df_nifty.columns]
    df_vix.columns = [c.strip().capitalize() for c in df_vix.columns]
    
    # Standardize column labels for consistent logic
    if 'Price' in df_nifty.columns: df_nifty.rename(columns={'Price': 'Close'}, inplace=True)
    if 'Price' in df_vix.columns: df_vix.rename(columns={'Price': 'Vix_Close'}, inplace=True)
    elif 'Close' in df_vix.columns: df_vix.rename(columns={'Close': 'Vix_Close'}, inplace=True)
    
    # Date conversion
    df_nifty['Date'] = pd.to_datetime(df_nifty['Date'], dayfirst=True)
    df_vix['Date'] = pd.to_datetime(df_vix['Date'], dayfirst=True)
    
    # Merge datasets to align Price and Fear
    df = pd.merge(df_nifty, df_vix[['Date', 'Vix_Close']], on='Date', how='inner').sort_values('Date')
    
    # Quantitative Risk Metrics (Z-Scores)
    # Measuring 'Greed' as deviation from 200-day rolling average
    df['Price_Z'] = (df['Close'] - df['Close'].rolling(200).mean()) / df['Close'].rolling(200).std()
    
    # Measuring 'Fear' as volatility elevation
    df['Vix_Z'] = (df['Vix_Close'] - df['Vix_Close'].rolling(200).mean()) / df['Vix_Close'].rolling(200).std()
    
    return df.dropna()

# 3. Visualization Execution
try:
    df = load_data()
    # Downsample slightly for better browser performance during 3D rotation
    df_plot = df.iloc[::2] 

    # Create the 3D Surface Coordinate Grid
    date_indices = np.arange(len(df_plot))
    y_axis = np.linspace(0, 1, 10)
    X, Y = np.meshgrid(date_indices, y_axis)
    
    # Elevation (Z-Axis) = Market Fear (VIX Z-Score)
    # Color Heatmap = Market Greed (Price Z-Score)
    Z_terrain = np.tile(df_plot['Vix_Z'].values, (10, 1))
    Color_Data = np.tile(df_plot['Price_Z'].values, (10, 1))

    fig = go.Figure()

    # Define the 3D Surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_terrain,
        surfacecolor=Color_Data,
        colorscale=[
            [0, '#1a1c23'],      # Deep Midnight (Stability)
            [0.85, '#e74c3c'],    # Vibrant Red (Euphoria)
            [1.0, '#ff0000']      # Pure Red (Structural Risk)
        ],
        colorbar=dict(title="Price Greed (Z)", thickness=20, tickfont=dict(color='white')),
    ))

    # Styling the Plotly Layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        scene=dict(
            xaxis=dict(
                title='Timeline', 
                tickvals=date_indices[::500], 
                ticktext=df_plot['Date'].dt.strftime('%Y').values[::500],
                color='white'
            ),
            yaxis=dict(visible=False),
            zaxis=dict(title='Fear Elevation (VIX Z)', color='white'),
            camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2))
        ),
        height=850,
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Execution Error: {e}")
