import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np

st.set_page_config(page_title="FarmConnect Dashboard", layout="wide")

# SIDEBAR NAVIGATION
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Back to Home Menu"):
    # Redirecting back to the Flask Menu route
    st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://farmconnect-dashboard-gmdiag4bzhje38myes2xmb.streamlit.app/\'">', unsafe_allow_html=True)

st.title("🚜 FarmConnect Smart Dashboard")

# --- NEW: AI PRICE PREDICTION SECTION ---
st.markdown("---")
st.subheader("🔮 AI Smart Price Predictor")
st.write("Predict the future market price for your crop based on current trends.")

try:
    # Load the trained AI models created by your train_model.py
    model = joblib.load('crop_price_model.pkl')
    le_commodity = joblib.load('commodity_encoder.pkl')
    
    # Check if state encoder exists (optional depending on your train_model.py run)
    try:
        le_state = joblib.load('state_encoder.pkl')
        has_state = True
    except:
        has_state = False

    col_a, col_b = st.columns(2)
    
    with col_a:
        user_crop = st.selectbox("Select Your Crop", le_commodity.classes_)
    
    with col_b:
        if has_state:
            user_state = st.selectbox("Select Your State", le_state.classes_)
        else:
            st.info("State-specific AI training pending; predicting based on national trends.")

    if st.button("Calculate Predicted Price"):
        # Process input for the model
        crop_idx = le_commodity.transform([user_crop])[0]
        
        if has_state:
            state_idx = le_state.transform([user_state])[0]
            prediction = model.predict([[crop_idx, state_idx]])
        else:
            prediction = model.predict([[crop_idx]])

        # Convert from Quintal (100kg) to KG (Prediction / 100)
        price_per_kg = prediction[0] / 100
        
        st.success(f"### Predicted Market Price: ₹{price_per_kg:.2f} / kg")
        st.caption(f"Trend Analysis for {user_crop} suggests this price for the upcoming week.")

except Exception as e:
    st.warning("AI Model not detected. Ensure 'crop_price_model.pkl' and 'commodity_encoder.pkl' are uploaded to GitHub.")

st.markdown("---")

# --- ORIGINAL DASHBOARD LOGIC (UNTOUCHED & REFINED) ---
try:
    # Loading your data.csv
    df_raw = pd.read_csv("data.csv")
    
    # Selecting columns: Commodity, Price Today, Price Yesterday, Price Day Before, Arrival
    df = df_raw.iloc[:, [1, 4, 5, 6, 8]].copy()
    df.columns = ["Commodity", "Price_Today", "Price_Yesterday", "Price_DayBefore", "Arrival"]
    
    # Cleaning: Removing commas from prices so they become numbers correctly
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace('₹', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=["Price_Today", "Commodity"])

    # Metrics
    highest = df.loc[df["Price_Today"].idxmax()]
    col1, col2 = st.columns(2)
    col1.metric("Highest Price Crop", highest['Commodity'], f"₹{highest['Price_Today']}")
    
    # Chart
    st.subheader("Price Trend Analysis")
    fig = px.line(df, x="Commodity", y=["Price_Today", "Price_Yesterday"], markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Raw Market Data")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error loading visualization data: {e}")