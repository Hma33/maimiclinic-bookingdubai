import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Miami Dental Clinic", layout="wide")

# --- 2. INITIALIZE SESSION STATE ---
if 'verified' not in st.session_state:
    st.session_state['verified'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

# --- 3. CUSTOM CSS ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* LEFT COLUMN: Input Fields Styling */
    .stTextInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #e6e6e6 !important;
        border: none !important;
        border-radius: 0px !important;
        color: black !important;
    }
    
    /* RIGHT COLUMN: Dark Card Styling */
    [data-testid="column"]:nth-of-type(2) > div {
        background-color: #19202a; /* Dark Navy */
        border-radius: 15px;
        padding: 40px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Text colors in right column */
    [data-testid="column"]:nth-of-type(2) h2, 
    [data-testid="column"]:nth-of-type(2) p, 
    [data-testid="column"]:nth-of-type(2) span, 
    [data-testid="column"]:nth-of-type(2) div {
        color: white !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #19202a;
        color: white;
        width: 150px;
        border-radius: 5px;
        height: 3em;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Hide Streamlit footer/header if desired */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 4. HELPER: DYNAMIC TIME SLOTS ---
def get_valid_time_slots(selected_date):
    day_idx = selected_date.weekday() 
    if day_idx in [0, 3, 4, 5, 6]: # Mon, Thu, Fri, Sat, Sun
        start_h, end_h = 10, 24 
    elif day_idx == 1: # Tue
        start_h, end_h = 12, 22
    elif day_idx == 2: # Wed
        start_h, end_h = 14, 24
    else:
        start_h, end_h = 9, 17

    slots = []
    current_h = start_h
    current_m = 0
    while current_h < end_h:
        is_pm = current_h >= 12
        display_h = current_h if current_h <= 12 else current_h - 12
        if display_h == 0: display_h = 12 
        period = "PM" if is_pm else "AM"
        time_label = f"{display_h:02d}:{current_m:02d} {period}"
        slots.append(time_label)
        current_m += 30
        if current_m == 60:
            current_m = 0
            current_h += 1
    return slots

# --- 5. GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_sheet_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" not in st.secrets:
        st.error("Missing 'gcp_service_account' in secrets.")
        st.stop()
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Clinic_Booking_System")

try:
    SHEET = get_sheet_connection()
    
    # 1. New Registration Sheet (Consolidated)
    try:
        ws_new_booking = SHEET.worksheet("New_Users_Booking")
    except:
        ws_new_booking = SHEET.add_worksheet(title="New_Users_Booking", rows="1000", cols="20")
        ws_new_booking.append_row([
            "Full Name", "Phone Number", "Appointment Date", "Time", "Treatments", "Doctor Assignment", "Status"
        ])

    # 2. Existing DB (Read Only Source)
    ws_exist = SHEET.worksheet("Existing_DB")
    
    # 3. Return Patient Booking Sheet (Append Target)
    try:
        ws_return = SHEET.worksheet("Existing_Users_Booking")
    except:
        ws_return = SHEET.add_worksheet(title="Existing_Users_Booking", rows="1000", cols="20")
        # Headers with RE included
        ws_return.append_row([
            "FILE #", "Patient Name", "Contact Number", "Data of Birth", "Height", "Weight", "Allergy", "RE",
            "Appointment Date", "Time", "Treatment", "Doctor Status", "Booking Status"
        ])

except Exception as e:
    st.error(f"🚨 Database Connection Failed: {e}")
    st.stop()

# --- 6. APP LAYOUT ---
col1, col2 = st.columns([2, 1], gap="large")

# === LEFT COLUMN: FORMS ===
with col1:
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    st.write("")
    
    tab1, tab2 = st.tabs(["New Registration", "Return"])
    
    # --- TAB 1: NEW PATIENT ---
    with tab1:
        st.write("")
        st.markdown("**1. Full Name**")
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("First Name", placeholder="", label_visibility="visible", key="n_fname")
        with c2:
            last_name = st.text_input("Last Name", placeholder="", label_visibility="visible", key="n_lname")
        
        st.write("")
        st.markdown("**2. Phone Number(WhatsApp)**")
        phone = st.text_input("Phone Number", placeholder="", label_visibility="visible", key="n_phone")
        
        st.write("")
        st.markdown("**3. Preferred Appointment Date and Time**")
        st.markdown("Preferred Date")
        date = st.date_input("Preferred Date", min_value=datetime.date.today(), label_visibility="collapsed", key="n_date")
        
        st.markdown("Preferred Time")
        valid_slots = get_valid_time_slots(date)
        time_str = st.selectbox("Preferred Time", valid_slots, label_visibility="collapsed", key="n_time")

        st.write("")
        st.markdown("**4. Select the Treatments**")
        treatments_list_new = [
            "Consult with professionals", "Scaling & Polishing", "Fillings",
            "Root Canal Treatment (RCT)", "Teeth Whitening", 
            "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
            "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
        ]
        
        # Single column for treatments
        selected_treatments = []
        for i, treat in enumerate(treatments_list_new):
            if st.checkbox(treat, key=f"n_treat_{i}"):
                selected_treatments.append(treat)
        
        st.write("")
        if st.button("Book now", type="primary", key="n_submit"):
            if first_name and last_name and phone:
                full_name = f"{first_name} {last_name}"
                treatments_str = ", ".join(selected_treatments) if selected_treatments else "General Checkup"
                
                try:
                    # Save to SINGLE sheet: New_Users_Booking (Append Only)
                    ws_new_booking.append_row([
                        full_name, 
                        phone, 
                        str(date), 
                        time_str, 
                        treatments_str, 
                        "this patient needs to assign doctor", 
                        "Confirmed"
                    ])
                    st.success("✅ Thank you for your appointment. We will shortly send the booking confirmation.")
                except Exception as e:
                    st.error(f"Error saving data: {e}")
            else:
                st.warning("⚠️ Please fill in your Name and Phone Number.")

    # --- TAB 2: RETURN PATIENT ---
    with tab2:
        st.markdown("#### Verify Identity")
        
        if not st.session_state['verified']:
            phone_input = st.text_input("Enter your registered Phone Number", key="verify_phone")
            
            if st.button("Find My Record"):
                try:
                    all_records = ws_exist.get_all_records()
                    found_user = None
                    clean_input = ''.join(filter(str.isdigit, str(phone_input)))
                    
                    if not clean_input:
                         st.warning("Please enter a valid number.")
                    else:
                        for record in all_records:
                            # Clean keys
                            clean_record = {k.strip(): v for k, v in record.items()}
                            
                            # Search Phone
                            sheet_phone_raw = str(clean_record.get("Contact number", "") or clean_record.get("Contact Number", ""))
                            sheet_phone_clean = ''.join(filter(str.isdigit, sheet_phone_raw))
                            
                            if clean_input in sheet_phone_clean or sheet_phone_clean in clean_input:
                                if sheet_phone_clean != "": 
                                    found_user = clean_record
                                    break
                        
                        if found_user:
                            st.session_state['verified'] = True
                            st.session_state['user_data'] = found_user
                            st.rerun()
                        else:
                            st.error(f"❌ Number '{phone_input}' not found in Existing_DB.")

                except Exception as e:
                    st.error(f"Error reading database: {e}")
        
        else:
            # --- DISPLAY INFO ---
            user = st.session_state['user_data']
            
            p_name = user.get("PATIENT NAME") or user.get("Patient Name", "Valued Patient")
            
            # HIDDEN FROM UI
            st.success(f"Welcome Back, **{p_name}**!")
            
            if st.button("Change User"):
                st.session_state['verified'] = False
                st.session_state['user_data'] = {}
                st.rerun()

            st.markdown("---")
            st.markdown("#### New Appointment Details")
            
            # Returning patient form also needs single column treatment? 
            # The image only shows "Select the Treatments" generally. I'll stick to consistent design.
            
            r_date = st.date_input("Date", min_value=datetime.date.today(), key="ret_date")
            r_valid_slots = get_valid_time_slots(r_date)
            r_time_str = st.selectbox("Time", r_valid_slots, key="ret_time")
            
            full_treatments_list = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            r_treat = st.selectbox("Treatment Required", full_treatments_list)
            
            st.write("")
            if st.button("Confirm Booking"):
                try:
                    # --- FINAL MAPPING (INCLUDES 'RE' DATA) ---
                    re_data = user.get("RE") or user.get("Re") or user.get("re", "")
                    
                    save_data = [
                        # 0. FILE #
                        user.get("FILE #") or user.get("FILE", ""), 

                        # 1. Patient Name
                        user.get("PATIENT NAME") or user.get("Patient Name", ""),
                        
                        # 2. Contact Number
                        user.get("Contact number") or user.get("Contact Number", ""),
                        
                        # 3. Data of Birth
                        user.get("DATE OF BIRTH", ""),
                        
                        # 4. Stats
                        user.get("HEIGHT") or user.get("Height", ""),
                        user.get("WEIGHT") or user.get("Weight", ""),
                        user.get("ALLERGY") or user.get("Allergy", ""),
                        
                        # 5. RE Data
                        re_data,
                        
                        # 6. New Booking
                        str(r_date),
                        r_time_str,
                        r_treat,
                        "this patient needs to assign doctor",
                        "Confirmed (Returning)"
                    ]
                    
                    # STRICTLY APPEND ROW (NO DELETION)
                    ws_return.append_row(save_data)
                    st.success("✅ Thank you for your appointment. We will shortly send the booking confirmation.")
                except Exception as e:
                    st.error(f"Error saving booking: {e}")

# === RIGHT COLUMN: INFO PANEL ===
with col2:
    # Use HTML/CSS to align content in the center vertically/horizontally as per the card style
    st.write("") # Spacer
    
    # Logo
    st.image("miami_logo.png", width=150)
    
    st.markdown("<h3>Maimi Dental Clinic</h3>", unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    st.write("")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="font-size: 0.9em; line-height: 1.6;">
        <b>Muraqqabat road, REQA bldg. 1st floor,<br>
        office no. 104. Dubai, UAE.</b><br><br>
        The same building of Rigga Restaurant.<br>
        Al Rigga Metro is the nearest metro station<br>
        exit 2
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Map Link with Icon
    st.markdown("""
        <a href="https://www.google.com/maps/place/Miami+General+Dental+Clinic/@25.2636757,55.325599,17z" target="_blank" style="text-decoration: none; color: white;">
            📍 Google Map
        </a>
    """, unsafe_allow_html=True)



