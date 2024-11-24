import streamlit as st
import json
from streamlit_option_menu import option_menu
import Dashboard, Consumed, LowStock, Analysis
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Spare parts Management System",
    layout="wide",
)

# Function for login
def login():
    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    # ---- LOAD ASSETS ----
    lottie_coding = load_lottiefile("coding.json.json")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        
        # Display instructions for do's and don'ts
        st.title(f":bar_chart: Spare Parts Management System \n \t Developer : Pallavi Kshirsagar \n ")
        st.markdown('<style>div.block-container{padding-top:1rem;}<style>', unsafe_allow_html=True)
        with st.container():
            st.write("---")
        title_html = """
        <div style="background-color:#f0f2f6;padding:5px;border-radius:5px;margin-bottom:20px">
        <h2 style="color:black;text-align:center;font-size:28px;">COMPACTOR MATERIAL MANAGEMENT GUIDELINES:</h2>
        </div>
        """
        st.markdown(title_html, unsafe_allow_html=True)

        left_column, right_column = st.columns([3, 1])
        with left_column:
            st.subheader(" 1) 5 DO'S - ")

            st.write(
                """
                1. USED/FAULTY MACHINE SPARES IMMEDIATELY DISPOSED.
                2. CHECK THE MATERIAL KEPT IS IN ITS PROPER LOCATION.
                3. CONFIRM THE NEW MATERIAL KEPT IN THE COMPACTOR WITH AN ENTRY IN THE COMPACTOR FILE.
                4. CONFIRM THAT THE COMPACTOR IS LOCKED AND THE KEY IS SECURELY KEPT AFTER USE.
                5. UPDATE THE CONSUMED SPARES IN THE COMPACTOR FILE & SAP.
                """
            )

        with st.container():
            st.subheader(" 2) 5 DONT'S - ")

            st.write(
                """
                1. DON'T KEPT USED/FAULTY SPARE IN COMPACTOR.
                2. DON'T MOVE SPARES FROM ITS LOCATION WITHOUT REQUIREMENT.
                3. DON'T FORGET TO UPDATE CONSUMED SPARES IN SAP/COMPACTOR FILE.
                4. DON'T KEPT NEW MATERIAL IN COMPACTOR WITHOUT ENTRY IN COMPACTOR FILE.
                5. DON'T FORGET TO LOCK COMPACTOR AFTER USE AND KEPT KEY AT ITS PROPER LOCATION.
                """
            )

        with right_column:
            st.subheader(" ")
            st_lottie(lottie_coding, height=300, key="coding")

        with st.container():
            st.write("---")
            st.write("[Learn Here: How to Use>](https://www.youtube.com/watch?v=VqgUkExPvLY&t=194s)")
        
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_button = st.sidebar.button("Login")

        if login_button:
            if username == "Spare@2024" and password == "12457801":
                st.session_state.logged_in = True
                # Redirect to home page after successful login
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password. Please try again.")
        else:
            st.sidebar.empty()

# Check if login is successful
login()

# Sidebar with logo
st.sidebar.image("Mahindra-Mahindra-Emblem.png", caption="Mahindra and Mahindra Limited", width=90, 
         output_format="JPEG", use_column_width=True, 
)

# Options menu
if st.session_state.logged_in:
    app = option_menu(
        menu_title='Spare Parts Management System',
        options=['Dashboard', 'Consumed', 'LowStock', 'Analysis'],
        icons=['database-fill', 'clipboard-data-fill', 'card-list', 'bar-chart-line-fill'],
        menu_icon='text-left',
        default_index=0,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": 'white'},
            "icon": {"color": "black", "font-size": "23px"}, 
            "nav-link": {"color": "black", "font-size": "23px", "text-align": "right", "margin": "0px", "--hover-color": "light gray"},
            "nav-link-selected": {"background-color": "#F0F2F6"},
            "menu-title": {"color": "blue", "font-weight": "bold", "font-size": "26px"}
        }
    )

    # Load the selected page
    if app == 'Dashboard':
        Dashboard.app()
    elif app == 'Consumed':
        Consumed.app()
    elif app == 'LowStock':
        LowStock.app()
    elif app == 'Analysis':
        Analysis.app()

    # Add logout option
    st.sidebar.markdown('---')
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.session_state.logged_in = False
        # Redirect to home page after successful logout
        st.rerun() 