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

vehicle_price = float(filtered_final["PRICE"].values[0])

# ---------------------------------------------------------
# MMC (Renamed to No Of Units)
# ---------------------------------------------------------
st.sidebar.title("MMC Options")
no_of_units = st.sidebar.number_input("No Of Units", min_value=1, value=1)

mmc_total = vehicle_price * no_of_units

# ---------------------------------------------------------
# Additional Accessories (Renamed)
# ---------------------------------------------------------
st.sidebar.title("Additional Accessories")

# Free-text accessory description
accessory_description = st.sidebar.text_input("Accessory Description")

# Additional accessory dropdown (from file)
additional_accessory_list = sorted(price_df["ACCESSORIES"].dropna().unique())
selected_additional_accessory = st.sidebar.selectbox(
    "Select Additional Accessory",
    ["None"] + additional_accessory_list
)

# Get price of selected accessory
if selected_additional_accessory != "None":
    accessory_price = float(
        price_df[price_df["ACCESSORIES"] == selected_additional_accessory]["PRICE"].values[0]
    )
else:
    accessory_price = 0.0

# Manual additional accessories input
manual_accessories = st.sidebar.number_input("Manual Accessories (AED)", min_value=0.0, value=0.0)

# Total accessories
accessories_total = accessory_price + manual_accessories

# ---------------------------------------------------------
# RMC Dropdown (from file)
# ---------------------------------------------------------
st.sidebar.title("RMC Selection")

rmc_list = sorted(price_df["RMC"].dropna().unique())
selected_rmc = st.sidebar.selectbox("Select RMC", ["None"] + rmc_list)

if selected_rmc != "None":
    rmc_price = float(price_df[price_df["RMC"] == selected_rmc]["PRICE"].values[0])
else:
    rmc_price = 0.0

# ---------------------------------------------------------
# Finance Options
# ---------------------------------------------------------
st.sidebar.title("Finance Options")

tenor = st.sidebar.slider("Select Tenor (Months)", 1, 24, 12)
dp_percent = st.sidebar.slider("Down Payment %", 0, 100, 25) / 100

# ---------------------------------------------------------
# Interest Rate Logic (Flat Interest)
# ---------------------------------------------------------
if tenor <= 3:
    interest_rate = 0.00
elif tenor <= 12:
    interest_rate = 0.05
else:
    interest_rate = 0.06

# ---------------------------------------------------------
# VAT Calculations
# ---------------------------------------------------------
vat_rate = 0.05

# VAT on MMC + Accessories + RMC
vat_total = (mmc_total + accessories_total + rmc_price) * vat_rate

# VAT on interest (flat interest)
if interest_rate == 0:
    vat_on_interest = 0
else:
    vat_on_interest = (mmc_total * interest_rate) * vat_rate

# ---------------------------------------------------------
# Fees (incl. VAT) per unit
# ---------------------------------------------------------
documentation_fee_total = 200 * 1.05 * no_of_units
mortgage_fee_total = 100 * 1.05 * no_of_units
mortgage_release_fee_total = 100 * 1.05 * no_of_units

# ---------------------------------------------------------
# DOWN PAYMENT (Excel Logic)
# ---------------------------------------------------------
dp_base = mmc_total + accessories_total + rmc_price
dp_portion = dp_base * dp_percent

down_payment = (
    dp_portion +
    vat_total +
    vat_on_interest +
    documentation_fee_total +
    mortgage_fee_total +
    mortgage_release_fee_total
)

# ---------------------------------------------------------
# PRINCIPAL FINANCED (Excel Logic)
# ---------------------------------------------------------
principal_financed = dp_base - dp_portion

# ---------------------------------------------------------
# FLAT INTEREST (Excel Logic)
# ---------------------------------------------------------
total_interest = principal_financed * interest_rate

# ---------------------------------------------------------
# LOAN AMOUNT (Excel Logic)
# ---------------------------------------------------------
loan_amount = principal_financed + total_interest

# ---------------------------------------------------------
# EMI (Excel Logic)
# ---------------------------------------------------------
emi = loan_amount / tenor

# ---------------------------------------------------------
# TOTAL PRICE (Excel Logic)
# ---------------------------------------------------------
total_price = (
    mmc_total +
    accessories_total +
    rmc_price +
    vat_total +
    vat_on_interest +
    documentation_fee_total +
    mortgage_fee_total +
    mortgage_release_fee_total +
    total_interest
)

# ---------------------------------------------------------
# Display Output
# ---------------------------------------------------------
st.title("Vehicle Finance Calculator (Updated Version)")

st.write("### Vehicle Details")
st.write(f"**Description:** {selected_description}")
st.write(f"**Variant (SAP):** {selected_variant}")
st.write(f"**Option Code:** {selected_option}")

st.write("### MMC / Units")
st.write(f"**No Of Units:** {no_of_units}")
st.write(f"**MMC Total:** {mmc_total:,.2f}")

st.write("### Accessories")
st.write(f"**Accessory Description:** {accessory_description}")
st.write(f"**Selected Accessory:** {selected_additional_accessory}")
st.write(f"**Accessory Price:** {accessory_price:,.2f}")
st.write(f"**Manual Accessories:** {manual_accessories:,.2f}")
st.write(f"**Total Accessories:** {accessories_total:,.2f}")

st.write("### RMC")
st.write(f"**Selected RMC:** {selected_rmc}")
st.write(f"**RMC Price:** {rmc_price:,.2f}")

st.write("### VAT & Fees")
st.write(f"**VAT:** {vat_total:,.2f}")
st.write(f"**VAT on Interest:** {vat_on_interest:,.2f}")
st.write(f"**Documentation Fee:** {documentation_fee_total:,.2f}")
st.write(f"**Mortgage Fee:** {mortgage_fee_total:,.2f}")
st.write(f"**Mortgage Release Fee:** {mortgage_release_fee_total:,.2f}")

st.write("### Total Price")
st.write(f"**Total Price:** {total_price:,.2f}")

st.write("### Down Payment")
st.write(f"**DP Base:** {dp_base:,.2f}")
st.write(f"**DP Portion ({dp_percent*100:.0f}%):** {dp_portion:,.2f}")
st.write(f"**Total Down Payment:** {down_payment:,.2f}")

st.write("### Loan Details")
st.write(f"**Principal Financed:** {principal_financed:,.2f}")
st.write(f"**Total Interest:** {total_interest:,.2f}")
st.write(f"**Loan Amount:** {loan_amount:,.2f}")

st.write("### EMI")
st.write(f"**Monthly EMI:** {emi:,.2f}")

st.success("All new UI changes have been applied successfully.")
