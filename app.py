import streamlit as st
import pandas as pd

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
# Finance Values (from your finance file)
# ---------------------------------------------------------
down_payment = float(finance_df.loc[0, "Down Payment"])
loan_amount = float(finance_df.loc[0, "Loan Amount"])

# ---------------------------------------------------------
# Tenor Selection + Interest Rate Logic
# ---------------------------------------------------------
st.sidebar.title("Finance Options")

tenor = st.sidebar.slider("Select Tenor (Months)", 1, 24, 12)

# Interest rate rules
if tenor <= 3:
    interest_rate = 0.0
elif tenor <= 12:
    interest_rate = 0.05
else:
    interest_rate = 0.06

monthly_rate = interest_rate / 12

# EMI Calculation
if interest_rate == 0:
    emi = loan_amount / tenor
else:
    emi = loan_amount * (
        monthly_rate * (1 + monthly_rate)**tenor
    ) / (
        (1 + monthly_rate)**tenor - 1
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

st.write("### Finance Details")
st.write(f"**Down Payment:** {down_payment:,.2f}")
st.write(f"**Loan Amount:** {loan_amount:,.2f}")
st.write(f"**Tenor:** {tenor} months")
st.write(f"**Interest Rate:** {interest_rate*100:.2f}%")

st.write("### Monthly EMI")
st.write(f"**EMI:** {emi:,.2f}")

st.success("Calculation Completed Successfully")
