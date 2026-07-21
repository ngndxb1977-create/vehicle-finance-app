import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_price_data():
    df = pd.read_excel("Price_LIST_RMC_ACCESSORIES.xlsx")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_finance_data():
    df = pd.read_excel("Vehicle Finance Calculator.xlsx")
    df.columns = df.columns.str.strip()
    return df

price_df = load_price_data()
finance_df = load_finance_data()

# ---------------------------------------------------------
# Debug: Show columns
# ---------------------------------------------------------
st.write("### Columns Found in Price List File")
st.write(price_df.columns.tolist())

st.write("### Columns Found in Finance Calculator File")
st.write(finance_df.columns.tolist())

# ---------------------------------------------------------
# Sidebar Filters (based on actual price list columns)
# ---------------------------------------------------------
st.sidebar.title("Vehicle Selection")

selected_description = st.sidebar.selectbox(
    "Description",
    sorted(price_df["Description"].dropna().unique())
)

filtered_desc = price_df[price_df["Description"] == selected_description]

selected_variant = st.sidebar.selectbox(
    "Variant (SAP)",
    sorted(filtered_desc["VARIANT AS IN SAP"].dropna().unique())
)

filtered_variant = filtered_desc[filtered_desc["VARIANT AS IN SAP"] == selected_variant]

selected_option = st.sidebar.selectbox(
    "Option Code",
    sorted(filtered_variant["OTPION CODE"].dropna().unique())
)

filtered_final = filtered_variant[filtered_variant["OTPION CODE"] == selected_option]

if filtered_final.empty:
    st.error("❌ No matching vehicle found. Please adjust your selections.")
    st.stop()

vehicle_price = float(filtered_final["PRICE"].values[0])

# ---------------------------------------------------------
# STOP HERE — DO NOT CALCULATE FINANCE UNTIL WE KNOW COLUMNS
# ---------------------------------------------------------
st.warning("Finance calculation paused — waiting for correct column names from your finance file.")

st.info("Please look at the 'Columns Found in Finance Calculator File' above and tell me the exact column names.")

