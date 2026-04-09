import streamlit as st
import joblib

model = joblib.load("model.pkl")

st.title("🏠 House Price Prediction App")

area = st.number_input("Enter Area (sq ft)")
bedrooms = st.number_input("Enter Bedrooms")

if st.button("Predict"):
    prediction = model.predict([[area, bedrooms]])
    st.success(f"Estimated Price: ₹{prediction[0]:,.2f}")