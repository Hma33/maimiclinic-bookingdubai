import streamlit as st
import gspread
from google.oauth2.service_account import Credentials # New library
from datetime import datetime

# --- CONFIGURATION ---
@st.cache_resource
def get_sheet_connection():
    # Define the scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Load credentials from secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # FIX: Handle the "\n" in the private key correctly
    # (Streamlit secrets sometimes escape newlines, this fixes it)
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Authorize with the new method
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    return client.open("Clinic_Booking_System")

# ... The rest of your code remains the same ...
