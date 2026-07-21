import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_price_data():
    df = pd.read_excel("Price_LIST_RMC_ACCESSORIES.xlsx")
    df.columns = df.columns.str.strip()  # Clean column names
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

# ---------------------------------------------------------
# Sidebar Filters (based on actual columns)
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
# Finance Logic
# ---------------------------------------------------------
interest_rate = float(finance_df.loc[0, "Interest_Rate"])
tenure = int(finance_df.loc[0, "Tenure"])
down_payment_pct = float(finance_df.loc[0, "Down_Payment_Percentage"])

down_payment = vehicle_price * down_payment_pct
loan_amount = vehicle_price - down_payment

monthly_rate = interest_rate / 12

emi = loan_amount * (
    monthly_rate * (1 + monthly_rate)**tenure
) / (
    (1 + monthly_rate)**tenure - 1
)

# ---------------------------------------------------------
# Display Output
# ---------------------------------------------------------
st.title("Vehicle Finance Calculator")

st.write("### Selected Vehicle Details")
st.write(f"**Description:** {selected_description}")
st.write(f"**Variant (SAP):** {selected_variant}")
st.write(f"**Option Code:** {selected_option}")

st.write("### Price Breakdown")
st.write(f"**Vehicle Price:** {vehicle_price:,.2f}")

st.write("### Finance Calculation")
st.write(f"**Down Payment ({down_payment_pct*100:.0f}%):** {down_payment:,.2f}")
st.write(f"**Loan Amount:** {loan_amount:,.2f}")
st.write(f"**Monthly EMI:** {emi:,.2f}")

st.success("Calculation Completed Successfully")
