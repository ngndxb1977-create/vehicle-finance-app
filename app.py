import pandas as pd
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Price List & Accessories", page_icon="🚗", layout="wide"
)

st.title("🚗 Vehicle Pricing & Financing Calculator")


# Helper function to find column names regardless of case or spaces
def get_column_name(df, possible_names):
    for name in possible_names:
        for col in df.columns:
            if str(col).strip().lower() == name.strip().lower():
                return col
    return None


# Helper to find the actual table header row in messy Excel files
def read_excel_auto_header(file_path, sheet_name=0):
    # Preview first 20 rows
    preview = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
    
    header_idx = 0
    keywords = ["MY", "MODEL", "VARIANT", "MODEL YEAR", "PRICE"]
    
    for idx, row in preview.iterrows():
        row_str = [str(val).strip().upper() for val in row.values if pd.notna(val)]
        if any(kw in row_str for kw in keywords):
            header_idx = idx
            break
            
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)
    # Strip whitespace from column headers
    df.columns = [str(col).strip() for col in df.columns]
    return df


# 1. Load Data from Excel File Dynamically
@st.cache_data
def load_data():
    try:
        file_path = "Price_LIST_RMC_ACCESSORIES.xlsx"
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        # Vehicles sheet
        v_sheet = "Vehicles" if "Vehicles" in sheet_names else 0
        df_vehicles = read_excel_auto_header(file_path, sheet_name=v_sheet)

        # RMC sheet
        rmc_sheet = next((s for s in sheet_names if s.strip().lower() == "rmc"), None)
        df_rmc = read_excel_auto_header(file_path, sheet_name=rmc_sheet) if rmc_sheet else pd.DataFrame()

        # Accessories sheet
        acc_sheet = next((s for s in sheet_names if s.strip().lower() in ["accessories", "accessory"]), None)
        df_acc = read_excel_auto_header(file_path, sheet_name=acc_sheet) if acc_sheet else pd.DataFrame()

        return df_vehicles, df_rmc, df_acc

    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


# Load data
df_vehicles, df_rmc, df_acc = load_data()

if not df_vehicles.empty:
    # Safely locate column names
    col_my = get_column_name(df_vehicles, ["MY", "Model Year", "Year", "MODEL YEAR"])
    col_model = get_column_name(df_vehicles, ["Model", "Model Name", "Vehicle Model", "MODEL"])
    col_variant = get_column_name(df_vehicles, ["VariantCode", "Variant Code", "Variant", "VARIANT CODE", "Code"])
    col_price = get_column_name(df_vehicles, ["Price", "Base Price", "Unit Price", "PRICE"])

    # If key columns are missing, show useful error UI instead of crashing
    if not col_my or not col_model or not col_variant:
        st.error("⚠️ Mandatory columns could not be auto-detected.")
        st.write("**Detected Columns in File:**", list(df_vehicles.columns))
        st.write("**Sample Data preview:**")
        st.dataframe(df_vehicles.head(5))
        st.stop()

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("📋 Vehicle Selection")

    # Dynamic Dropdowns from Excel Data using detected column names
    available_my = sorted(df_vehicles[col_my].dropna().unique())
    selected_my = st.sidebar.selectbox("Model Year (MY)", available_my)

    # Filter Models based on Selected MY
    filtered_models = df_vehicles[df_vehicles[col_my] == selected_my][col_model].dropna().unique()
    selected_model = st.sidebar.selectbox("Vehicle Model", filtered_models)

    # Filter Variant Codes based on Model & MY
    filtered_variants = (
        df_vehicles[
            (df_vehicles[col_my] == selected_my) & (df_vehicles[col_model] == selected_model)
        ][col_variant]
        .dropna()
        .unique()
    )
    selected_variant = st.sidebar.selectbox("Variant Code", filtered_variants)

    # Number of Units
    quantity = st.sidebar.number_input("Number of Units", min_value=1, value=1, step=1)

    # Retrieve base price for selected vehicle
    matching_rows = df_vehicles[
        (df_vehicles[col_my] == selected_my)
        & (df_vehicles[col_model] == selected_model)
        & (df_vehicles[col_variant] == selected_variant)
    ]

    if not matching_rows.empty and col_price:
        try:
            unit_base_price = float(matching_rows.iloc[0][col_price])
        except (ValueError, TypeError):
            unit_base_price = 0.0
    else:
        unit_base_price = 0.0

    # Optional RMC & Accessories selection
    st.sidebar.subheader("➕ Add-Ons (Per Unit)")
    rmc_price = 0.0
    rmc_opt_col = get_column_name(df_rmc, ["RMC_Option", "RMC Option", "Option", "RMC"])
    rmc_price_col = get_column_name(df_rmc, ["Price", "Cost", "PRICE"])

    if not df_rmc.empty and rmc_opt_col and rmc_price_col:
        selected_rmc = st.sidebar.selectbox("RMC Contract", ["None"] + list(df_rmc[rmc_opt_col].unique()))
        if selected_rmc != "None":
            try:
                rmc_price = float(df_rmc[df_rmc[rmc_opt_col] == selected_rmc][rmc_price_col].values[0])
            except Exception:
                rmc_price = 0.0

    acc_price = 0.0
    acc_item_col = get_column_name(df_acc, ["Accessory", "Item", "Description", "ACCESSORY"])
    acc_price_col = get_column_name(df_acc, ["Price", "Cost", "PRICE"])

    if not df_acc.empty and acc_item_col and acc_price_col:
        selected_acc = st.sidebar.multiselect("Accessories", list(df_acc[acc_item_col].unique()))
        if selected_acc:
            try:
                acc_price = float(df_acc[df_acc[acc_item_col].isin(selected_acc)][acc_price_col].sum())
            except Exception:
                acc_price = 0.0

    total_unit_price = unit_base_price + rmc_price + acc_price
    total_vehicle_price = total_unit_price * quantity

    st.sidebar.subheader("🏦 Financing Terms")
    tenor_months = st.sidebar.selectbox("Tenor (Months)", options=[12, 24, 36, 48, 60], index=0)
    interest_rate_annual = st.sidebar.number_input("Annual Interest Rate (%)", value=5.00, step=0.25) / 100
    dp_percentage = st.sidebar.slider("Down Payment (%)", min_value=10, max_value=50, value=25) / 100

    # Fixed Charges
    mortgage_release = st.sidebar.number_input("Mortgage Releasing Charges", value=100.0)
    mortgage_fee = st.sidebar.number_input("Mortgage Charges", value=100.0)
    doc_fee = st.sidebar.number_input("Documentation Charges", value=200.0)
    vat_rate = 0.05

    # --- DYNAMIC CALCULATIONS ---
    base_down_payment = total_vehicle_price * dp_percentage
    loan_principal = total_vehicle_price - base_down_payment

    deferred_admin_charges = loan_principal * interest_rate_annual * (tenor_months / 12)

    subtotal_fees = deferred_admin_charges + mortgage_release + mortgage_fee + doc_fee
    grand_total_net = total_vehicle_price + subtotal_fees

    vat_vehicle = total_vehicle_price * vat_rate
    vat_fees = subtotal_fees * vat_rate
    grand_total_vat = vat_vehicle + vat_fees

    total_price_inc_vat = grand_total_net + grand_total_vat

    total_down_payment = (base_down_payment * (1 + vat_rate)) + (vat_fees)
    balance_due = total_price_inc_vat - total_down_payment
    pdc_monthly_installment = balance_due / tenor_months if tenor_months > 0 else 0

    # --- MAIN INTERFACE DISPLAY ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Vehicle Breakdown")
        st.write(f"**MY / Model:** {selected_my} | {selected_model}")
        st.write(f"**Variant Code:** {selected_variant}")
        st.write(f"**Quantity:** {quantity} Unit(s)")
        st.write(f"**Unit Net Price:** AED {total_unit_price:,.2f}")
        st.write(f"**Total Vehicle Price (Net):** AED {total_vehicle_price:,.2f}")

        st.markdown("---")
        st.subheader("⚙️ Charges & Dynamic Fees")
        st.write(f"**Dynamic Deferred Admin Charges ({interest_rate_annual*100:.2f}% / {tenor_months}M):** AED {deferred_admin_charges:,.2f}")
        st.write(f"**Mortgage Charges (Release + Registration):** AED {(mortgage_release + mortgage_fee):,.2f}")
        st.write(f"**Documentation Charges:** AED {doc_fee:,.2f}")
        st.write(f"**Total Net Charges:** AED {subtotal_fees:,.2f}")
        st.write(f"**Total VAT (5%):** AED {grand_total_vat:,.2f}")
        st.markdown(f"### **Grand Total Price (Inc. VAT): AED {total_price_inc_vat:,.2f}**")

    with col2:
        st.subheader("💳 Financing & Repayment Summary")
        st.write(f"**Down Payment Percentage:** {dp_percentage*100:.0f}%")
        st.write(f"**Total Down Payment (Inc. VAT):** AED {total_down_payment:,.2f}")
        st.write(f"**Net Balance Financed:** AED {balance_due:,.2f}")
        st.write(f"**Tenor Duration:** {tenor_months} Months")
        st.write(f"**Interest Rate Applied:** {interest_rate_annual*100:.2f}% Flat Equivalent")

        st.markdown("---")
        st.markdown(f"### **Monthly PDC Amount: AED {pdc_monthly_installment:,.2f}**")

else:
    st.info("Please place `Price_LIST_RMC_ACCESSORIES.xlsx` in the project root directory.")
