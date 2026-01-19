import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ROBUST CSS STYLING ---
st.markdown("""
    <style>
    /* IMPORT FONT */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600&display=swap');

    /* GLOBAL TEXT & BACKGROUND */
    html, body, [class*="css"] {
        font-family: 'Source Sans Pro', sans-serif;
    }
    .stApp {
        background-color: #0D223F !important; /* Global Navy Blue */
    }

    /* HIDE HEADER/FOOTER */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max_width: 1200px;
    }

    /* --- LEFT COLUMN: THE WHITE FORM CARD --- */
    /* We target the 1st column and force it to be white */
    div[data-testid="column"]:nth-of-type(1) {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 8px 0px 0px 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* FIX: Force text inside the white card to be black */
    div[data-testid="column"]:nth-of-type(1) label,
    div[data-testid="column"]:nth-of-type(1) p,
    div[data-testid="column"]:nth-of-type(1) h1,
    div[data-testid="column"]:nth-of-type(1) h2,
    div[data-testid="column"]:nth-of-type(1) h3 {
        color: #0D223F !important;
    }

    /* --- RIGHT COLUMN: THE DARK INFO CARD --- */
    /* Target the 2nd column */
    div[data-testid="column"]:nth-of-type(2) {
        background-color: #1E2227; /* Dark Grey/Navy */
        padding: 40px;
        border-radius: 0px 8px 8px 0px;
        color: white !important;
    }

    /* --- INPUT FIELDS --- */
    /* Light Grey Background, Square corners */
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #E5E7EB !important; /* Light Grey */
        color: #000000 !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 10px;
    }
    /* Fix for date picker icon color */
    div[data-baseweb="calendar"] {
        background-color: white;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 0px;
        color: #6B7280; /* Grey inactive */
        font-weight: 400;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #0D223F !important; /* Navy active */
        border-bottom: 3px solid #b91c1c !important; /* Red underline */
        font-weight: 600;
    }

    /* --- BUTTONS --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0D223F;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
        margin-top: 10px;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #1a3a6c;
    }
    
    /* --- CUSTOM HEADERS --- */
    .section-num {
        font-weight: 600;
        color: #0D223F;
        font-size: 15px;
        margin-top: 20px;
        margin-bottom: 5px;
    }
    .input-label {
        font-size: 13px;
        color: #374151; /* Dark grey text */
        margin-bottom: 2px;
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
col_left, col_right = st.columns([1.5, 1], gap="small")

# === RIGHT COLUMN (Info Card) ===
with col_right:
    # Use HTML markdown safely
    st.markdown("""
        <div style="text-align: center; margin-top: 60px;">
            <div style="
                width: 120px; height: 120px; 
                background-color: black; 
                border-radius: 50%; 
                margin: 0 auto 20px auto; 
                display: flex; align-items: center; justify-content: center;
                border: 2px solid #333;">
                <span style="font-size: 50px;">🦷</span>
            </div>
            
            <h2 style="color: white; font-family: 'Source Sans Pro'; font-weight: 600; margin-bottom: 40px;">Maimi Dental Clinic</h2>
            
            <hr style="border-color: #6B7280; width: 80%; margin: 0 auto 30px auto; opacity: 0.5;">
            
            <div style="color: #D1D5DB; font-size: 13px; line-height: 1.6;">
                <p>Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.</p>
                <br>
                <p>The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station<br>exit 2</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://maps.google.com" target="_blank" style="color: white; text-decoration: none; font-weight: 600; font-size: 13px;">
                    📍 Google Map
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === LEFT COLUMN (Form) ===
with col_left:
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    
    # TABS
    tab_new, tab_return = st.tabs(["New Registration", "Return"])
    
    # --- NEW REGISTRATION ---
    with tab_new:
        with st.form("new_reg"):
            st.markdown('<div class="section-num">1. Full Name</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="input-label">First Name</div>', unsafe_allow_html=True)
                f_name = st.text_input("fname", label_visibility="collapsed")
            with c2:
                st.markdown('<div class="input-label">Last Name</div>', unsafe_allow_html=True)
                l_name = st.text_input("lname", label_visibility="collapsed")
            
            st.markdown('<div class="section-num">2. Phone Number(WhatsApp)</div>', unsafe_allow_html=True)
            st.markdown('<div class="input-label">Phone Number</div>', unsafe_allow_html=True)
            phone = st.text_input("phone", label_visibility="collapsed")
            
            st.markdown('<div class="section-num">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                date = st.date_input("date", label_visibility="collapsed")
            with c4:
                st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                time = st.time_input("time", label_visibility="collapsed")
                
            st.markdown('<div class="section-num">4. Select the Treatments</div>', unsafe_allow_html=True)
            treatments = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            sel = []
            for t in treatments:
                if st.checkbox(t):
                    sel.append(t)
            
            st.write("")
            submit = st.form_submit_button("Book now")
            
            if submit:
                if f_name and phone:
                    full = f"{f_name} {l_name}"
                    t_str = ", ".join(sel)
                    ws_new.append_row([full, phone, str(date), str(time), t_str, str(datetime.now())])
                    ws_final.append_row([full, phone, str(date), str(time), t_str, "New", "Confirmed"])
                    st.success("Registration Successful!")
                else:
                    st.error("Please fill in the required fields.")

    # --- RETURN USER ---
    with tab_return:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.v_name = ""

        if not st.session_state.verified:
            st.markdown('<div class="input-label">Enter your registered Phone Number</div>', unsafe_allow_html=True)
            v_phone = st.text_input("vphone", label_visibility="collapsed")
            
            # Using a normal button for verify (outside form)
            if st.button("Verify me"):
                try:
                    cell = ws_exist.find(v_phone)
                    row = ws_exist.row_values(cell.row)
                    st.session_state.verified = True
                    st.session_state.v_name = row[0]
                    st.rerun()
                except:
                    st.error("Phone number not found.")
        else:
            st.info(f"Welcome Back, {st.session_state.v_name}!")
            with st.form("return_book"):
                st.markdown('<div class="section-num">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                    r_date = st.date_input("rdate", label_visibility="collapsed")
                with rc2:
                    st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                    r_time = st.time_input("rtime", label_visibility="collapsed")
                
                st.markdown('<div class="section-num">4. Select the Treatments</div>', unsafe_allow_html=True)
                r_sel = []
                for t in treatments:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_sel.append(t)
                
                r_sub = st.form_submit_button("Book now")
                
                if r_sub:
                    t_str = ", ".join(r_sel)
                    ws_final.append_row([st.session_state.v_name, "Existing", str(r_date), str(r_time), t_str, "Return", "Confirmed"])
                    st.success("Booking Confirmed!")
