import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import re

# Page config
st.set_page_config(page_title="SR3-SR1 Structure Analyzer", layout="wide", page_icon="📊")

# FRED API Key
FRED_API_KEY = 'ec39710b3961ff09572460cb2548361e'

# Title
st.title("📊 SR3-SR1 Structure Analyzer")
st.markdown("Upload historical data and analyze structure pricing with market context")

# File path
DATA_FILE_PATH = r"Historical Data Sheet.csv"

# Sidebar info
with st.sidebar:
    st.header("Data Source")
    st.info(f"📁 Loading data from:\n{DATA_FILE_PATH}")
    
    if st.button("🔄 Reload Data"):
        st.cache_data.clear()
        st.rerun()

# Functions
@st.cache_data
def load_data(file_path):
    """Load and parse CSV data from file path"""
    try:
        df = pd.read_csv(file_path)
        # Handle different date formats
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        # Remove any rows with invalid dates
        df = df.dropna(subset=['Timestamp'])
        return df
    except FileNotFoundError:
        st.error(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

def get_analysis_period(structure_name):
    """Extract contract month and calculate analysis period"""
    # Handle both "SR3-SR1 Jun25" and "SR3-SR1Jun25" formats
    match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d{2})', structure_name)
    if not match:
        return None, None
    
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    
    month = month_map[match.group(1)]
    year = 2000 + int(match.group(2))
    
    # Set expiry to last day of the contract month
    if month == 12:
        expiry_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        expiry_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    start_date = expiry_date - timedelta(days=240)  # ~8 months
    
    return start_date, expiry_date

@st.cache_data
def fetch_sofr_data(start_date, end_date):
    """Fetch SOFR data from FRED"""
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'SOFR',
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.rename(columns={'value': 'SOFR'})
            return df[['date', 'SOFR']]
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching SOFR data: {e}")
        return pd.DataFrame()

@st.cache_data
def fetch_fed_decisions(start_date, end_date):
    """Fetch Fed Funds Target Rate Upper Limit to identify rate decisions"""
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': 'DFEDTARU',  # Fed Funds Target Rate - Upper Limit
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            
            # Detect rate changes
            df['rate_change'] = df['value'].diff()
            decisions = df[df['rate_change'].abs() > 0.01].copy()
            decisions = decisions.rename(columns={'value': 'rate'})
            
            return decisions[['date', 'rate', 'rate_change']]
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching Fed data: {e}")
        return pd.DataFrame()

@st.cache_data
def fetch_economic_data(series_id, start_date, end_date, name):
    """Fetch economic indicator from FRED - DEPRECATED"""
    return pd.DataFrame()

def calculate_statistics(series):
    """Calculate statistical measures"""
    return {
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'current': series.iloc[-1] if len(series) > 0 else np.nan,
        'z_score': (series.iloc[-1] - series.mean()) / series.std() if len(series) > 0 else np.nan
    }

# Main app
try:
    # Load data
    df = load_data(DATA_FILE_PATH)
    
    if df is not None:
        st.success(f"✓ Loaded {len(df)} rows of data")
        
        # Structure selection
        structures = [col for col in df.columns if col != 'Timestamp' and not col.startswith('Unnamed')]
        selected_structure = st.selectbox("Select Structure to Analyze", structures, index=0 if structures else None)
    
    if selected_structure:
        # Get analysis period
        start_date, end_date = get_analysis_period(selected_structure)
        
        if start_date and end_date:
            st.info(f"📅 Analysis Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")
            
            # Filter data
            mask = (df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)
            filtered_df = df[mask].copy()
            
            # Calculate statistics
            stats = calculate_statistics(filtered_df[selected_structure])
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Value", f"{stats['current']:.4f}")
            
            with col2:
                z_color = "🔴" if stats['z_score'] > 1.5 else "🟢" if stats['z_score'] < -1.5 else "🔵"
                st.metric("Z-Score", f"{z_color} {stats['z_score']:.2f}")
            
            with col3:
                st.markdown(f"**Mean**")
                st.markdown(f"## {stats['mean']:.4f}")
            
            with col4:
                st.markdown(f"**Median / Std Dev**")
                st.markdown(f"## {stats['median']:.4f}")
                st.markdown(f"**± {stats['std']:.4f}**")
            
            # Fetch market data
            with st.spinner("Fetching market data from FRED..."):
                sofr_data = fetch_sofr_data(start_date, end_date)
                fed_decisions = fetch_fed_decisions(start_date, end_date)
            
            # Merge data
            analysis_df = filtered_df[['Timestamp', selected_structure]].copy()
            analysis_df = analysis_df.rename(columns={'Timestamp': 'date'})
            
            if not sofr_data.empty:
                analysis_df = pd.merge(analysis_df, sofr_data, on='date', how='left')
            
            # Create main chart
            st.subheader("📈 Structure Price & SOFR")
            
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                subplot_titles=('Structure Price & SOFR', 'Price Distribution'),
                vertical_spacing=0.12,
                specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
            )
            
            # SOFR on secondary axis (plot first so it's in background)
            if 'SOFR' in analysis_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=analysis_df['date'],
                        y=analysis_df['SOFR'],
                        name='SOFR %',
                        line=dict(color='#10B981', width=1.5),
                        opacity=0.6
                    ),
                    row=1, col=1, secondary_y=True
                )
            
            # Structure price on primary axis
            fig.add_trace(
                go.Scatter(
                    x=analysis_df['date'],
                    y=analysis_df[selected_structure],
                    name='Structure Price',
                    line=dict(color='#3B82F6', width=2.5)
                ),
                row=1, col=1, secondary_y=False
            )
            
            # Mean line
            fig.add_trace(
                go.Scatter(
                    x=analysis_df['date'],
                    y=[stats['mean']] * len(analysis_df),
                    name='Mean',
                    line=dict(color='red', dash='dash', width=2)
                ),
                row=1, col=1, secondary_y=False
            )
            
            # Add Fed decision markers using shapes instead of vline
            if not fed_decisions.empty:
                for _, decision in fed_decisions.iterrows():
                    color = 'red' if decision['rate_change'] > 0 else 'green'
                    decision_date = pd.Timestamp(decision['date'])
                    
                    fig.add_shape(
                        type="line",
                        x0=decision_date, x1=decision_date,
                        y0=0, y1=1,
                        yref="paper",
                        line=dict(color=color, dash='dot', width=2),
                        row=1, col=1
                    )
                    
                    # Add annotation
                    fig.add_annotation(
                        x=decision_date,
                        y=1.05,
                        yref="paper",
                        text=f"Fed {'+' if decision['rate_change'] > 0 else ''}{decision['rate_change']:.2f}%",
                        showarrow=False,
                        font=dict(size=9, color=color),
                        row=1, col=1
                    )
            
            # Histogram
            fig.add_trace(
                go.Histogram(
                    x=analysis_df[selected_structure],
                    name='Distribution',
                    marker_color='#3B82F6',
                    opacity=0.7,
                    nbinsx=30
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_xaxes(title_text="Date", row=1, col=1)
            fig.update_xaxes(title_text="Structure Value", row=2, col=1)
            fig.update_yaxes(title_text="Structure Value", row=1, col=1, secondary_y=False)
            fig.update_yaxes(title_text="SOFR %", row=1, col=1, secondary_y=True)
            fig.update_yaxes(title_text="Frequency", row=2, col=1)
            
            fig.update_layout(height=800, showlegend=True, hovermode='x unified')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Fed Decisions Section
            if not fed_decisions.empty:
                st.subheader("🏛️ Fed Rate Decisions")
                for _, decision in fed_decisions.iterrows():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(decision['date'].strftime('%B %d, %Y'))
                    with col2:
                        st.write(f"Rate: {decision['rate']:.2f}%")
                    with col3:
                        change_color = "🔴" if decision['rate_change'] > 0 else "🟢"
                        st.write(f"{change_color} {decision['rate_change']:+.2f}%")
            
            # Value Assessment
            st.subheader("💡 Value Assessment")
            
            if stats['z_score'] > 1.5:
                st.error(f"⚠️ **Rich Territory**: Structure is trading {abs(stats['z_score']):.1f} standard deviations above mean")
            elif stats['z_score'] < -1.5:
                st.success(f"✅ **Cheap Territory**: Structure is trading {abs(stats['z_score']):.1f} standard deviations below mean")
            else:
                st.info(f"◈ **Fair Value Range**: Structure is trading within normal range ({stats['z_score']:.1f} std dev from mean)")
            
            # Download processed data
            st.subheader("💾 Download Data")
            csv = analysis_df.to_csv(index=False)
            st.download_button(
                label="Download Analysis Data as CSV",
                data=csv,
                file_name=f"{selected_structure}_analysis.csv",
                mime="text/csv"
            )
            
        else:
            st.error("Could not parse structure name. Please ensure it follows the format: SR3-SR1 MonYY")
    else:
        st.error("Failed to load data file. Please check the file path.")
        
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please check that the data file exists at the specified path")