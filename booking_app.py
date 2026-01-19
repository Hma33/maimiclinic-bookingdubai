import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Miami Dental Clinic", layout="wide")

# --- 2. CUSTOM CSS ---
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    
    /* Right Column (Info Panel) Styling */
    [data-testid="column"]:nth-of-type(2) {
        background-color: #1E2A38;
        border-radius: 15px;
        padding: 30px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Text Color Overrides */
    [data-testid="column"]:nth-of-type(2) h2, 
    [data-testid="column"]:nth-of-type(2) p, 
    [data-testid="column"]:nth-of-type(2) a,
    [data-testid="column"]:nth-of-type(2) span {
        color: white !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #1E2A38;
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 3em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #2c3e50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTION: GENERATE TIME SLOTS ---
def get_valid_time_slots(selected_date):
    """
    Returns 30-min slots based on specific daily hours.
    """
    day_idx = selected_date.weekday() # 0=Mon ... 6=Sun
    
    # Define hours (24h format). 24 = Midnight
    if day_idx in [0, 3, 4, 5, 6]: # Mon, Thu, Fri, Sat, Sun (10 AM - 12 AM)
        start_h, end_h = 10, 24 
    elif day_idx == 1: # Tuesday (12 PM - 10 PM)
        start_h, end_h = 12, 22
    elif day_idx == 2: # Wednesday (2 PM - 12 AM)
        start_h, end_h = 14, 24
    else:
        start_h, end_h = 9, 17 # Fallback

    slots = []
    current_h = start_h
    current_m = 0
    
    while current_h < end_h:
        is_pm = current_h >= 12
        display_h = current_h if current_h <= 12 else current_h - 12
        if display_h == 0: display_h = 12
        
        period = "PM" if is_pm else "AM"
        if current_h == 24: # Handle Midnight edge case
            display_h, period = 12, "AM"
            
        time_label = f"{display_h:02d}:{current_m:02d} {period}"
        slots.append(time_label)
        
        current_m += 30
        if current_m == 60:
            current_m = 0
            current_h += 1
            
    return slots

# --- 4. GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_sheet_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    if "gcp_service_account" not in st.secrets:
        st.error("Missing 'gcp_service_account' in streamlit secrets.")
        st.stop()
        
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
    st.error(f"🚨 Database Connection Failed: {e}")
    st.stop()

# --- 5. APP LAYOUT ---
col1, col2 = st.columns([2, 1], gap="large")

# === LEFT COLUMN: FORMS ===
with col1:
    st.title("Dental Clinic Appointment and Treatment Form")
    
    # *** THIS LINE WAS LIKELY MISSING OR OUT OF ORDER ***
    tab1, tab2 = st.tabs(["New Registration", "Return Patient"])
    
    # --- FLOW 1: NEW REGISTRATION ---
    with tab1:
        with st.form("new_patient_form"):
            st.markdown("#### 1. Full Name")
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First Name", placeholder="e.g. John")
            with c2:
                last_name = st.text_input("Last Name", placeholder="e.g. Doe")
            
            st.markdown("#### 2. Phone Number (WhatsApp)")
            phone = st.text_input("Phone Number", placeholder="+971 ...")
            
            st.markdown("#### 3. Preferred Appointment")
            d_col, t_col = st.columns(2)
            
            with d_col:
                # 1. Select Date
                date = st.date_input("Preferred Date", min_value=datetime.date.today())
            
            with t_col:
                # 2. Generate and Select Time
                valid_slots = get_valid_time_slots(date)
                time_str = st.selectbox("Available Time Slots", valid_slots)

            st.markdown("#### 4. Select Treatments")
            treatments_list = [
                "Consultation", "Scaling & Polishing", "Fillings",
                "Root Canal (RCT)", "Teeth Whitening", "Extractions", 
                "X-ray", "Crown & Bridge", "Veneers", "Kids Treatment"
            ]
            
            tc1, tc2 = st.columns(2)
            selected_treatments = []
            for i, treat in enumerate(treatments_list):
                target_col = tc1 if i % 2 == 0 else tc2
                if target_col.checkbox(treat):
                    selected_treatments.append(treat)
            
            st.write("")
            submitted = st.form_submit_button("Book now")
            
            if submitted:
                if first_name and last_name and phone:
                    full_name = f"{first_name} {last_name}"
                    treatments_str = ", ".join(selected_treatments) if selected_treatments else "General Checkup"
                    
                    try:
                        ws_new.append_row([full_name, phone, str(date), time_str, treatments_str, str(datetime.datetime.now())])
                        ws_final.append_row([full_name, phone, str(date), time_str, treatments_str, "Dr. Assigned", "Confirmed"])
                        st.success(f"✅ Thank you {first_name}! Appointment booked for {date} at {time_str}.")
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
                else:
                    st.warning("⚠️ Please fill in Name and Phone Number.")

    # --- FLOW 2: RETURN PATIENT ---
    with tab2:
        st.markdown("#### Verify Identity")
        
        if 'verified' not in st.session_state:
            st.session_state['verified'] = False
            st.session_state['user_name'] = ""
            st.session_state['user_phone'] = ""

        if not st.session_state['verified']:
            phone_input = st.text_input("Enter your registered Phone Number", key="verify_phone")
            if st.button("Find My Record"):
                try:
                    cell = ws_exist.find(phone_input)
                    if cell:
                        user_data = ws_exist.row_values(cell.row)
                        st.session_state['verified'] = True
                        st.session_state['user_name'] = user_data[0] 
                        st.session_state['user_phone'] = phone_input
                        st.rerun()
                    else:
                        st.error("Number not found.")
                except Exception as e:
                    st.error("Number not found or API Error.")
        else:
            st.success(f"👋 Welcome back, **{st.session_state['user_name']}**")
            if st.button("Change User"):
                st.session_state['verified'] = False
                st.rerun()

            with st.form("return_booking_form"):
                st.markdown("#### New Appointment Details")
                rd_col, rt_col = st.columns(2)
                with rd_col:
                    r_date = st.date_input("Date", min_value=datetime.date.today(), key="ret_date")
                with rt_col:
                    # Apply logic here too
                    r_valid_slots = get_valid_time_slots(r_date)
                    r_time_str = st.selectbox("Time", r_valid_slots, key="ret_time")
                
                r_treat = st.selectbox("Treatment Required", ["Routine Checkup", "Cleaning", "Follow-up", "Pain/Emergency"])
                
                r_submitted = st.form_submit_button("Confirm Booking")
                
                if r_submitted:
                    try:
                        ws_final.append_row([
                            st.session_state['user_name'],
                            st.session_state['user_phone'],
                            str(r_date),
                            r_time_str,
                            r_treat,
                            "Dr. Auto-Assigned",
                            "Confirmed (Returning)"
                        ])
                        st.success(f"✅ Booking Confirmed for {r_date} at {r_time_str}!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# === RIGHT COLUMN: INFO PANEL ===
with col2:
    st.markdown("<div style='font-size: 80px; text-align:center;'>🦷</div>", unsafe_allow_html=True) 
    st.markdown("## Miami Dental Clinic")
    st.markdown("---")
    st.markdown("""
    **Muraqqabat road, REQA bldg. 1st floor,** **office no. 104. Dubai, UAE.**
    
    The same building of Rigga Restaurant.
    Al Rigga Metro is the nearest metro station
    exit 2
    """)
    st.write("")
    st.markdown("📍 **[Google Map](https://maps.google.com)**")
    st.write("")
    st.info("ℹ️ **Admin Note:** Data is saved to 'New_Users' & 'Final_Bookings' tabs.")
