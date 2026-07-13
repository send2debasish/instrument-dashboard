import streamlit as st
import gspread
import pandas as pd
import base64
import openpyxl
from google.oauth2.service_account import Credentials

# -----------------------------streamlit run app.py
# Page Config
# -----------------------------
st.set_page_config(
    page_title="C&I",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session State
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# Page Session
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------------
# Hide Streamlit Menu
# -----------------------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Background Image
# -----------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_base64("background.png")

# -----------------------------
# CSS
# -----------------------------
if not st.session_state.logged_in:

    st.markdown(f"""
    <style>

    .stApp {{
        background-image: url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .header-box{{
        width:850px;
        margin:-80px auto 20px auto;
        text-align:center;
    }}

    .header-title{{
        font-size:42px;
        font-weight:bold;
        color:white;
    }}

    .header-subtitle{{
        font-size:20px;
        font-weight:bold;
        color:#FFD700;
    }}

    .login-title {{
        text-align:center;
        font-size:34px;
        color:white;
        font-weight:bold;
    }}

    .stTextInput label {{
        color:white !important;
        font-size:16px !important;
        font-weight:bold !important;
    }}

    .stTextInput input {{
        height:45px !important;
        font-size:20px !important;
        
    }}

    .stButton>button {{
        width:100%;
        height:60px;
        font-size:22px;
    }}

    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    .stApp{
        background:white !important;
        background-image:none !important;
    }

    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# Load Data from Google Sheet
# -----------------------------
@st.cache_data(ttl=60)
def load_data():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")
    worksheet = workbook.worksheet("Sheet1")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df
# -----------------------------
# Load Control Valve Data (Sheet2)
# -----------------------------
@st.cache_data(ttl=60)
def load_valve_data():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")

    # Load Sheet2
    worksheet = workbook.worksheet("Sheet2")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df


# =====================================================
# LOGIN PAGE
# =====================================================
if not st.session_state.logged_in:

    st.markdown("""
    <div class="header-box">
        <div class="header-title">
            CENTRAL AUTOMATION DEPARTMENT
        </div>
        <div class="header-subtitle">
            JSW JFE STEEL
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1.3,1,1.3])

    with center:

        st.markdown(
            '<div class="login-title">USER LOGIN</div>',
            unsafe_allow_html=True
        )

        username = st.text_input(
            "USERNAME",
            placeholder="Enter Username"
        )

        password = st.text_input(
            "PASSWORD",
            type="password",
            placeholder="Enter Password"
        )

        if st.button("LOGIN"):

            if username == "admin" and password == "jsw123":
                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")

else:

    # ==========================
    # HOME PAGE
    # ==========================
    if st.session_state.page == "Home":

        st.markdown(
            """
            <h1 style='margin-top:-100px; margin-bottom:20px;'>
                🏠 INDEX PAGE
            </h1>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📋 INSTRUMENT LIST", use_container_width=True):
                st.session_state.page = "Instrument"
                st.rerun()

            if st.button("📊 INSTRUMENT SUMMERY", use_container_width=True):
                st.session_state.page = "Summary"
                st.rerun()

        with col2:
            if st.button("⚙ CONTROL VALVE LIST", use_container_width=True):
                st.session_state.page = "Valve"
                st.rerun()

            if st.button("📈 CONTROL VALVE SUMMERY", use_container_width=True):
                st.session_state.page = "ValveSummary"
                st.rerun()

    # ==========================
    # INSTRUMENT LIST PAGE
    # ==========================
    elif st.session_state.page == "Instrument":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                📋 INSTRUMENT LIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        df = load_data()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=700
        )

    # ==========================
    # INSTRUMENT SUMMARY PAGE
    # ==========================
    elif st.session_state.page == "Summary":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                📋 INSTRUMENT SUMMERY
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Read Excel
        df = load_data()

        # Ensure Installed Qty is numeric
        df["INSTALLED QTY"] = pd.to_numeric(
            df["INSTALLED QTY"],
            errors="coerce"
        ).fillna(0)

        # Summary
        summary = pd.pivot_table(
            df,
            index="AREA",
            columns="INSTRUMENT TYPE",
            values="INSTALLED QTY",
            aggfunc="sum",
            fill_value=0
        )


        st.dataframe(
            summary.reset_index(),
            use_container_width=True,
            hide_index=True,
            height=700
        )

# ==========================
# CONTROL VALVE LIST PAGE
# ==========================

    elif st.session_state.page == "Valve":

        st.markdown(
            """
            <h1 style='margin-top:-100px; margin-bottom:15px;'>
                ⚙ CONTROL VALVE LIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Load Sheet2
        valve_df = load_valve_data()

        st.dataframe(
            valve_df,
            use_container_width=True,
            hide_index=True,
            height=700
        )

#=========================================================================================================
