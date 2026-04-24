import streamlit as st
import tempfile
import os
import base64
import requests
from datetime import datetime

# Set up page configuration
st.set_page_config(
    page_title="ASU Library App",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Static Demo Data ---
LIBRARIES = {
    "ASU California Center Library": {
        "location": "Los Angeles / California",
        "hours": "7:30 a.m. to 7 p.m. Pacific Time"
    },
    "Hayden Library": {
        "location": "Tempe campus",
        "hours": "7 a.m. to 12 a.m. for ASU faculty, staff, and students; visitor access 7 a.m. to 9 p.m."
    },
    "Noble Library": {
        "location": "Tempe campus",
        "hours": "24 hours for ASU faculty, staff, and students; visitor access 7 a.m. to 9 p.m."
    },
    "Design and the Arts Library": {
        "location": "Tempe campus",
        "hours": "9 a.m. to 5 p.m."
    },
    "Music Library": {
        "location": "Tempe campus",
        "hours": "8 a.m. to 8 p.m."
    },
    "Downtown Phoenix campus Library": {
        "location": "Downtown Phoenix campus",
        "hours": "7:30 a.m. to 10 p.m. for ASU faculty, staff, and students"
    },
    "Fletcher Library": {
        "location": "West Valley campus",
        "hours": "7:30 a.m. to 10 p.m. for ASU faculty, staff, and students"
    },
    "Polytechnic campus Library": {
        "location": "Polytechnic campus",
        "hours": "8 a.m. to 10 p.m."
    }
}

# Initialize Session State for Screen Routing
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "phone_home"
if "selected_library" not in st.session_state:
    st.session_state.selected_library = "Hayden Library"

def go_to_library_home():
    st.session_state.current_screen = "library_home"

def go_to_occupancy_check():
    st.session_state.current_screen = "occupancy_check"

def go_to_phone_home():
    st.session_state.current_screen = "phone_home"

# --- Custom CSS for Phone Mockup ---
st.markdown(f"""
<style>
    /* Dark background for the whole page (outside the phone) */
    .stApp {{
        background-color: #0E1117;
    }}
    
    /* Turn the main block container into a phone frame */
    .block-container {{
        max-width: 414px !important; /* Standard phone width */
        min-height: 800px;
        background-color: #1A1A1A; /* Phone screen background */
        border: 12px solid #333333; /* Phone bezel */
        border-radius: 40px;
        padding: 1rem 1.5rem 3rem 1.5rem !important;
        margin: 2rem auto !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        position: relative;
        overflow-x: hidden;
    }}
    
    /* Hide sidebar and top header to enhance phone illusion */
    section[data-testid="stSidebar"] {{ display: none; }}
    header[data-testid="stHeader"] {{ display: none; }}
    footer {{ display: none; }}

    /* Phone Status Bar */
    .status-bar {{
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: white;
        margin-top: -5px;
        margin-bottom: 20px;
        padding: 0 5px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* Dynamic Notch */
    .notch {{
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 140px;
        height: 25px;
        background-color: #333333;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        z-index: 999;
    }}

    /* Standard Button Styling overrides for ASU theme inside app */
    div.stButton > button {{
        border-radius: 10px;
        border: 1px solid #FFC627;
        color: #FFC627;
        background-color: transparent;
        font-weight: 600;
    }}
    div.stButton > button:hover {{
        background-color: #FFC627;
        color: #8C1D40;
        border: 1px solid #FFC627;
    }}

    /* Metric Cards Styling */
    div[data-testid="metric-container"] {{
        background-color: #2D3748;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        border: 1px solid #4A5568;
    }}
    
    /* App Headers */
    .app-header {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFC627;
        text-align: center;
        margin-bottom: 5px;
        margin-top: 10px;
    }}
    .app-subheader {{
        font-size: 0.9rem;
        color: #A0AEC0;
        text-align: center;
        margin-bottom: 25px;
    }}

    /* Custom Status Cards */
    .status-card {{
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 15px;
        margin-bottom: 15px;
    }}
    .status-card h3 {{ margin: 0; font-size: 1.3rem; font-weight: bold; }}
    .status-card p {{ margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.9; }}
    
    .status-red {{ background: linear-gradient(135deg, #F56565, #C53030); }}
    .status-yellow {{ background: linear-gradient(135deg, #F6E05E, #D69E2E); color: #1A202C !important; }}
    .status-yellow h3, .status-yellow p {{ color: #1A202C !important; }}
    .status-green {{ background: linear-gradient(135deg, #68D391, #2F855A); }}
    
    /* Library Card */
    .library-card {{
        background-color: #2D3748;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #8C1D40;
        margin-bottom: 20px;
    }}
    .library-card h4 {{ color: white; margin: 0 0 5px 0; }}
    .library-card p {{ color: #E2E8F0; font-size: 0.85rem; margin: 0; }}
    .library-note {{ color: #A0AEC0; font-size: 0.75rem; margin-top: 10px; font-style: italic; }}

</style>

<div class="notch"></div>
<div class="status-bar">
    <span>{datetime.now().strftime("%H:%M")}</span>
    <span>5G &nbsp;🔋 100%</span>
</div>
""", unsafe_allow_html=True)

# API Configuration
ROBOFLOW_API_KEY = "XDZZ7pLIRDHcNZ2R483M"

# ==========================================
# SCREEN 1: PHONE HOME SCREEN
# ==========================================
if st.session_state.current_screen == "phone_home":
    # Inject CSS specific to the Home Screen
    st.markdown("""
    <style>
        /* Home Screen Wallpaper */
        .block-container {
            background: linear-gradient(to bottom, #1A1A24, #000000) !important;
        }
        
        /* Make the Streamlit button invisible and pull it up over the image */
        div.stButton {
            margin-top: -110px !important;
            z-index: 10 !important;
            position: relative;
        }
        div.stButton > button {
            height: 110px !important;
            width: 100% !important;
            opacity: 0 !important; /* Completely transparent */
            cursor: pointer !important;
            background-color: transparent !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Push content down slightly
    st.write("")
    st.write("")
    
    # Use a 4-column grid to simulate an app grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Load and encode the logo image
        with open("ASU-logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        # Render the icon and text via HTML
        st.markdown(f"""
        <div style="text-align: center; pointer-events: none;">
            <img src="data:image/png;base64,{logo_b64}" style="background-color: white; border-radius: 16px; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); width: 100%; aspect-ratio: 1/1; object-fit: contain;">
            <p style="color: white; font-size: 0.8rem; font-weight: 500; margin-top: 5px; font-family: -apple-system, sans-serif;">ASU Library</p>
        </div>
        """, unsafe_allow_html=True)
        
        # This button is invisible and overlays the HTML above it
        st.button("OpenApp", on_click=go_to_library_home, use_container_width=True)

# ==========================================
# SCREEN 2: LIBRARY HOME SCREEN
# ==========================================
elif st.session_state.current_screen == "library_home":
    st.button("⬅️ Exit App", on_click=go_to_phone_home)
    
    st.markdown('<p class="app-header">ASU Library</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subheader">Find space, check hours, and view seat availability</p>', unsafe_allow_html=True)
    
    st.markdown("### Select a library")
    selected = st.selectbox("Library", list(LIBRARIES.keys()), label_visibility="collapsed")
    st.session_state.selected_library = selected
    
    lib_info = LIBRARIES[selected]
    
    st.markdown(f"""
    <div class="library-card">
        <h4>📍 {lib_info['location']}</h4>
        <p><strong>Today's Hours:</strong> {lib_info['hours']}</p>
        <p class="library-note">Hours may vary during holidays and finals week. Real deployment would pull live hours from ASU Library systems.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Seat Availability")
    st.markdown("Check real-time occupancy using the library cameras.")
    st.button("Check Occupancy", on_click=go_to_occupancy_check, use_container_width=True)

# ==========================================
# SCREEN 3: OCCUPANCY CHECK (ROBOFLOW)
# ==========================================
elif st.session_state.current_screen == "occupancy_check":
    # Top nav bar
    st.button("⬅️ Back to Library Home", on_click=go_to_library_home)
    
    st.markdown(f'<p class="app-header">{st.session_state.selected_library}</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subheader">Live Seat Occupancy Detection</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload photo of study area", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is None:
        st.info("Tap to upload an image from your camera roll.")
    else:
        image_bytes = uploaded_file.read()
        
        with st.spinner("Analyzing space..."):
            try:
                # --- API Call ---
                url = "https://detect.roboflow.com/infer/workflows/shanes-workspace-hwgpf/library-occupancy-heatmap-poc-1776907651480"
                payload = {
                    "api_key": ROBOFLOW_API_KEY,
                    "inputs": {
                        "image": {
                            "type": "base64",
                            "value": base64.b64encode(image_bytes).decode('utf-8')
                        }
                    }
                }
                
                headers = {"Content-Type": "application/json"}
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                api_result = response.json()
                result = api_result.get("outputs", [{}])
                
                # --- Prediction Processing ---
                try:
                    predictions = result[0]["tracked_detections"]["predictions"]
                except KeyError:
                    predictions = []
                
                occupied_seats = 0
                empty_seats = 0
                
                for pred in predictions:
                    label = pred.get("class", "")
                    if label == "Occupied Seat":
                        occupied_seats += 1
                    elif label == "Empty Seat":
                        empty_seats += 1
                
                # --- Metrics Calculation ---
                total_seats = occupied_seats + empty_seats
                occupancy_rate = (occupied_seats / total_seats * 100) if total_seats > 0 else 0.0
                
                # --- Recommendation Banner ---
                if occupancy_rate >= 80:
                    st.markdown("""
                    <div class="status-card status-red">
                        <h3>🚨 Very Busy</h3>
                        <p>Highly occupied. Seats are limited.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif occupancy_rate >= 50:
                    st.markdown("""
                    <div class="status-card status-yellow">
                        <h3>⚠️ Moderately Busy</h3>
                        <p>Filling up, but some seats available.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif occupancy_rate > 5:
                    st.markdown("""
                    <div class="status-card status-green">
                        <h3>✅ Plenty of Space</h3>
                        <p>Quiet. Great time to grab a seat!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="status-card status-green">
                        <h3>👻 Ghost Town</h3>
                        <p>Practically empty. Pick any seat!</p>
                    </div>
                    """, unsafe_allow_html=True)

                # --- Metrics Row ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total", total_seats)
                with col2:
                    st.metric("Occupied", occupied_seats)
                with col3:
                    st.metric("Open", empty_seats)
                
                # --- Occupancy Meter ---
                if occupancy_rate < 50:
                    bar_color = "#38a169" # green
                elif occupancy_rate < 80:
                    bar_color = "#d69e2e" # orange
                else:
                    bar_color = "#e53e3e" # red
                    
                st.markdown(f"**Occupancy Level: {occupancy_rate:.0f}%**")
                st.markdown(f"""
                <div style="width: 100%; background-color: #4A5568; border-radius: 10px; margin-bottom: 20px;">
                    <div style="width: {occupancy_rate}%; background-color: {bar_color}; height: 20px; border-radius: 10px; transition: width 0.5s ease-in-out;"></div>
                </div>
                """, unsafe_allow_html=True)
                    
                st.markdown("---")
                
                # --- Image Display (Stacked for Mobile) ---
                st.markdown("##### 📷 Live Feed")
                st.image(image_bytes, use_container_width=True)
                
                st.markdown("**AI Detection**")
                annotated_base64 = result[0].get("annotated_image", "")
                
                if isinstance(annotated_base64, dict):
                    annotated_base64 = annotated_base64.get("value", "")
                    
                if annotated_base64 and isinstance(annotated_base64, str):
                    if "," in annotated_base64:
                        annotated_base64 = annotated_base64.split(",")[1]
                    annotated_bytes = base64.b64decode(annotated_base64)
                    st.image(annotated_bytes, use_container_width=True)
                else:
                    st.info("No annotated image returned.")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
