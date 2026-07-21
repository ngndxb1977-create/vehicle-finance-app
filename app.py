import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_price_data():
    return pd.read_excel("Price_LIST_RMC_ACCESSORIES.xlsx")

@st.cache_data
def load_finance_data():
    return pd.read_excel("Vehicle Finance Calculator.xlsx")

price_df = load_price_data()
finance_df = load_finance_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("Vehicle Selection")

selected_my = st.sidebar.selectbox("Model Year (MY)", sorted(price_df["MY"].unique()))
selected_model = st.sidebar.selectbox("Model Name", sorted(price_df["Model_Name"].unique()))
selected_code = st.sidebar.selectbox("Model Code", sorted(price_df["Model_Code"].unique()))

# Filter based on MY, Model Name, Model Code
filtered_df = price_df[
    (price_df["MY"] == selected_my) &
    (price_df["Model_Name"] == selected_model) &
    (price_df["Model_Code"] == selected_code)
]

# RMC & Accessories dropdowns based on filtered data
selected_rmc = st.sidebar.selectbox("RMC", sorted(filtered_df["RMC"].unique()))
selected_accessory = st.sidebar.selectbox("Accessories", sorted(filtered_df["Accessories"].unique()))

# -----------------------------
# Finance Logic
# -----------------------------
# Extract finance parameters
interest_rate = finance_df.loc[0, "Interest_Rate"]
tenure = int(finance_df.loc[0, "Tenure"])
down_payment_pct = finance_df.loc[0, "Down_Payment_Percentage"]

# Calculate values
vehicle_price = selected_rmc + selected_accessory
down_payment = vehicle_price * down_payment_pct
loan_amount = vehicle_price - down_payment

monthly_rate = interest_rate / 12

# EMI Formula
emi = loan_amount * (monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)

# -----------------------------
# Display Output
# -----------------------------
st.title("Vehicle Finance Calculator")

st.write("### Selected Vehicle Details")
st.write(f"**Model Year:** {selected_my}")
st.write(f"**Model Name:** {selected_model}")
st.write(f"**Model Code:** {selected_code}")

st.write("### Price Breakdown")
st.write(f"**RMC:** {selected_rmc:,.2f}")
st.write(f"**Accessories:** {selected_accessory:,.2f}")
st.write(f"**Total Vehicle Price:** {vehicle_price:,.2f}")

st.write("### Finance Calculation")
st.write(f"**Down Payment ({down_payment_pct*100:.0f}%):** {down_payment:,.2f}")
st.write(f"**Loan Amount:** {loan_amount:,.2f}")
st.write(f"**Monthly EMI:** {emi:,.2f}")

st.success("Calculation Completed Successfully")
