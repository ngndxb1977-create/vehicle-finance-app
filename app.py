import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_price_data():
    df = pd.read_excel("Price_LIST_RMC_ACCESSORIES.xlsx")
    df.columns = df.columns.str.strip()  # Remove hidden spaces
    return df

@st.cache_data
def load_finance_data():
    df = pd.read_excel("Vehicle Finance Calculator.xlsx")
    df.columns = df.columns.str.strip()
    return df

price_df = load_price_data()
finance_df = load_finance_data()

# ---------------------------------------------------------
# Debug: Show columns so app never crashes silently
# ---------------------------------------------------------
st.write("### Columns Found in Price List File")
st.write(price_df.columns.tolist())

# Expected column names (update these if your Excel differs)
EXPECTED_MY = "MY"
EXPECTED_MODEL_NAME = "Model_Name"
EXPECTED_MODEL_CODE = "Model_Code"
EXPECTED_RMC = "RMC"
EXPECTED_ACCESSORY = "Accessories"

# ---------------------------------------------------------
# Validate Columns
# ---------------------------------------------------------
missing_columns = [
    col for col in [EXPECTED_MY, EXPECTED_MODEL_NAME, EXPECTED_MODEL_CODE, EXPECTED_RMC, EXPECTED_ACCESSORY]
    if col not in price_df.columns
]

if missing_columns:
    st.error(f"❌ Missing columns in Excel file: {missing_columns}")
    st.stop()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.title("Vehicle Selection")

selected_my = st.sidebar.selectbox(
    "Model Year (MY)",
    sorted(price_df[EXPECTED_MY].dropna().unique())
)

selected_model = st.sidebar.selectbox(
    "Model Name",
    sorted(price_df[EXPECTED_MODEL_NAME].dropna().unique())
)

selected_code = st.sidebar.selectbox(
    "Model Code",
    sorted(price_df[EXPECTED_MODEL_CODE].dropna().unique())
)

# Filter based on MY, Model Name, Model Code
filtered_df = price_df[
    (price_df[EXPECTED_MY] == selected_my) &
    (price_df[EXPECTED_MODEL_NAME] == selected_model) &
    (price_df[EXPECTED_MODEL_CODE] == selected_code)
]

if filtered_df.empty:
    st.error("❌ No matching vehicle found. Please adjust your selections.")
    st.stop()

selected_rmc = st.sidebar.selectbox(
    "RMC",
    sorted(filtered_df[EXPECTED_RMC].dropna().unique())
)

selected_accessory = st.sidebar.selectbox(
    "Accessories",
    sorted(filtered_df[EXPECTED_ACCESSORY].dropna().unique())
)

# ---------------------------------------------------------
# Finance Logic
# ---------------------------------------------------------
interest_rate = float(finance_df.loc[0, "Interest_Rate"])
tenure = int(finance_df.loc[0, "Tenure"])
down_payment_pct = float(finance_df.loc[0, "Down_Payment_Percentage"])

vehicle_price = float(selected_rmc) + float(selected_accessory)
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
