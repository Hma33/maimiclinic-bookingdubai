# ... [Previous imports remain] ...
from datetime import datetime, timedelta, time

# --- HELPER FUNCTION: GENERATE TIME SLOTS ---
def get_valid_time_slots(selected_date):
    """
    Returns a list of 30-minute time slots based on the day of the week.
    Mon(0), Thu(3), Fri(4), Sat(5), Sun(6): 10:00 AM - 12:00 AM (Midnight)
    Tue(1): 12:00 PM - 10:00 PM
    Wed(2): 02:00 PM - 12:00 AM (Midnight)
    """
    day_idx = selected_date.weekday() # 0=Mon, 6=Sun
    
    # Define start and end hours (24-hour format)
    # Note: 24 represents midnight (end of day)
    if day_idx in [0, 3, 4, 5, 6]: # Mon, Thu, Fri, Sat, Sun
        start_h, end_h = 10, 24 
    elif day_idx == 1: # Tuesday
        start_h, end_h = 12, 22
    elif day_idx == 2: # Wednesday
        start_h, end_h = 14, 24
    else:
        # Fallback (shouldn't happen with valid logic)
        start_h, end_h = 9, 17 

    # Generate 30-min intervals
    slots = []
    current_h = start_h
    current_m = 0
    
    # Loop until we reach the end hour
    while current_h < end_h:
        # Format label (e.g., "10:00 AM")
        is_pm = current_h >= 12
        display_h = current_h if current_h <= 12 else current_h - 12
        if display_h == 0: display_h = 12 # Handle 12 AM/PM edge case
        
        period = "PM" if is_pm else "AM"
        # Special check for Midnight end label if you want "12:00 AM"
        if current_h == 24: 
            display_h, period = 12, "AM"
            
        time_label = f"{display_h:02d}:{current_m:02d} {period}"
        slots.append(time_label)
        
        # Increment by 30 mins
        current_m += 30
        if current_m == 60:
            current_m = 0
            current_h += 1
            
    return slots

# ... [Inside your layout code] ...

# --- FLOW 1: NEW REGISTRATION (UPDATED) ---
with tab1:
    with st.form("new_patient_form"):
        # ... [Name and Phone inputs remain the same] ...
        
        st.markdown("#### 3. Preferred Appointment")
        d_col, t_col = st.columns(2)
        
        with d_col:
            # 1. User picks Date first
            date = st.date_input("Preferred Date", min_value=datetime.today())
            
        with t_col:
            # 2. Logic calculates valid slots for that specific day
            valid_slots = get_valid_time_slots(date)
            
            # 3. User picks from the specific list
            time_str = st.selectbox("Available Time Slots", valid_slots)

        # ... [Rest of the form (Treatments, Button) remains the same] ...
