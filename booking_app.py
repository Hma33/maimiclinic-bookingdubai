import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (EXACT FIGMA STYLING) ---
st.markdown("""
    <style>
    /* 1. IMPORT FONT: Source Sans Pro */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600&display=swap');

    /* 2. APPLY FONT GLOBALLY */
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
    }

    /* 3. MAIN BACKGROUND (Navy Blue #0D223F) */
    .stApp {
        background-color: #0D223F;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max_width: 1100px;
    }
    header {visibility: hidden;}

    /* --- LEFT CARD (The Booking Form) --- */
    /* Target the first column */
    div[data-testid="column"]:nth-of-type(1) > div {
        background-color: #FFFFFF; /* White Card */
        padding: 40px;
        border-radius: 6px 0px 0px 6px;
        min-height: 850px;
    }

    /* --- RIGHT CARD (The Info Panel) --- */
    /* Target the second column */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #1E2227; /* Dark Neutral from your Figma */
        padding: 40px;
        border-radius: 0px 6px 6px 0px;
        min-height: 850px;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    /* --- INPUT FIELDS (Light Gray #F8F9FA) --- */
    /* Remove borders, set background to Light Gray */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #F8F9FA !important; 
        color: #0D223F !important; /* Navy Text */
        border: none !important;
        border-radius: 0px !important;
        padding: 12px;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Hover/Focus states for inputs */
    .stTextInput input:focus, .stDateInput input:focus {
        background-color: #F1F3F5 !important;
    }

    /* --- HEADINGS --- */
    h1, h2, h3, h4, h5, h6 {
        color: #0D223F !important; /* Primary Navy */
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #F8F9FA;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #888; /* Gray for inactive */
        font-size: 14px;
        font-weight: 400;
    }
    .stTabs [aria-selected="true"] {
        color: #0D223F !important; /* Navy for active */
        border-bottom: 3px solid #b91c1c !important; /* Red underline */
        font-weight: 600;
    }

    /* --- BUTTONS --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0D223F; /* Primary Navy */
        color: white;
        border: none;
        padding: 10px 24px;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        border-radius: 4px;
        transition: opacity 0.3s;
        width: 100%; /* Full width button */
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        opacity: 0.9;
        border: 1px solid white;
    }

    /* --- CHECKBOXES --- */
    div[data-testid="stCheckbox"] label span {
        color: #333;
        font-size: 13px;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* CUSTOM CLASSES FOR LABELS */
    .label-text {
        font-size: 13px;
        color: #000;
        margin-bottom: 4px;
        font-weight: 400;
    }
    .section-header {
        font-size: 14px;
        color: #0D223F;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
@st.cache_resource
def get_sheet_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Clinic_Booking_System")

try:
    SHEET = get_sheet_connection()
    ws_new = SHEET.worksheet("New_Users")
    ws_exist = SHEET.worksheet("Existing_DB")
    ws_final = SHEET.worksheet("Final_Bookings")
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# --- 4. LAYOUT ---
col_left, col_right = st.columns([1.6, 1], gap="small")

# === RIGHT COLUMN (Info Card - Dark) ===
with col_right:
    st.markdown("""
        <div style="margin-top: 60px;">
            <div style="
                width: 110px; height: 110px; 
                background-color: black; 
                border-radius: 50%; 
                margin: 0 auto 20px auto; 
                display: flex; align-items: center; justify-content: center;
                border: 2px solid #333;">
                <span style="font-size: 40px;">🦷</span>
            </div>
            
            <h3 style="color: white !important; font-weight: 600; margin-bottom: 50px; font-family: 'Source Sans Pro';">Maimi Dental Clinic</h3>
            
            <hr style="border-color: #F8F9FA; width: 80%; margin: 0 auto 30px auto; opacity: 0.2;">
            
            <div style="text-align: center; color: #F8F9FA; font-size: 12px; line-height: 1.8; opacity: 0.9;">
                <p>Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.</p>
                <br>
                <p>The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station<br>exit 2</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://maps.google.com" target="_blank" style="color: white; text-decoration: none; font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span>📍</span> Google Map
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === LEFT COLUMN (Form Card - White) ===
with col_left:
    st.markdown("<h3 style='margin-bottom: 10px; font-weight: 600;'>Dental Clinic Appointment and Treatment Form</h3>", unsafe_allow_html=True)
    
    # Custom Tabs
    tab_new, tab_return = st.tabs(["New Registration", "Return"])
    
    # --- TAB 1: NEW REGISTRATION ---
    with tab_new:
        with st.form("new_reg_form"):
            
            # 1. Name
            st.markdown('<div class="section-header">1. Full Name</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="label-text">First Name</div>', unsafe_allow_html=True)
                f_name = st.text_input("First Name", label_visibility="collapsed")
            with c2:
                st.markdown('<div class="label-text">Last Name</div>', unsafe_allow_html=True)
                l_name = st.text_input("Last Name", label_visibility="collapsed")

            # 2. Phone
            st.markdown('<div class="section-header">2. Phone Number(WhatsApp)</div>', unsafe_allow_html=True)
            st.markdown('<div class="label-text">Phone Number</div>', unsafe_allow_html=True)
            phone = st.text_input("Phone", label_visibility="collapsed")

            # 3. Date
            st.markdown('<div class="section-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="label-text">Preferred Date</div>', unsafe_allow_html=True)
                date = st.date_input("Date", label_visibility="collapsed")
            with c4:
                st.markdown('<div class="label-text">Preferred Time</div>', unsafe_allow_html=True)
                time = st.time_input("Time", label_visibility="collapsed")

            # 4. Treatments
            st.markdown('<div class="section-header">4. Select the Treatments</div>', unsafe_allow_html=True)
            treatments = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            selected_treatments = []
            for t in treatments:
                if st.checkbox(t):
                    selected_treatments.append(t)
            
            st.write("")
            submitted = st.form_submit_button("Book now")
            
            if submitted:
                if f_name and phone:
                    full_name = f"{f_name} {l_name}"
                    t_str = ", ".join(selected_treatments)
                    ws_new.append_row([full_name, phone, str(date), str(time), t_str, str(datetime.now())])
                    ws_final.append_row([full_name, phone, str(date), str(time), t_str, "New", "Confirmed"])
                    st.success("Registration Successful!")
                else:
                    st.error("Please fill in the required fields.")

    # --- TAB 2: RETURN ---
    with tab_return:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.v_name = ""

        if not st.session_state.verified:
            st.markdown('<div class="label-text">Enter your registered Phone Number</div>', unsafe_allow_html=True)
            v_phone = st.text_input("VPhone", label_visibility="collapsed")
            
            # Using a secondary button style for Verify
            if st.button("Verify me"):
                try:
                    cell = ws_exist.find(v_phone)
                    row_val = ws_exist.row_values(cell.row)
                    st.session_state.verified = True
                    st.session_state.v_name = row_val[0]
                    st.rerun()
                except:
                    st.error("Phone number not found.")
        else:
            st.info(f"Welcome Back, {st.session_state.v_name}!")
            with st.form("return_booking"):
                st.markdown('<div class="section-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div class="label-text">Preferred Date</div>', unsafe_allow_html=True)
                    r_date = st.date_input("RD", label_visibility="collapsed")
                with rc2:
                    st.markdown('<div class="label-text">Preferred Time</div>', unsafe_allow_html=True)
                    r_time = st.time_input("RT", label_visibility="collapsed")
                
                st.markdown('<div class="section-header">4. Select the Treatments</div>', unsafe_allow_html=True)
                r_sel = []
                for t in treatments:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_sel.append(t)
                
                r_sub = st.form_submit_button("Book now")
                
                if r_sub:
                    t_str = ", ".join(r_sel)
                    ws_final.append_row([
                        st.session_state.v_name, 
                        "Existing", 
                        str(r_date), str(r_time), 
                        t_str, "Return", "Confirmed"
                    ])
                    st.success("Booking Confirmed!")
