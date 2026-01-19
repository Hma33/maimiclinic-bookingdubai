import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ROBUST CSS STYLING ---
st.markdown("""
    <style>
    /* IMPORT FONT */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');

    /* GLOBAL RESET */
    * { font-family: 'Source Sans Pro', sans-serif; }
    
    /* GLOBAL BACKGROUND (Navy Blue) */
    .stApp {
        background-color: #0D223F !important;
    }

    /* HIDE DEFAULT HEADER */
    header, footer {visibility: hidden;}
    .block-container { padding-top: 2rem; max_width: 1200px; }

    /* --- LEFT COLUMN: THE WHITE FORM --- */
    /* Target the first column specifically */
    div[data-testid="column"]:nth-of-type(1) > div {
        background-color: #FFFFFF !important;
        padding: 40px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* FORCE TEXT BLACK INSIDE WHITE CARD */
    div[data-testid="column"]:nth-of-type(1) h1,
    div[data-testid="column"]:nth-of-type(1) h2,
    div[data-testid="column"]:nth-of-type(1) h3,
    div[data-testid="column"]:nth-of-type(1) p,
    div[data-testid="column"]:nth-of-type(1) label,
    div[data-testid="column"]:nth-of-type(1) span,
    div[data-testid="column"]:nth-of-type(1) div {
        color: #0D223F !important;
    }

    /* --- RIGHT COLUMN: THE DARK INFO CARD --- */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #1E2227 !important;
        padding: 40px;
        border-radius: 8px;
        height: 100%;
        color: white !important;
    }

    /* --- INPUT FIELDS --- */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #F3F4F6 !important; /* Light Grey */
        color: #1F2937 !important; /* Dark Grey Text */
        border: 1px solid #E5E7EB !important;
        border-radius: 4px !important;
        padding: 10px;
    }
    
    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #F3F4F6;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        color: #9CA3AF;
        font-weight: 400;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #0D223F !important;
        border-bottom: 3px solid #b91c1c !important; /* Red Underline */
        font-weight: 600;
    }

    /* --- BUTTONS --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0D223F;
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
        transition: background 0.2s;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #1a3a6c;
        color: white !important;
    }

    /* --- CUSTOM HEADERS --- */
    .form-step {
        font-size: 15px;
        font-weight: 600;
        color: #0D223F;
        margin-top: 25px;
        margin-bottom: 8px;
    }
    .input-label {
        font-size: 13px;
        color: #4B5563;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
@st.cache_resource
def get_sheet_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Fix for private key newline issue
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
col_form, col_info = st.columns([1.6, 1], gap="large")

# === RIGHT COLUMN (Dark Info Card) ===
with col_info:
    # We use st.markdown with unsafe_allow_html=True to prevent the code from showing as text
    st.markdown("""
        <div style="text-align: center; margin-top: 50px;">
            <div style="
                width: 120px; height: 120px; 
                background-color: black; 
                border-radius: 50%; 
                margin: 0 auto 25px auto; 
                display: flex; align-items: center; justify-content: center;
                border: 2px solid #374151;">
                <span style="font-size: 50px;">🦷</span>
            </div>
            
            <h2 style="color: white; margin-bottom: 30px; font-weight: 600;">Maimi Dental Clinic</h2>
            
            <hr style="border-color: #4B5563; width: 80%; margin: 0 auto 30px auto; opacity: 0.5;">
            
            <div style="color: #D1D5DB; font-size: 14px; line-height: 1.6;">
                <p>Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.</p>
                <br>
                <p>The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station<br>exit 2</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://maps.google.com" target="_blank" style="color: white; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 8px;">
                    <span>📍</span> Google Map
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === LEFT COLUMN (White Form Card) ===
with col_form:
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    
    # Custom Tabs
    tab1, tab2 = st.tabs(["New Registration", "Return"])
    
    # --- TAB 1: NEW REGISTRATION ---
    with tab1:
        with st.form("new_reg_form"):
            # 1. Full Name
            st.markdown('<div class="form-step">1. Full Name</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="input-label">First Name</div>', unsafe_allow_html=True)
                fname = st.text_input("fname", label_visibility="collapsed")
            with c2:
                st.markdown('<div class="input-label">Last Name</div>', unsafe_allow_html=True)
                lname = st.text_input("lname", label_visibility="collapsed")
            
            # 2. Phone
            st.markdown('<div class="form-step">2. Phone Number (WhatsApp)</div>', unsafe_allow_html=True)
            st.markdown('<div class="input-label">Phone Number</div>', unsafe_allow_html=True)
            phone = st.text_input("phone", label_visibility="collapsed")
            
            # 3. Date & Time
            st.markdown('<div class="form-step">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                date = st.date_input("date", label_visibility="collapsed")
            with c4:
                st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                time = st.time_input("time", label_visibility="collapsed")
            
            # 4. Treatments
            st.markdown('<div class="form-step">4. Select the Treatments</div>', unsafe_allow_html=True)
            treatments = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            selected = []
            for t in treatments:
                if st.checkbox(t):
                    selected.append(t)
            
            st.write("")
            submit = st.form_submit_button("Book now")
            
            if submit:
                if fname and phone:
                    fullname = f"{fname} {lname}"
                    t_str = ", ".join(selected)
                    ws_new.append_row([fullname, phone, str(date), str(time), t_str, str(datetime.now())])
                    ws_final.append_row([fullname, phone, str(date), str(time), t_str, "New", "Confirmed"])
                    st.success("Registration Successful!")
                else:
                    st.error("Please fill in the required fields.")

    # --- TAB 2: RETURN USER ---
    with tab2:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        # Initialize session state for verification
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.v_name = ""

        # STATE A: NOT VERIFIED
        if not st.session_state.verified:
            st.markdown('<div class="input-label">Enter your registered Phone Number</div>', unsafe_allow_html=True)
            v_phone = st.text_input("v_phone", label_visibility="collapsed")
            
            # Use columns to make the button smaller
            b1, b2 = st.columns([1, 4])
            with b1:
                if st.button("Verify me"):
                    try:
                        cell = ws_exist.find(v_phone)
                        row = ws_exist.row_values(cell.row)
                        st.session_state.verified = True
                        st.session_state.v_name = row[0]
                        st.rerun()
                    except:
                        st.error("Number not found.")
        
        # STATE B: VERIFIED (SHOW BOOKING FORM)
        else:
            st.success(f"Welcome back, {st.session_state.v_name}!")
            
            with st.form("return_booking"):
                st.markdown('<div class="form-step">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                    r_date = st.date_input("r_date", label_visibility="collapsed")
                with rc2:
                    st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                    r_time = st.time_input("r_time", label_visibility="collapsed")
                
                st.markdown('<div class="form-step">4. Select the Treatments</div>', unsafe_allow_html=True)
                r_sel = []
                for t in treatments:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_sel.append(t)
                
                r_sub = st.form_submit_button("Book now")
                
                if r_sub:
                    t_str = ", ".join(r_sel)
                    ws_final.append_row([st.session_state.v_name, "Existing", str(r_date), str(r_time), t_str, "Return", "Confirmed"])
                    st.success("Booking Confirmed!")
