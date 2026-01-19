import streamlit as st
import datetime

# 1. Page Configuration: Set layout to 'wide' to allow side-by-side columns
st.set_page_config(page_title="Dental Clinic Form", layout="wide")

# 2. Custom CSS to mimic the specific UI styling
# We inject CSS to style the second column dark blue and round the corners
st.markdown("""
<style>
    /* Main container background */
    .main {
        background-color: #f0f2f6;
    }
    
    /* Style the second column (The Info Panel) */
    [data-testid="column"]:nth-of-type(2) {
        background-color: #1E2A38; /* Dark Navy Blue */
        border-radius: 15px;
        padding: 30px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Text color fixes for the dark column */
    [data-testid="column"]:nth-of-type(2) h2, 
    [data-testid="column"]:nth-of-type(2) p, 
    [data-testid="column"]:nth-of-type(2) a {
        color: white !important;
    }

    /* Style the Submit Button to look like 'Book Now' */
    .stButton > button {
        background-color: #1E2A38;
        color: white;
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .stButton > button:hover {
        background-color: #2c3e50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 3. Create Layout: Two columns (Left is wider 2/3, Right is narrower 1/3)
col1, col2 = st.columns([2, 1], gap="large")

# --- LEFT COLUMN: The Form ---
with col1:
    st.title("Dental Clinic Appointment and Treatment Form")
    
    # Tabs for Registration Type
    tab1, tab2 = st.tabs(["New Registration", "Return"])
    
    with tab1:
        # We use a form container so the app doesn't reload on every input
        with st.form("appointment_form"):
            
            # Section 1: Name
            st.markdown("#### 1. Full Name")
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First Name", placeholder="e.g. John")
            with c2:
                last_name = st.text_input("Last Name", placeholder="e.g. Doe")
            
            # Section 2: Contact
            st.markdown("#### 2. Phone Number (WhatsApp)")
            phone = st.text_input("Phone Number", placeholder="+971 ...")
            
            # Section 3: Date & Time
            st.markdown("#### 3. Preferred Appointment Date and Time")
            d_col, t_col = st.columns(2)
            with d_col:
                date = st.date_input("Preferred Date", min_value=datetime.date.today())
            with t_col:
                time = st.time_input("Preferred Time", value=datetime.time(9, 00))
            
            # Section 4: Treatments (Checkboxes)
            st.markdown("#### 4. Select the Treatments")
            
            treatments_list = [
                "Consult with professionals", "Scaling & Polishing", "Fillings",
                "Root Canal Treatment (RCT)", "Teeth Whitening", 
                "Routine and Wisdom Teeth Extractions", "Panoramic and Periapical X-ray",
                "Crown & Bridge", "Veneers", "Kids Treatment", "Partial & Full Denture"
            ]
            
            selected_treatments = []
            # Create a simplified list view
            for treat in treatments_list:
                if st.checkbox(treat):
                    selected_treatments.append(treat)
            
            st.write("") # Spacer
            
            # Submit Button
            submitted = st.form_submit_button("Book now")
            
            if submitted:
                if not first_name or not phone:
                    st.error("Please fill in your name and phone number.")
                else:
                    st.success(f"Thank you {first_name}! Appointment booked for {date}.")
                    # Here you would connect to a database or send an email

# --- RIGHT COLUMN: The Info Panel ---
with col2:
    # Use an emoji or upload an actual logo using st.image()
    st.markdown("<div style='font-size: 80px;'>🦷</div>", unsafe_allow_html=True) 
    
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
