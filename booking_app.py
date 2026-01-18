import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Maimi Dental Clinic", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (THE DESIGN ENGINE) ---
st.markdown("""
    <style>
    /* RESET & BACKGROUND */
    .stApp {
        background-color: #0E1621; /* Deep Navy Background */
        font-family: 'Arial', sans-serif;
    }
    
    /* HIDE STREAMLIT ELEMENTS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max_width: 1200px;
    }

    /* --- LEFT CARD: THE FORM (White) --- */
    /* We target the specific container for the left column */
    div[data-testid="column"]:nth-of-type(1) > div {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 8px 0px 0px 8px; /* Rounded Left Corners */
        height: 800px; /* Fixed height for alignment */
        overflow-y: auto;
    }

    /* --- RIGHT CARD: THE INFO (Dark) --- */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #151f2b; /* Slightly lighter navy for contrast */
        padding: 40px;
        border-radius: 0px 8px 8px 0px; /* Rounded Right Corners */
        height: 800px;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    /* --- INPUT FIELDS STYLING --- */
    /* Remove default borders and make them light grey */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #E6E8EA !important;
        border: none !important;
        color: #333 !important;
        border-radius: 4px !important;
    }
    /* Labels */
    .stMarkdown p {
        font-size: 14px;
        font-weight: 500;
        color: #333;
    }
    
    /* --- TABS STYLING --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #666;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #0E1621 !important;
        border-bottom: 3px solid #b91c1c !important; /* The Red Underline */
    }

    /* --- BUTTON STYLING --- */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #0E1621;
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        width: 150px;
        border-radius: 4px;
        transition: background 0.3s;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #2c3e50;
    }
    
    /* Checkbox spacing */
    div[data-baseweb="checkbox"] {
        margin-bottom: 8px;
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

# --- 4. UI LAYOUT ---

# Create two columns: Left (Form) and Right (Info)
col_left, col_right = st.columns([1.5, 1], gap="small")

# === RIGHT COLUMN (Static Info Card) ===
with col_right:
    # We use pure HTML here because this part is static
    st.markdown("""
        <div style="margin-top: 50px;">
            <div style="background-color: #000; width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px;">🦷</span>
            </div>
            <h2 style="color: white; margin-bottom: 40px;">Maimi Dental Clinic</h2>
            
            <hr style="border-color: #334155; width: 80%; margin: 0 auto 30px auto; opacity: 0.3;">
            
            <div style="text-align: center; color: #cbd5e1; font-size: 14px; line-height: 1.8;">
                <p>Muraqqabat road, REQA bldg. 1st floor,<br>
                office no. 104. Dubai, UAE.</p>
                <br>
                <p>The same building of Rigga Restaurant.<br>
                Al Rigga Metro is the nearest metro station exit 2</p>
            </div>
            
            <div style="margin-top: 40px;">
                <a href="https://maps.google.com" target="_blank" style="color: white; text-decoration: none; font-weight: bold;">
                    📍 Google Map
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === LEFT COLUMN (Interactive Form) ===
with col_left:
    st.markdown("### Dental Clinic Appointment and Treatment Form")
    
    # Tabs
    tab1, tab2 = st.tabs(["New Registration", "Return"])
    
    # --- TAB 1: NEW REGISTRATION ---
    with tab1:
        with st.form("new_user_form"):
            st.write("") # Spacer
            st.markdown("**1. Full Name**")
            c1, c2 = st.columns(2)
            f_name = c1.text_input("First Name", label_visibility="collapsed", placeholder="First Name")
            l_name = c2.text_input("Last Name", label_visibility="collapsed", placeholder="Last Name")
            
            st.markdown("**2. Phone Number (WhatsApp)**")
            phone = st.text_input("Phone", label_visibility="collapsed", placeholder="Enter Phone Number")
            
            st.markdown("**3. Preferred Appointment Date and Time**")
            c3, c4 = st.columns(2)
            date = c3.date_input("Date", label_visibility="collapsed")
            time = c4.time_input("Time", label_visibility="collapsed")
            
            st.markdown("**4. Select the Treatments**")
            # Treatments List
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
                if f_name and phone:
                    full_name = f"{f_name} {l_name}"
                    t_str = ", ".join(selected)
                    # Update Sheets
                    ws_new.append_row([full_name, phone, str(date), str(time), t_str, str(datetime.now())])
                    ws_final.append_row([full_name, phone, str(date), str(time), t_str, "New", "Confirmed"])
                    st.success("✅ Registration Successful!")
                else:
                    st.error("Please fill in required fields.")

    # --- TAB 2: RETURN USER ---
    with tab2:
        st.write("")
        st.markdown("**1. Verify your identity to book faster.**")
        
        # We need a container to hold the verify state
        if 'verified' not in st.session_state:
            st.session_state.verified = False
            st.session_state.v_name = ""

        if not st.session_state.verified:
            v_phone = st.text_input("Enter your registered Phone Number")
            if st.button("Verify me"):
                try:
                    cell = ws_exist.find(v_phone)
                    data = ws_exist.row_values(cell.row)
                    st.session_state.verified = True
                    st.session_state.v_name = data[0] # Name is Col 1
                    st.rerun()
                except:
                    st.error("Number not found.")
        
        else:
            # Verified State
            st.info(f"Welcome Back, {st.session_state.v_name}!")
            
            with st.form("return_form"):
                st.markdown("**3. Preferred Appointment Date and Time**")
                rc1, rc2 = st.columns(2)
                r_date = rc1.date_input("Date")
                r_time = rc2.time_input("Time")
                
                st.markdown("**4. Select Treatments**")
                r_selected = []
                for t in treatments:
                    if st.checkbox(t, key=f"r_{t}"):
                        r_selected.append(t)
                
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
