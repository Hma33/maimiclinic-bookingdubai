import streamlit as st
import gspread
from google.oauth2.service_account import Credentials # <--- This is the NEW library
from datetime import datetime

# --- 1. PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="Clinic Booking", layout="centered")

# --- 2. DATABASE CONNECTION ---
@st.cache_resource
def get_sheet_connection():
    # Define scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Load credentials from secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # FIX: Handle the "\n" in the private key correctly
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Authorize with the new method
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    return client.open("Clinic_Booking_System")

# --- 3. LOAD DATA (WITH ERROR HANDLING) ---
try:
    SHEET = get_sheet_connection()
    ws_new = SHEET.worksheet("New_Users")
    ws_exist = SHEET.worksheet("Existing_DB")
    ws_final = SHEET.worksheet("Final_Bookings")
except Exception as e:
    st.error(f"🚨 Connection Failed: {e}")
    st.stop()

# --- 4. APP UI ---
st.title("🏥 Clinic Booking Portal")

# Use tabs for the two user flows
tab1, tab2 = st.tabs(["📝 New Patient Registration", "🔄 Existing Patient Booking"])

# --- FLOW 1: NEW PATIENT ---
with tab1:
    st.write("Please register your details below.")
    with st.form("new_user_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        date = st.date_input("Preferred Date")
        time = st.time_input("Preferred Time") 
        treatment = st.selectbox("Treatment Required", ["Dental Checkup", "Skin Consultation", "General Health"])
        
        submitted = st.form_submit_button("Confirm Booking")
        
        if submitted:
            if name and phone:
                # Save to New Users Sheet
                ws_new.append_row([name, phone, str(date), str(time), treatment, str(datetime.now())])
                
                # Assign Doctor
                assigned_doc = "Dr. Smith" if "Dental" in treatment else "Dr. Jones"
                
                # Save to Final Sheet
                ws_final.append_row([name, phone, str(date), str(time), treatment, assigned_doc, "Confirmed"])
                st.success(f"✅ Success! You are booked with {assigned_doc}.")
            else:
                st.warning("Please fill in all fields.")

# --- FLOW 2: EXISTING PATIENT ---
with tab2:
    st.write("Verify your identity to book faster.")
    
    if 'verified' not in st.session_state:
        st.session_state['verified'] = False
        st.session_state['user_name'] = ""

    phone_input = st.text_input("Enter your registered Phone Number")
    verify_btn = st.button("Verify Me")

    if verify_btn:
        try:
            cell = ws_exist.find(phone_input)
            user_data = ws_exist.row_values(cell.row)
            
            st.session_state['verified'] = True
            st.session_state['user_name'] = user_data[0] 
            st.success(f"Welcome back, {user_data[0]}!")
        except:
            st.error("Phone number not found. Please use the New Patient tab.")
            st.session_state['verified'] = False

    if st.session_state['verified']:
        with st.form("existing_booking_form"):
            st.write(f"Booking for: **{st.session_state['user_name']}**")
            ex_date = st.date_input("Date")
            ex_time = st.time_input("Time")
            ex_treat = st.selectbox("Treatment", ["Dental Checkup", "Skin Consultation", "General Health"])
            
            ex_submitted = st.form_submit_button("Book Appointment")
            
            if ex_submitted:
                ws_final.append_row([
                    st.session_state['user_name'],
                    phone_input,
                    str(ex_date),
                    str(ex_time),
                    ex_treat,
                    "Dr. Auto-Assigned",
                    "Confirmed (Returning)"
                ])
                st.success("✅ Booking Confirmed!")
