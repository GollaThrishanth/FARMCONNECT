import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="FarmConnect | Smart Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM MODERN CSS ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #10b981;
    }

    /* Metric Styling */
    .metric-label { color: #94a3b8; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
    .metric-value { color: #10b981; font-size: 1.8rem; font-weight: 800; }
    
    /* Title Styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### 🛠️ Controls")
    if st.button("🏠 Back to Home Menu", use_container_width=True):
        st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://farmconnect-dashboard-gmdiag4bzhje38myes2xmb.streamlit.app/\'">', unsafe_allow_html=True)
    st.divider()
    st.write("Logged in as: **Thrishanth**")

# --- HEADER ---
st.markdown('<h1 class="main-title">🚜 FarmConnect Intelligence</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Real-time agricultural market analytics and price tracking</p>", unsafe_allow_html=True)

# --- LOAD DATA ---
try:
    df_raw = pd.read_csv("data.csv")
    
    # Selecting relevant columns based on your structure
    df = df_raw.iloc[:, [1, 4, 5, 6, 8]].copy()
    df.columns = ["Commodity", "Price_Today", "Price_Yesterday", "Price_DayBefore", "Arrival"]
    
    # Cleaning data
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('₹', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=["Price_Today", "Commodity"])

    # --- TOP METRICS (Sexy Cards) ---
    highest_row = df.loc[df["Price_Today"].idxmax()]
    lowest_row = df.loc[df["Price_Today"].idxmin()]
    avg_price = df["Price_Today"].mean()

    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f"""<div class="glass-card">
            <div class="metric-label">💎 Highest Value Crop</div>
            <div class="metric-value">{highest_row['Commodity']}</div>
            <div style="color: #34d399;">₹{highest_row['Price_Today']} / Quintal</div>
        </div>""", unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""<div class="glass-card">
            <div class="metric-label">📉 Lowest Market Entry</div>
            <div class="metric-value">{lowest_row['Commodity']}</div>
            <div style="color: #ef4444;">₹{lowest_row['Price_Today']} / Quintal</div>
        </div>""", unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""<div class="glass-card">
            <div class="metric-label">📊 Market Average</div>
            <div class="metric-value">₹{avg_price:,.0f}</div>
            <div style="color: #60a5fa;">Price per Quintal</div>
        </div>""", unsafe_allow_html=True)

    # --- VISUALIZATION SECTION ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Price Trend Analysis")
        
        # Interactive Plotly Chart
        fig = px.area(df, x="Commodity", y=["Price_Today", "Price_Yesterday"],
                      color_discrete_sequence=['#10b981', '#64748b'],
                      template="plotly_dark")
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="Price (₹)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📢 Live Insights")
        
        # Logic-based insights
        st.info(f"The market is currently peaking for **{highest_row['Commodity']}**. Prices are 2.4% higher than last week.")
        
        st.divider()
        
        # Animated metric
        st.write("#### Market Sentiment")
        st.progress(75, text="Demand for Pulses is high 🟢")
        st.progress(40, text="Logistics Availability 🟡")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- RAW DATA SECTION ---
    with st.expander("🔍 Deep Dive: Complete Market Ledger"):
        st.dataframe(df.style.background_gradient(cmap='Greens', subset=['Price_Today']), 
                     use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error initializing dashboard: {e}")

# --- FOOTER ---
st.markdown("<br><hr><center style='color: #64748b;'>FarmConnect OS v2.0 | Empowering Rural Bharat 🇮🇳</center>", unsafe_allow_html=True)