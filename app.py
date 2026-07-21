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

price_df = df_2026 if model_year == "MY 2026" else df_2025

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
    accessory_price_single = df_accessories[
        df_accessories["List Of Accessories"].isin(selected_accessories)
    ]["Price"].sum()
else:
    accessory_price_single = 0.0

accessories_total = (accessory_price_single + manual_accessories) * no_of_units

# ---------------------------------------------------------
# RMC Selection (with N/A handling)
# ---------------------------------------------------------
st.sidebar.title("RMC Selection")

rmc_options = list(df_rmc.columns[1:])
selected_rmc = st.sidebar.selectbox("Select RMC Package", ["None"] + rmc_options)

if selected_rmc != "None":
    if "Vehicle Model" in df_rmc.columns:
        match_rows = df_rmc[df_rmc["Vehicle Model"] == selected_description]
        raw_value = match_rows[selected_rmc].iloc[0] if not match_rows.empty else df_rmc[selected_rmc].iloc[0]
    else:
        raw_value = df_rmc[selected_rmc].iloc[0]

    try:
        rmc_price_single = float(raw_value)
    except:
        rmc_price_single = 0.0
else:
    rmc_price_single = 0.0

rmc_total = rmc_price_single * no_of_units

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
# VAT Calculations
# ---------------------------------------------------------
vat_rate = 0.05

vat_total = (mmc_total + accessories_total + rmc_total) * vat_rate

# ---------------------------------------------------------
# Fees (incl. VAT)
# ---------------------------------------------------------
documentation_fee_total = 200 * 1.05 * no_of_units
mortgage_fee_total = 100 * 1.05 * no_of_units
mortgage_release_fee_total = 100 * 1.05 * no_of_units

# ---------------------------------------------------------
# Down Payment base and portion
# ---------------------------------------------------------
dp_base = mmc_total + accessories_total + rmc_total
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
# VAT on Interest (correct)
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
    rmc_total +
    vat_total +
    vat_on_interest +
    documentation_fee_total +
    mortgage_fee_total +
    mortgage_release_fee_total +
    total_interest
)

# ---------------------------------------------------------
# Mitsubishi Red Theme Styling
# ---------------------------------------------------------
st.title("Vehicle Finance Summary")

st.markdown("""
<style>
.grid-box {
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.grid-red {
    background-color: #ffe5e5;
    border: 2px solid #ff4d4d;
}
.grid-white {
    background-color: #ffffff;
    border: 2px solid #ff4d4d;
}
.grid-header {
    color: #cc0000;
    font-weight: 700;
    font-size: 22px;
    margin-bottom: 10px;
}
.req-header {
    color: #cc0000;
    font-weight: 700;
    font-size: 24px;
    margin-top: 30px;
}
.req-box {
    background-color: #fff5f5;
    border-left: 5px solid #cc0000;
    padding: 18px;
    border-radius: 8px;
    margin-top: 10px;
}
.req-item {
    font-size: 16px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

grid1, grid2 = st.columns(2)

# ---------------------------------------------------------
# GRID 1 — VEHICLE & COST BREAKDOWN
# ---------------------------------------------------------
with grid1:
    st.markdown('<div class="grid-box grid-red">', unsafe_allow_html=True)
    st.markdown('<div class="grid-header">Vehicle & Cost Breakdown</div>', unsafe_allow_html=True)

    st.markdown(f"""
    **Model Year:** {model_year}  
    **Description:** {selected_description}  
    **Variant (SAP):** {selected_variant}  
    **Option Code:** {selected_option}  

    ### MMC / Units
    **Units:** {no_of_units}  
    **MMC Total:** AED {mmc_total:,.2f}

    ### Accessories
    **Accessory Description:** {accessory_description if accessory_description else "—"}  
    **Selected Accessories:** {', '.join(selected_accessories) if selected_accessories else "None"}  
    **Accessories Total:** AED {accessories_total:,.2f}

    ### RMC
    **RMC Package:** {selected_rmc}  
    **RMC Total:** AED {rmc_total:,.2f}

    ### VAT & Fees
    **VAT:** AED {vat_total:,.2f}  
    **VAT on Interest:** AED {vat_on_interest:,.2f}  
    **Documentation Fee:** AED {documentation_fee_total:,.2f}  
    **Mortgage Fee:** AED {mortgage_fee_total:,.2f}  
    **Mortgage Release Fee:** AED {mortgage_release_fee_total:,.2f}

    ### Total Price
    **Grand Total:** AED {total_price:,.2f}
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# GRID 2 — FINANCE SUMMARY
# ---------------------------------------------------------
with grid2:
    st.markdown('<div class="grid-box grid-white">', unsafe_allow_html=True)
    st.markdown('<div class="grid-header">Finance Summary</div>', unsafe_allow_html=True)

    st.markdown(f"""
    ### Down Payment
    **DP Base:** AED {dp_base:,.2f}  
    **Down Payment ({dp_percent*100:.0f}%):** AED {dp_portion:,.2f}  
    **Total Down Payment:** AED {down_payment:,.2f}

    ### Loan Details
    **Principal Financed:** AED {principal_financed:,.2f}  
    **Total Interest:** AED {total_interest:,.2f}  
    **Loan Amount:** AED {loan_amount:,.2f}

    ### EMI Plan
    **Tenor:** {tenor} months  
    **Interest Rate:** {interest_rate*100:.2f}%  
    **Monthly EMI:** AED {emi:,.2f}
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# REQUIREMENTS SECTION
# ---------------------------------------------------------
st.markdown('<div class="req-header">Required Documents</div>', unsafe_allow_html=True)

st.markdown("""
<div class="req-box">
    <div class="req-item">• Valid Trade License Copy – All three pages for LLC</div>
    <div class="req-item">• Valid Passport Copies of all partners including the sponsor</div>
    <div class="req-item">• Valid UAE Residence Visa Copies for all expatriate partners</div>
    <div class="req-item">• Address page mandatory for Indian passport holders</div>
    <div class="req-item">• Valid Emirates ID (front & back) for the signatory</div>
    <div class="req-item">• Memorandum of Association & all amendment copies</div>
    <div class="req-item">• Last six months bank statements</div>
    <div class="req-item">• VAT Certificate Copy</div>
    <div class="req-item">• Tenancy Contract Copy</div>
    <div class="req-item">• VAT Return Statements & Receipts (last two quarters)</div>
    <div class="req-item">• 10 recent invoice copies (sales & purchase)</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PDF EXPORT (HTML Download)
# ---------------------------------------------------------
html_report = f"""
<h2>Vehicle Finance Summary</h2>

<h3>Vehicle & Cost Breakdown</h3>
Model Year: {model_year}<br>
Description: {selected_description}<br>
Variant (SAP): {selected_variant}<br>
Option Code: {selected_option}<br><br>

<b>MMC Total:</b> AED {mmc_total:,.2f}<br>
<b>Accessories Total:</b> AED {accessories_total:,.2f}<br>
<b>RMC Total:</b> AED {rmc_total:,.2f}<br>
<b>VAT:</b> AED {vat_total:,.2f}<br>
<b>VAT on Interest:</b> AED {vat_on_interest:,.2f}<br>
<b>Total Price:</b> AED {total_price:,.2f}<br><br>

<h3>Finance Summary</h3>
<b>DP Base:</b> AED {dp_base:,.2f}<br>
<b>Down Payment:</b> AED {down_payment:,.2f}<br>
<b>Principal Financed:</b> AED {principal_financed:,.2f}<br>
<b>Total Interest:</b> AED {total_interest:,.2f}<br>
<b>Loan Amount:</b> AED {loan_amount:,.2f}<br>
<b>Monthly EMI:</b> AED {emi:,.2f}<br><br>

<h3>Required Documents</h3>
<ul>
<li>Valid Trade License Copy – All three pages for LLC</li>
<li>Valid Passport Copies of all partners including the sponsor</li>
<li>Valid UAE Residence Visa Copies for all expatriate partners</li>
<li>Address page mandatory for Indian passport holders</li>
<li>Valid Emirates ID (front & back) for the signatory</li>
<li>Memorandum of Association & all amendment copies</li>
<li>Last six months bank statements</li>
<li>VAT Certificate Copy</li>
<li>Tenancy Contract Copy</li>
<li>VAT Return Statements & Receipts (last two quarters)</li>
<li>10 recent invoice copies (sales & purchase)</li>
</ul>
"""

st.download_button(
    label="📄 Download HTML for PDF/Print",
    data=html_report,
    file_name="vehicle_finance_summary.html",
    mime="text/html"
)

st.success("Report generated with Mitsubishi theme, requirements, and export option.")
