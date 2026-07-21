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

price_df = load_price_data()

# ---------------------------------------------------------
# Sidebar Vehicle Selection
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

vehicle_base_price = float(filtered_final["PRICE"].values[0])

# ---------------------------------------------------------
# Additional Cost Inputs
# ---------------------------------------------------------
st.sidebar.title("Additional Costs")

accessories = st.sidebar.number_input("Accessories (AED)", min_value=0.0, value=0.0)
rmc = st.sidebar.number_input("RMC (AED)", min_value=0.0, value=0.0)

# ---------------------------------------------------------
# Finance Options
# ---------------------------------------------------------
st.sidebar.title("Finance Options")

tenor = st.sidebar.slider("Select Tenor (Months)", 1, 24, 12)
dp_percent = st.sidebar.slider("Down Payment %", 0, 100, 25) / 100

# ---------------------------------------------------------
# Interest Rate Logic
# ---------------------------------------------------------
if tenor <= 3:
    interest_rate = 0.0
elif tenor <= 12:
    interest_rate = 0.05
else:
    interest_rate = 0.06

monthly_rate = interest_rate / 12

# ---------------------------------------------------------
# VAT Calculations
# ---------------------------------------------------------
vat_rate = 0.05

# VAT on base price + accessories + RMC
vat_total = (vehicle_base_price + accessories + rmc) * vat_rate

# VAT on interest (only if interest > 0)
if interest_rate == 0:
    vat_on_interest = 0
else:
    vat_on_interest = (vehicle_base_price * interest_rate) * vat_rate

# ---------------------------------------------------------
# Fees (incl. VAT)
# ---------------------------------------------------------
documentation_fee = 210
mortgage_fee = 105
mortgage_release_fee = 105

# ---------------------------------------------------------
# Total Cost for Down Payment
# ---------------------------------------------------------
total_cost = (
    vehicle_base_price +
    accessories +
    rmc +
    vat_total +
    vat_on_interest +
    documentation_fee +
    mortgage_fee +
    mortgage_release_fee
)

down_payment = total_cost * dp_percent
loan_amount = total_cost - down_payment

# ---------------------------------------------------------
# EMI Calculation
# ---------------------------------------------------------
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
st.write(f"**Base Price:** {vehicle_base_price:,.2f}")
st.write(f"**Accessories:** {accessories:,.2f}")
st.write(f"**RMC:** {rmc:,.2f}")
st.write(f"**VAT:** {vat_total:,.2f}")
st.write(f"**VAT on Interest:** {vat_on_interest:,.2f}")

st.write("### Fees (incl. VAT)")
st.write(f"**Documentation Fee:** {documentation_fee:,.2f}")
st.write(f"**Mortgage Fee:** {mortgage_fee:,.2f}")
st.write(f"**Mortgage Release Fee:** {mortgage_release_fee:,.2f}")

st.write("### Total Cost")
st.write(f"**Total Cost:** {total_cost:,.2f}")

st.write("### Down Payment")
st.write(f"**Down Payment ({dp_percent*100:.0f}%):** {down_payment:,.2f}")

st.write("### Loan Amount")
st.write(f"**Loan Amount:** {loan_amount:,.2f}")

st.write("### EMI Calculation")
st.write(f"**Tenor:** {tenor} months")
st.write(f"**Interest Rate:** {interest_rate*100:.2f}%")
st.write(f"**Monthly EMI:** {emi:,.2f}")

st.success("Finance Calculation Completed Successfully")
