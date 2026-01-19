import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap');
    * { font-family: 'Source Sans Pro', sans-serif; }
    .stApp { background-color: #0D223F !important; }
    header, footer {visibility: hidden;}
    .block-container { padding-top: 2rem; max_width: 1200px; }
    
    /* Left Card (White) */
    div[data-testid="column"]:nth-of-type(1) > div {
        background-color: #FFFFFF !important;
        padding: 40px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        min-height: 800px;
    }
    div[data-testid="column"]:nth-of-type(1) * { color: #0D223F !important; }

    /* Right Card (Dark) */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #1E2227 !important;
        padding: 40px;
        border-radius: 8px;
        min-height: 800px;
        color: white !important;
        text-align: center;
    }

    /* Inputs */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 4px !important;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #F3F4F6; margin-bottom: 20px; }
    .stTabs [aria-selected="true"] {
        color: #0D223F !important;
        border-bottom: 3px solid #b91c1c !important;
        font-weight: 600;
    }
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0D223F;
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
        margin-top: 10px;
    }
    .form-header { font-size: 15px; font-weight: 600; color: #0D223F; margin-top: 25px; margin-bottom: 8px; }
    .input-label { font-size: 13px; color: #4B5563; margin-bottom: 4px; }
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
    
    # Connect to (or create) Existing_Users_Booking
    try:
        ws_exist_booking = SHEET.worksheet("Existing_Users_Booking")
    except:
        ws_exist_booking = SHEET.add_worksheet(title="Existing_Users_Booking", rows="1000", cols="20")
        
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# --- 4. LOGIC: TIME VALIDATION ---
def check_clinic_hours(selected_date, selected_time):
    day_name = selected_date.strftime("%A") 
    
    if day_name == "Tuesday":
        open_time = time(12, 0)
        close_time = time(22, 0)
        schedule_msg = "12:00 PM - 10:00 PM"
    elif day_name == "Wednesday":
        open_time = time(14, 0)
        close_time = time(23, 59)
        schedule_msg = "02:00 PM - 12:00 AM"
    else: # Mon, Thu, Fri, Sat, Sun
        open_time = time(10, 0)
        close_time = time(23, 59)
        schedule_msg = "10:00 AM - 12:00 AM"

    if open_time <= selected_time <= close_time:
        return True, ""
    else:
        return False, f"⚠️ Clinic is closed at this time on {day_name}s. Open hours: {schedule_msg}"

# --- HELPER: GET DATA BY HEADER ---
def get_data_by_headers(sheet, row_index, required_headers):
    """
    Fetches data from specific columns based on header names.
    Returns a dictionary: { "HeaderName": "Value", ... }
    """
    # 1. Get all headers from the first row
    all_headers = sheet.row_values(1)
    
    # 2. Get all values from the specific row
    row_values = sheet.row_values(row_index)
    
    # 3. Map headers to indices
    data_map = {}
    for req_h in required_headers:
        if req_h in all_headers:
            col_idx = all_headers.index(req_h)
            # Ensure index is within bounds of the row data
            if col_idx < len(row_values):
                data_map[req_h] = row_values[col_idx]
            else:
                data_map[req_h] = "" # Cell is empty
        else:
            data_map[req_h] = "N/A" # Header not found in sheet
            
    return data_map

# --- 5. UI LAYOUT ---
col_form, col_info = st.columns([1.6, 1], gap="large")

# === RIGHT COLUMN (Info Card) ===
with col_info:
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
            
            <div style="color: #D1D5DB; font-size: 14px; line-height: 1.6; margin-top: 20px;">
                <strong>Opening Hours:</strong><br>
                Mon, Thu-Sun: 10 AM - 12 AM<br>
                Tue: 12 PM - 10 PM<br>
                Wed: 02 PM - 12 AM
            </div>
        </div>
    """, unsafe_allow_html=True)

# === LEFT COLUMN (Form) ===
with col_form:
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    tab1, tab2 = st.tabs(["New Registration", "Return"])
    
    treatments = [
        "Consult with professionals", "Scaling & Polishing", "Fillings",
        "Root Canal Treatment (RCT)", "Teeth Whitening", 
        "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
        "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
    ]

    # --- TAB 1: NEW REGISTRATION ---
    with tab1:
        with st.form("new_reg_form"):
            st.markdown('<div class="form-header">1. Full Name</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="input-label">First Name</div>', unsafe_allow_html=True)
                fname = st.text_input("fname", label_visibility="collapsed")
            with c2:
                st.markdown('<div class="input-label">Last Name</div>', unsafe_allow_html=True)
                lname = st.text_input("lname", label_visibility="collapsed")
            
            st.markdown('<div class="form-header">2. Phone Number (WhatsApp)</div>', unsafe_allow_html=True)
            st.markdown('<div class="input-label">Phone Number</div>', unsafe_allow_html=True)
            phone = st.text_input("phone", label_visibility="collapsed")
            
            st.markdown('<div class="form-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                date = st.date_input("date", label_visibility="collapsed")
            with c4:
                st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                time_val = st.time_input("time", label_visibility="collapsed")
            
            st.markdown('<div class="form-header">4. Select the Treatments</div>', unsafe_allow_html=True)
            selected = []
            for t in treatments:
                if st.checkbox(t):
                    selected.append(t)
            
            submit = st.form_submit_button("Book now")
            
            if submit:
                if not (fname and phone):
                    st.error("Please fill in your name and phone number.")
                else:
                    is_open, error_msg = check_clinic_hours(date, time_val)
                    if not is_open:
                        st.error(error_msg)
                    else:
                        fullname = f"{fname} {lname}"
                        t_str = ", ".join(selected)
                        ws_new.append_row([fullname, phone, str(date), str(time_val), t_str, str(datetime.now())])
                        ws_final.append_row([fullname, phone, str(date), str(time_val), t_str, "New", "Confirmed"])
                        st.success("Registration Successful!")

    # --- TAB 2: RETURN USER (STRICT HEADER MATCHING) ---
    with tab2:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.patient_dict = {}

        # List of Exact Headers we need from Existing_DB
        REQUIRED_FIELDS = ["FILE", "#PATIENT NAME", "Contact number", "DATE OF BIRTH", "HEIGHT", "WEIGHT", "ALLERGY"]

        if not st.session_state.verified:
            st.markdown('<div class="input-label">Enter your registered Phone Number</div>', unsafe_allow_html=True)
            v_phone = st.text_input("v_phone", label_visibility="collapsed")
            
            c_btn1, c_btn2 = st.columns([1, 3])
            with c_btn1:
                if st.button("Verify me"):
                    try:
                        # 1. Find the cell with the phone number
                        cell = ws_exist.find(v_phone)
                        
                        # 2. Extract data safely using headers
                        data_map = get_data_by_headers(ws_exist, cell.row, REQUIRED_FIELDS)
                        
                        st.session_state.verified = True
                        st.session_state.patient_dict = data_map
                        st.rerun()
                    except gspread.exceptions.CellNotFound:
                        st.error("Phone number not found in database.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        else:
            p_data = st.session_state.patient_dict
            st.success(f"Welcome back, {p_data.get('#PATIENT NAME', 'Patient')}!")
            
            # Debug view (optional, you can remove this)
            # st.write(p_data) 
            
            with st.form("return_booking"):
                st.markdown('<div class="form-header">3. Preferred Appointment Date and Time</div>', unsafe_allow_html=True)
                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div class="input-label">Preferred Date</div>', unsafe_allow_html=True)
                    r_date = st.date_input("r_date", label_visibility="collapsed")
                with rc2:
                    st.markdown('<div class="input-label">Preferred Time</div>', unsafe_allow_html=True)
                    r_time = st.time_input("r_time", label_visibility="collapsed")
                
                # Dynamic Helper
                r_day = r_date.strftime("%A")
                if r_day == "Tuesday":
                    st.caption(f"ℹ️ Hours for {r_day}: 12:00 PM - 10:00 PM")
                elif r_day == "Wednesday":
                    st.caption(f"ℹ️ Hours for {r_day}: 02:00 PM - 12:00 AM")
                else:
                    st.caption(f"ℹ️ Hours for {r_day}: 10:00 AM - 12:00 AM")

                st.markdown('<div class="form-header">4. Select the Treatments</div>', unsafe_allow_html=True)
                r_sel = []
                for t in treatments:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_sel.append(t)
                
                r_sub = st.form_submit_button("Book now")
                
                if r_sub:
                    is_open_r, error_msg_r = check_clinic_hours(r_date, r_time)
                    
                    if not is_open_r:
                        st.error(error_msg_r)
                    else:
                        t_str = ", ".join(r_sel)
                        
                        # --- COPY DATA TO 'Existing_Users_Booking' ---
                        
                        # 1. Setup Headers for Destination if empty
                        booking_headers = REQUIRED_FIELDS + ["BOOKING DATE", "BOOKING TIME", "TREATMENTS"]
                        
                        if not ws_exist_booking.get_all_values():
                            ws_exist_booking.append_row(booking_headers)
                        
                        # 2. Prepare Data Row in exact order
                        row_to_append = [
                            p_data.get("FILE", ""),
                            p_data.get("#PATIENT NAME", ""),
                            p_data.get("Contact number", ""),
                            p_data.get("DATE OF BIRTH", ""),
                            p_data.get("HEIGHT", ""),
                            p_data.get("WEIGHT", ""),
                            p_data.get("ALLERGY", ""),
                            str(r_date),
                            str(r_time),
                            t_str
                        ]
                        
                        ws_exist_booking.append_row(row_to_append)
                        ws_final.append_row([p_data.get("#PATIENT NAME"), p_data.get("Contact number"), str(r_date), str(r_time), t_str, "Return", "Confirmed"])
                        
                        st.success("Booking Confirmed!")
                        
            if st.button("Reset Verification"):
                st.session_state.verified = False
                st.session_state.patient_dict = {}
                st.rerun()
