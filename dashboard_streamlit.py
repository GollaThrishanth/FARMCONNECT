import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FarmConnect Dashboard", layout="wide")

# SIDEBAR NAVIGATION
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Back to Home Menu"):
    # Redirecting back to the Flask Menu route
    st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://farmconnect-dashboard-gmdiag4bzhje38myes2xmb.streamlit.app/\'">', unsafe_allow_html=True)

st.title("🚜 FarmConnect Smart Dashboard")

# Load Data
try:
    df_raw = pd.read_csv("data.csv")
    df = df_raw.iloc[:, [1, 4, 5, 6, 8]].copy()
    df.columns = ["Commodity", "Price_Today", "Price_Yesterday", "Price_DayBefore", "Arrival"]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    # Metrics
    highest = df.loc[df["Price_Today"].idxmax()]
    col1, col2 = st.columns(2)
    col1.metric("Highest Price Crop", highest['Commodity'], f"₹{highest['Price_Today']}")
    
    # Chart
    st.subheader("Price Trend Analysis")
    fig = px.line(df, x="Commodity", y=["Price_Today", "Price_Yesterday"], markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading data: {e}")