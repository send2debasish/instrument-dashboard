import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# CONFIGURATION
# ==========================

SHEET_ID = "12UjodtyOq1avZrCb974Z0-87z7TmKLru6TdmqTqJj10"

INSTRUMENT_SHEET = "Sheet1"
SUMMARY_SHEET = "Summary"

USERNAME = "admin"
PASSWORD = "jsw123"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

st.set_page_config(
    page_title="JSW JFE STEEL",
    page_icon="🏭",
    layout="wide"
)

# ==========================
# LOAD DATA
# ==========================

@st.cache_data(ttl=30)
def load_sheet(sheet_name):

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SHEET_ID)

    worksheet = spreadsheet.worksheet(sheet_name)

    data = worksheet.get_all_records()

    return pd.DataFrame(data)

# ==========================
# LOGIN SESSION
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ==========================
# LOGIN PAGE
# ==========================

if not st.session_state.logged_in:

    st.markdown("<h1 style='text-align:center;'>🏭 JSW JFE STEEL</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Instrument Dashboard Login</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        user = st.text_input("User Name")

        pwd = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            if user == USERNAME and pwd == PASSWORD:

                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("Invalid Username or Password")

# ==========================
# MAIN PAGE
# ==========================

else:

    st.sidebar.success("Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🏭 JSW JFE STEEL")
    st.subheader("Automation & Instrument Dashboard")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("📋 Instrument List", use_container_width=True):
            st.session_state.page = "Instrument"

    with col2:

        if st.button("📊 Summary Sheet", use_container_width=True):
            st.session_state.page = "Summary"

    st.markdown("---")

    # ======================
    # Instrument List Page
    # ======================

    if st.session_state.page == "Instrument":

        st.header("📋 Instrument List")

        df = load_sheet(INSTRUMENT_SHEET)

        st.success("Instrument Sheet Loaded Successfully")

        st.dataframe(df, use_container_width=True)


    # ======================
    # Summary Page
    # ======================

    elif st.session_state.page == "Summary":

        st.header("📊 Instrument Summary")

        df = load_sheet(INSTRUMENT_SHEET)

        instrument_col = "INSTRUMENT TYPE"
        area_col = "AREA"
        qty_col = "INSTALLED QTY"

        if (
                instrument_col not in df.columns
                or area_col not in df.columns
                or qty_col not in df.columns
        ):

            st.error("Required columns not found.")

        else:

            df[qty_col] = pd.to_numeric(
                df[qty_col],
                errors="coerce"
            ).fillna(0)

            summary = pd.pivot_table(
                df,
                index=area_col,
                columns=instrument_col,
                values=qty_col,
                aggfunc="sum",
                fill_value=0
            )

            summary["TOTAL"] = summary.sum(axis=1)

            summary = summary.reset_index()

            st.dataframe(summary, use_container_width=True)
