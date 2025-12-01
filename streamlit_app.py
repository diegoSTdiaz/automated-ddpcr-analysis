import streamlit as st
from utils.plate import create_plate_df, render_interactive_plate
from utils.parser import parse_qxmanager_csv
from utils.calculator import calculate_copies_per_sample
import pandas as pd

# Page config
st.set_page_config(page_title="Automated ddPCR Analysis", layout="wide")
st.title("🧬 Automated ddPCR Analysis Tool")
st.markdown("**Upload your 3 files → Customize DNA input per well → Get accurate copies/ng results**")

# Session state
if "well_mass" not in st.session_state:
    st.session_state.well_mass = {}

# Sidebar uploads
st.sidebar.header("📁 Upload Files")
plate_layout_file = st.sidebar.file_uploader("1. Plate Layout CSV (Well → Sample)", type="csv")
study_info_file   = st.sidebar.file_uploader("2. Study Info CSV (Sample → DNA ng)", type="csv")
qx_file           = st.sidebar.file_uploader("3. QxManager/QuantaSoft Export CSV", type="csv")
default_ng = st.sidebar.number_input("Global Default DNA Input (ng)", value=140.0, step=5.0)

# Load CSVs
@st.cache_data
def load_csv(file):
    return pd.read_csv(file) if file else None

plate_layout_df = load_csv(plate_layout_file)
study_info_df   = load_csv(study_info_file)
qx_data_raw     = load_csv(qx_file)

# Parse QxManager
if qx_data_raw is not None:
    with st.spinner("Parsing QuantaSoft data..."):
        st.session_state.qx_data = parse_qxmanager_csv(qx_data_raw)
    st.success("QuantaSoft data loaded")
else:
    st.session_state.qx_data = None

# Build plate
plate_df = create_plate_df(plate_layout_df, study_info_df, default_ng, st.session_state.well_mass)

# Interactive plate
st.subheader("🧪 Click any well to change DNA amount")
st.session_state.well_mass = render_interactive_plate(plate_df, st.session_state.well_mass)

# Run calculations
if st.button("Run Calculations", type="primary"):
    if st.session_state.qx_data is None:
        st.error("Please upload QuantaSoft file")
    else:
        results = calculate_copies_per_sample(st.session_state.qx_data, plate_df)
        st.success("Done!")
        st.dataframe(results, use_container_width=True)
        st.download_button("Download results", results.to_csv(index=False), "ddpcr_results.csv")
