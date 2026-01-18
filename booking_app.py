import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide")

# Custom CSS to match your Figma Design
st.markdown("""
    <style>
    /* 1. Main Background - Deep Navy Blue */
    .stApp {
        background-color: #101d2d;
    }
    
    /* 2. Remove top white bar and padding */
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 3. The White Form Card (Left Side) */
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
    }

    /* 4. The Info Card (Right Side) - Darker Navy */
    .info-card {
        background-color: #1a2634;
        padding: 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        height: 100%;
    }
    .info-card h3 { color: white; margin-bottom: 20px; }
    .info-card p { font-size: 14px; line-height: 1.6; color: #cbd5e1; }
    .info-card a { color: #fff; text-decoration: underline; }

    /* 5. Inputs & Buttons Styling */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #eef2f6; /* Light grey input background */
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stFormSubmitButton"] button {
        background-color: #101d2d;
        color: white;
        border: none;
        padding: 10px 30px;
        border-radius: 5px;
        width: 100%;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Hide the default Streamlit anchor links (little chain icons) */
    .css-15zrgzn {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION (Same as before) ---
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
    st.error(f"Database Error: {e}")
    st.stop()

# --- 3. LAYOUT: TWO COLUMNS ---
col_form, col_info = st.columns([2, 1], gap="large")

# --- RIGHT COLUMN: STATIC INFO (The Dark Card) ---
with col_info:
    # We use HTML to create the dark card look exactly like your design
    st.markdown("""
        <div class="info-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3004/3004458.png" width="80" style="margin-bottom: 20px; filter: invert(1);">
            <h3>Maimi Dental Clinic</h3>
            <hr style="border-color: #334155; margin: 20px 0;">
            <p>
                Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.
            </p>
            <br>
            <p>
                The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station exit 2.
            </p>
            <br>
            <p>📍 <a href="https://maps.google.com" target="_blank">Google Map</a></p>
        </div>
    """, unsafe_allow_html=True)

# --- LEFT COLUMN: THE BOOKING FORM (The White Card) ---
with col_form:
    # Title
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    
    # Tabs styling wrapper
    tab_new, tab_return = st.tabs(["New Registration", "Return"])

    # === TAB 1: NEW REGISTRATION ===
    with tab_new:
        st.write("") # Spacer
        with st.form("new_reg_form"):
            st.markdown("##### 1. Full Name")
            c1, c2 = st.columns(2)
            first_name = c1.text_input("First Name")
            last_name = c2.text_input("Last Name")

            st.markdown("##### 2. Phone Number (WhatsApp)")
            phone = st.text_input("Phone Number", label_visibility="collapsed", placeholder="Enter your number")

            st.markdown("##### 3. Preferred Appointment Date and Time")
            c3, c4 = st.columns(2)
            date = c3.date_input("Preferred Date")
            time = c4.time_input("Preferred Time")

            st.markdown("##### 4. Select the Treatments")
            # List of treatments from your image
            treatment_options = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            # Create checkboxes
            selected_treatments = []
            for t in treatment_options:
                if st.checkbox(t):
                    selected_treatments.append(t)

            st.write("") # Spacer
            submitted = st.form_submit_button("Book now")

            if submitted:
                if first_name and last_name and phone and selected_treatments:
                    full_name = f"{first_name} {last_name}"
                    treatments_str = ", ".join(selected_treatments)
                    
                    ws_new.append_row([full_name, phone, str(date), str(time), treatments_str, str(datetime.now())])
                    ws_final.append_row([full_name, phone, str(date), str(time), treatments_str, "New Patient", "Confirmed"])
                    
                    st.success("✅ Registration Complete!")
                else:
                    st.error("Please fill in name, phone, and select at least one treatment.")

    # === TAB 2: RETURN / EXISTING ===
    with tab_return:
        st.write("")
        st.markdown("##### 1. Verify your identity to book faster.")
        
        # Verify Section
        if 'verified' not in st.session_state:
            st.session_state['verified'] = False
            st.session_state['v_name'] = ""

        if not st.session_state['verified']:
            v_phone = st.text_input("Enter your registered Phone Number", key="v_input")
            if st.button("Verify me"):
                try:
                    cell = ws_exist.find(v_phone)
                    row_data = ws_exist.row_values(cell.row)
                    st.session_state['verified'] = True
                    st.session_state['v_name'] = row_data[0] # Assuming Name is Col 1
                    st.rerun() # Refresh to show the booking form
                except:
                    st.error("Phone number not found.")
        
        # Booking Section (Only shows if verified)
        else:
            # The "Welcome Back" blue banner
            st.info(f"Welcome Back!!! {st.session_state['v_name']}")
            
            with st.form("return_booking_form"):
                st.markdown("##### 3. Preferred Appointment Date and Time")
                c5, c6 = st.columns(2)
                r_date = c5.date_input("Preferred Date")
                r_time = c6.time_input("Preferred Time")

                st.markdown("##### 4. Select the Treatments")
                r_selected_treatments = []
                for t in treatment_options:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_selected_treatments.append(t)

                st.write("")
                r_submitted = st.form_submit_button("Book now")

                if r_submitted:
                    treatments_str = ", ".join(r_selected_treatments)
                    ws_final.append_row([
                        st.session_state['v_name'], 
                        st.session_state.get('v_input', 'Existing'), 
                        str(r_date), str(r_time), 
                        treatments_str, 
                        "Returning", "Confirmed"
                    ])
                    st.success("✅ Booking Confirmed!")
