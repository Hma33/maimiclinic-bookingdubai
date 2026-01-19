import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. EXACT UI STYLING (CSS) ---
st.markdown("""
    <style>
    /* IMPORT FONT (Source Sans Pro matches your design) */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');

    /* GLOBAL RESET */
    * { font-family: 'Source Sans Pro', sans-serif; }
    
    /* BACKGROUND COLOR - Dark Navy */
    .stApp {
        background-color: #0d223f;
    }

    /* HIDE DEFAULT STREAMLIT HEADER */
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max_width: 1200px;
    }

    /* --- LEFT CARD (The Form) --- */
    /* We target the first column's internal div */
    div[data-testid="column"]:nth-of-type(1) > div {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 5px 0px 0px 5px; /* Matches your image radius */
        min-height: 850px;
    }

    /* --- RIGHT CARD (The Info) --- */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #1e2227; /* Darker card color */
        padding: 40px;
        border-radius: 0px 5px 5px 0px;
        min-height: 850px;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    /* --- INPUT FIELDS (The Grey Boxes) --- */
    /* Remove borders, add grey background */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #E5E7EB !important; /* Light grey like your design */
        border: none !important;
        color: #000 !important;
        border-radius: 0px !important; /* Square edges as per design */
        padding: 10px;
    }
    
    /* HIDE LABELS for cleaner look (We use custom headers instead) */
    .stTextInput label, .stDateInput label, .stTimeInput label {
        display: none;
    }

    /* --- TABS STYLING --- */
    /* Tab Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid #ddd;
    }
    /* Individual Tab Text */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #000;
        font-size: 16px;
        font-weight: 400;
    }
    /* Active Tab (Red Underline) */
    .stTabs [aria-selected="true"] {
        color: #000 !important;
        border-bottom: 3px solid #b91c1c !important; /* The Red Line */
        font-weight: 600;
    }

    /* --- BUTTON STYLING (Dark Blue "Book Now") --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0d223f;
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 4px;
        transition: background 0.3s;
        width: 120px; 
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #1a3a6c;
    }
    
    /* --- CHECKBOX STYLING --- */
    /* Reduce spacing */
    div[data-testid="stCheckbox"] {
        margin-bottom: -15px; 
    }
    div[data-testid="stCheckbox"] label span {
        font-size: 12px; /* Smaller font for treatments */
    }

    /* Custom Headers like "1. Full Name" */
    .form-header {
        font-size: 14px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 5px;
        color: #000;
    }
    .sub-label {
        font-size: 12px;
        color: #333;
        margin-bottom: 5px;
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

# --- 4. LAYOUT STRUCTURE ---
# Two columns: Form (Left) and Info (Right)
col_left, col_right = st.columns([1.5, 1], gap="small")

# ================= RIGHT COLUMN (Info Card) =================
with col_right:
    # Using HTML for the static dark card
    st.markdown("""
        <div style="margin-top: 80px;">
            <div style="
                width: 120px; height: 120px; 
                background-color: black; 
                border-radius: 50%; 
                margin: 0 auto 20px auto; 
                display: flex; align-items: center; justify-content: center;
                border: 2px solid #333;">
                <span style="font-size: 40px;">🦷</span>
            </div>
            
            <h2 style="color: white; font-weight: 600; margin-bottom: 60px;">Maimi Dental Clinic</h2>
            
            <hr style="border-color: #4B5563; width: 80%; margin: 0 auto 30px auto; opacity: 0.5;">
            
            <div style="text-align: center; color: #E5E7EB; font-size: 13px; line-height: 1.8;">
                <p>Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.</p>
                <br>
                <p>The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station<br>exit 2</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://maps.google.com" target="_blank" style="color: white; text-decoration: none; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    <span>📍</span> Google Map
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ================= LEFT COLUMN (Booking Form) =================
with col_left:
    st.markdown("<h3 style='margin-bottom: 20px; color: #0d223f;'>Dental Clinic Appointment and Treatment Form</h3>", unsafe_allow_html=True)
    
    # Tabs
    tab_new, tab_return = st.tabs(["New Registration", "Return"])
    
    # --- TAB 1: NEW REGISTRATION ---
    with tab_new:
        with st.form("new_reg_form"):
            
            # 1. Full Name
            st.markdown('<div class="form-header">1. Full Name</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="sub-label">First Name</div>', unsafe_allow_html=True)
                f_name = st.text_input("First Name") # Label hidden by CSS
            with c2:
                st.markdown('<div class="sub-label">Last Name</div>', unsafe_allow_html=True)
                l_name = st.text_input("Last Name")

            # 2. Phone
            st.markdown('<div class="form-header">2. Phone Number(WhatsApp)</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-label">Phone Number</div>', unsafe_allow_html=True)
            phone = st.text_input("Phone")

            # 3. Date & Time
            st.markdown('<div class="form-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="sub-label">Preferred Date</div>', unsafe_allow_html=True)
                date = st.date_input("Date")
            with c4:
                st.markdown('<div class="sub-label">Preferred Time</div>', unsafe_allow_html=True)
                time = st.time_input("Time")

            # 4. Treatments
            st.markdown('<div class="form-header">4. Select the Treatments</div>', unsafe_allow_html=True)
            treatments_list = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            selected_treatments = []
            for t in treatments_list:
                if st.checkbox(t):
                    selected_treatments.append(t)
            
            st.write("") # Spacer
            
            # Submit Button
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

    # --- TAB 2: RETURN USER ---
    with tab_return:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.v_name = ""

        if not st.session_state.verified:
            st.markdown('<div class="sub-label">Enter your registered Phone Number</div>', unsafe_allow_html=True)
            v_phone = st.text_input("Verify Phone", key="v_phone_input")
            
            if st.button("Verify me"):
                try:
                    cell = ws_exist.find(v_phone)
                    row_values = ws_exist.row_values(cell.row)
                    st.session_state.verified = True
                    st.session_state.v_name = row_values[0] # Assuming Name is first col
                    st.rerun()
                except:
                    st.error("Phone number not found.")
        
        else:
            # Verified View
            st.success(f"Welcome Back, {st.session_state.v_name}!")
            
            with st.form("return_booking_form"):
                st.markdown('<div class="form-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div class="sub-label">Preferred Date</div>', unsafe_allow_html=True)
                    r_date = st.date_input("RDate")
                with rc2:
                    st.markdown('<div class="sub-label">Preferred Time</div>', unsafe_allow_html=True)
                    r_time = st.time_input("RTime")

                st.markdown('<div class="form-header">4. Select the Treatments</div>', unsafe_allow_html=True)
                r_selected = []
                for t in treatments_list:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_selected.append(t)

                st.write("")
                r_submit = st.form_submit_button("Book now")

                if r_submit:
                    t_str = ", ".join(r_selected)
                    ws_final.append_row([
                        st.session_state.v_name, 
                        "Existing", 
                        str(r_date), str(r_time), 
                        t_str, "Return", "Confirmed"
                    ])
                    st.success("Booking Confirmed!")
