import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURATION ---
@st.cache_resource
def get_sheet_connection():
    # This reads the secret key we will upload to Streamlit later
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Clinic_Booking_System")

try:
    SHEET = get_sheet_connection()
    ws_new = SHEET.worksheet("New_Users")
    ws_exist = SHEET.worksheet("Existing_DB")
    ws_final = SHEET.worksheet("Final_Bookings")
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# --- UI DESIGN ---
st.set_page_config(page_title="Clinic Booking", layout="centered")
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
        treatment = st.selectbox("Treatment Required", ["Dental Checkup", "Skin Consultation", "General Health"])
        
        submitted = st.form_submit_button("Confirm Booking")
        
        if submitted:
            if name and phone:
                # 1. Save to New Users Sheet
                ws_new.append_row([name, phone, str(date), treatment, str(datetime.now())])
                
                # 2. Assign Doctor (Simple Logic)
                assigned_doc = "Dr. Smith" if "Dental" in treatment else "Dr. Jones"
                
                # 3. Save to Final Sheet
                ws_final.append_row([name, phone, str(date), treatment, assigned_doc, "Confirmed"])
                st.success(f"✅ Success! You are booked with {assigned_doc}.")
            else:
                st.warning("Please fill in all fields.")

# --- FLOW 2: EXISTING PATIENT ---
with tab2:
    st.write("Verify your identity to book faster.")
    
    # Session state to remember if user is verified
    if 'verified' not in st.session_state:
        st.session_state['verified'] = False
        st.session_state['user_name'] = ""

    # Verification Step
    phone_input = st.text_input("Enter your registered Phone Number")
    verify_btn = st.button("Verify Me")

    if verify_btn:
        try:
            # Search for phone in Column B (Index 2 in Python, Col 2 in Sheets)
            # Assuming format: [Name, Phone, ...] in Existing_DB
            cell = ws_exist.find(phone_input)
            user_data = ws_exist.row_values(cell.row)
            
            st.session_state['verified'] = True
            st.session_state['user_name'] = user_data[0] # Assuming Name is first column
            st.success(f"Welcome back, {user_data[0]}!")
        except:
            st.error("Phone number not found. Please use the New Patient tab.")
            st.session_state['verified'] = False

    # Booking Form (Only appears if verified)
    if st.session_state['verified']:
        with st.form("existing_booking_form"):
            st.write(f"Booking for: **{st.session_state['user_name']}**")
            ex_date = st.date_input("Date")
            ex_treat = st.selectbox("Treatment", ["Dental Checkup", "Skin Consultation", "General Health"])
            
            ex_submitted = st.form_submit_button("Book Appointment")
            
            if ex_submitted:
                ws_final.append_row([
                    st.session_state['user_name'],
                    phone_input,
                    str(ex_date),
                    ex_treat,
                    "Dr. Auto-Assigned",
                    "Confirmed (Returning)"
                ])
                st.success("✅ Booking Confirmed!")
