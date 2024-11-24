import os
import pandas as pd
import streamlit as st

# Directory to save uploaded files
upload_dir = r"C:\Users\25021648\Desktop\last smps"
file_name = "uploaded_file.xlsx"
file_path = os.path.join(upload_dir, file_name)

# Ensure the upload directory exists
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# Define the correct password for file upload
correct_password = "12356"

# Function to check password
@st.cache_data
def check_password(password):
    return password == correct_password

# Function to read the Excel file and return the DataFrame
@st.cache_data(ttl=600)
def read_excel_file(file_mod_time):
    df = pd.read_excel(file_path, sheet_name="RawData")
    return df

# Function to save uploaded file
def save_uploaded_file(uploaded_file):
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Update the session state to trigger cache invalidation
    st.session_state['file_mod_time'] = os.path.getmtime(file_path)
    st.session_state['dataframe'] = read_excel_file(st.session_state['file_mod_time'])

def app():
    title_html = """
    <div style="background-color:#f0f2f6;padding:5px;border-radius:5px;margin-bottom:20px">
    <h2 style="color:black;text-align:center;font-size:28px;">Dashboard:</h2>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)

    # Title and search
    st.subheader("Search Spare Here:")

    # Read Excel file if password is correct
    password = st.text_input("Enter password to upload file:", type="password")
    if password and check_password(password):
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
        if uploaded_file is not None:
            # Save the uploaded file
            save_uploaded_file(uploaded_file)
            st.success("File uploaded successfully!")
    elif password:
        st.error("Incorrect password. Please try again.")

    # Initialize session state if not already done
    if 'file_mod_time' not in st.session_state and os.path.exists(file_path):
        st.session_state['file_mod_time'] = os.path.getmtime(file_path)
        st.session_state['dataframe'] = read_excel_file(st.session_state['file_mod_time'])

    # Check if the file exists
    if 'dataframe' in st.session_state:
        df = st.session_state['dataframe']
        st.write(df)  # Display the DataFrame

        # Sidebar filters
        st.sidebar.header("Please Filter Here:")

        # Options To Choose Location Wise
        location_options = ["Select the Location:", "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "DIE MAINT", "E1", "EOL RH INS", "G2", "I1", "I3", "J1", "J2", "K1", "K2", "L1", "L2", "M1", "NA", "NEAR", "NW", "OIL", "PIT", "RACK A1", "RACK A2", "RACK A3", "RACK A4", "RACK A7", "RACK A8", "RACK B1", "RACK B2", "RACK B3", "RACK B4", "RACK C3", "RACK C6", "RACK C7", "RACK C8", "RACK D3", "RACK D9", "RACK N", "RACK OPP", "SOUTH", "Y", "YELLOW"]
        st.subheader("Filtered Spare Parts Here:")
        df['Storage Bin'] = df['Storage Bin'].fillna('')

        selected_locations = st.sidebar.multiselect("Select the Location:", options=location_options)  # Location selection
        Material_No = st.sidebar.multiselect("Select the Material:", options=df["Material No"].unique())  # Material_No selection
        Material_Description = st.sidebar.multiselect("Select the Material Description:", options=df["Material Description"].unique())  # Material_Description selection
        obsolete = st.sidebar.multiselect("Select the obsolete:", options=df["ABC Indicator"].unique())

        # Filter the DataFrame based on selected values
        filtered_df = df[
            df['Storage Bin'].str.startswith(tuple(str(loc) for loc in selected_locations)) |
            df['Material No'].isin(Material_No) |
            df['Material Description'].isin(Material_Description) |
            df['ABC Indicator'].isin(obsolete)
        ]

        # Display the filtered DataFrame
        st.write(filtered_df)
    else:
        st.info("Please upload a file to display data.")

if __name__ == "__main__":
    app()


