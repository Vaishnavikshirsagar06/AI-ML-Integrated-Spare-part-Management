import pandas as pd
import streamlit as st

# Define the file path
df_path = r'C:\Users\25021648\Desktop\last smps\uploaded_file.xlsx'

@st.cache_data
def load_data():
    return pd.read_excel(df_path)

def filter_by_price_range(df, price_range):
    if price_range == "Choose an option":
        return df
    min_price, max_price = map(float, price_range.split("-"))
    return df[(df["Moving Average Price"] >= min_price) & (df["Moving Average Price"] <= max_price)]

def app():
    title_html = """
    <div style="background-color:#f0f2f6;padding:5px;border-radius:5px;margin-bottom:20px">
    <h2 style="color:black;text-align:center;font-size:28px;">Low Stock Spares List:</h2>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    
    df = pd.read_excel(df_path)

    if df is not None:
        # Apply condition "Unrestricted Stock <= Reorder Point"
        filtered_df = df[df["Unrestricted Stock"] <= df["Reorder Point"]]

        # Sidebar filters
        st.sidebar.subheader("Please Filter Here:")

        # Price filter
        price_ranges = ["Choose an option", "0-500", "500-1000", "1000-3000", "3000-5000", "5000-10000", "10000-20000", "20000-30000", "30000-40000", "40000-50000", "50000-100000"]
        selected_price_range = st.sidebar.selectbox("Select price range:", price_ranges)
        filtered_df_price = filter_by_price_range(filtered_df, selected_price_range)

        # Obsolete filter
        obsolete = st.sidebar.multiselect("Select obsolete indicators:", options=filtered_df["ABC Indicator"].unique())
        if obsolete:
            filtered_df_obsolete = filtered_df_price[filtered_df_price['ABC Indicator'].isin(obsolete)]
        else:
            filtered_df_obsolete = filtered_df_price

        # Categorize filter
        categorize = st.sidebar.multiselect("Select categories:", options=filtered_df["Categorized"].unique())
        if categorize:
            filtered_df_categorized = filtered_df_obsolete[filtered_df_obsolete['Categorized'].isin(categorize)]
        else:
            filtered_df_categorized = filtered_df_obsolete

        # Display filtered data with additional filters
        st.subheader("Filtered Data:")
        if filtered_df_categorized.empty:
            st.write("No spare parts meet the selected criteria.")
        else:
            st.dataframe(filtered_df_categorized)
    else:
        st.error("Unable to read the data from the specified file path.")

# Run the app function
if __name__ == "__main__":
    app()

