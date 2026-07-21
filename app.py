import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Load Data (case-insensitive sheet detection)
# ---------------------------------------------------------
@st.cache_data
def load_price_data():
    xls = pd.ExcelFile("Price_LIST_RMC_ACCESSORIES.xlsx")

    sheet_names = [name.strip() for name in xls.sheet_names]
    sheet_names_lower = [name.lower() for name in sheet_names]

    sheet_2026 = sheet_names[sheet_names_lower.index("price_list_my_2026")]
    sheet_2025 = sheet_names[sheet_names_lower.index("price_list_my_2025")]
    sheet_rmc = sheet_names[sheet_names_lower.index("rmc")]
    sheet_accessories = sheet_names[sheet_names_lower.index("accessories")]

    df_2026 = pd.read_excel(xls, sheet_2026)
    df_2025 = pd.read_excel(xls, sheet_2025)
    df_rmc = pd.read_excel(xls, sheet_rmc)
    df_accessories = pd.read_excel(xls, sheet_accessories)

    for df in [df_2026, df_2025, df_rmc, df_accessories]:
        df.columns = df.columns.str.strip()

    return df_2026, df_2025, df_rmc, df_accessories


df_2026, df_2025, df_rmc, df_accessories = load_price_data()

# ---------------------------------------------------------
# Model Year selection
# ---------------------------------------------------------
st.sidebar.title("Model Year Selection")

model_year = st.sidebar.selectbox(
    "Select Model Year",
    ["MY 2026", "MY 2025"]
)

if model_year == "MY 2026":
    price_df = df_2026
else:
    price_df = df_2025

# ---------------------------------------------------------
# Vehicle Selection
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
# MMC Options (No Of Units)
# ---------------------------------------------------------
st.sidebar.title("MMC Options")
no_of_units = st.sidebar.number_input("No Of Units", min_value=1, value=1)

mmc_total = vehicle_price * no_of_units

# ---------------------------------------------------------
# Additional Accessories (with multi-select)
# ---------------------------------------------------------
st.sidebar.title("Additional Accessories")

accessory_description = st.sidebar.text_input("Accessory Description")

manual_accessories = st.sidebar.number_input(
    "Manual Accessories (AED)",
    min_value=0.0,
    value=0.0
)

accessory_list = df_accessories["List Of Accessories"].dropna().tolist()

selected_accessories = st.sidebar.multiselect(
    "Select Accessories",
    accessory_list
)

if selected_accessories:
    accessory_price = df_accessories[
        df_accessories["List Of Accessories"].isin(selected_accessories)
    ]["Price"].sum()
else:
    accessory_price = 0.0

accessories_total = accessory_price + manual_accessories

# ---------------------------------------------------------
# RMC Selection (with N/A handling)
# ---------------------------------------------------------
st.sidebar.title("RMC Selection")

rmc_options = list(df_rmc.columns[1:])  # skip "Vehicle Model"
selected_rmc = st.sidebar.selectbox("Select RMC Package", ["None"] + rmc_options)

if selected_rmc != "None":
    if "Vehicle Model" in df_rmc.columns:
        match_rows = df_rmc[df_rmc["Vehicle Model"] == selected_description]

        if not match_rows.empty:
            raw_value = match_rows[selected_rmc].iloc[0]
            try:
                rmc_price = float(raw_value)
            except:
                rmc_price = 0.0
        else:
            raw_value = df_rmc[selected_rmc].iloc[0]
            try:
                rmc_price = float(raw_value)
            except:
                rmc_price = 0.0
    else:
        raw_value = df_rmc[selected_rmc].iloc[0]
        try:
            rmc_price = float(raw_value)
        except:
            rmc_price = 0.0
else:
    rmc_price = 0.0

# ---------------------------------------------------------
# Finance Options (editable interest rate)
# ---------------------------------------------------------
st.sidebar.title("Finance Options")

tenor = st.sidebar.slider("Select Tenor (Months)", 1, 24, 12)

interest_rate = st.sidebar.number_input(
    "Interest Rate (Flat %)",
    min_value=0.0,
    max_value=10.0,
    value=5.0
) / 100

dp_percent = st.sidebar.slider("Down Payment %", 0, 100, 25) / 100

# ---------------------------------------------------------
# VAT Calculations (excluding VAT on interest for now)
# ---------------------------------------------------------
vat_rate = 0.05

vat_total = (mmc_total + accessories_total + rmc_price) * vat_rate

# ---------------------------------------------------------
# Fees (incl. VAT)
# ---------------------------------------------------------
documentation_fee_total = 200 * 1.05 * no_of_units
mortgage_fee_total = 100 * 1.05 * no_of_units
mortgage_release_fee_total = 100 * 1.05 * no_of_units

# ---------------------------------------------------------
# Down Payment base and portion
# ---------------------------------------------------------
dp_base = mmc_total + accessories_total + rmc_price
dp_portion = dp_base * dp_percent

# ---------------------------------------------------------
# Principal Financed
# ---------------------------------------------------------
principal_financed = dp_base - dp_portion

# ---------------------------------------------------------
# Flat Interest
# ---------------------------------------------------------
total_interest = principal_financed * interest_rate

# ---------------------------------------------------------
# VAT on Interest (correct: based on total interest)
# ---------------------------------------------------------
vat_on_interest = total_interest * vat_rate

# ---------------------------------------------------------
# Down Payment (final)
# ---------------------------------------------------------
down_payment = (
    dp_portion +
    vat_total +
    vat_on_interest +
    documentation_fee_total +
    mortgage_fee_total +
    mortgage_release_fee_total
)

# ---------------------------------------------------------
# Loan Amount
# ---------------------------------------------------------
loan_amount = principal_financed + total_interest

# ---------------------------------------------------------
# EMI
# ---------------------------------------------------------
emi = loan_amount / tenor

# ---------------------------------------------------------
# Total Price
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
st.title("Vehicle Finance Calculator")

st.write("### Vehicle Details")
st.write(f"**Model Year:** {model_year}")
st.write(f"**Description:** {selected_description}")
st.write(f"**Variant (SAP):** {selected_variant}")
st.write(f"**Option Code:** {selected_option}")

st.write("### MMC / Units")
st.write(f"**No Of Units:** {no_of_units}")
st.write(f"**MMC Total:** {mmc_total:,.2f}")

st.write("### Accessories")
st.write(f"**Accessory Description:** {accessory_description}")
st.write(f"**Selected Accessories:** {', '.join(selected_accessories) if selected_accessories else 'None'}")
st.write(f"**Accessories Price (from list):** {accessory_price:,.2f}")
st.write(f"**Manual Accessories:** {manual_accessories:,.2f}")
st.write(f"**Total Accessories:** {accessories_total:,.2f}")

st.write("### RMC")
st.write(f"**Selected RMC Package:** {selected_rmc}")
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
st.write(f"**Tenor:** {tenor} months")
st.write(f"**Interest Rate:** {interest_rate*100:.2f}%")
st.write(f"**Monthly EMI:** {emi:,.2f}")

st.success("App updated with correct VAT on interest, model year filter, multi-accessory selection, RMC handling, and editable interest rate.")
