import pandas as pd
import streamlit as st
import os
import calendar

# Function to load data from a specified file path
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        st.error(f"File not found at {file_path}. Please check the path.")
        return None

def app():
    title_html = """
    <div style="background-color:#f0f2f6;padding:5px;border-radius:5px;margin-bottom:20px">
    <h2 style="color:black;text-align:center;font-size:28px;">Consumed Spare Parts List:</h2>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    
    def get_file_path(file_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, file_name)
    
    # Specify the file path
    df_path = r'C:\Users\25021648\Desktop\last smps\uploaded_file.xlsx'
    df = pd.read_excel(df_path)
    
    if df is not None:  # Check if df is not None
        
        st.subheader("Search the Spare Here: ")
        st.write(df)
        
        # Sidebar filters
        st.sidebar.header("Please Filter Here:")
        
        if "Material No" in df.columns:  # Check if 'Material No' column exists
            Material_No = st.sidebar.multiselect("Select the Material:", options=df["Material No"].unique())
            Material_Description = st.sidebar.multiselect("Select the Material Description:", options=df["Material Description"].unique())
            
            # Filter dataframe
            filtered_df = df[
                df['Material No'].isin(Material_No) |
                df['Material Description'].isin(Material_Description) 
            ]
            
            # Add new columns
            date = st.sidebar.date_input('Date')
            quantity = st.sidebar.number_input('Quantity', value=0)
            consumption_reason = st.sidebar.selectbox('Consumption Reason', ['PM', 'BD'])
            
            # Display filtered dataframe
            st.subheader("Filtered data: ")
            st.write(filtered_df)
            
            # Update dataframe with new columns
            if st.sidebar.button('Add Consumption'):
                if date and quantity and consumption_reason:
                    # Create a copy of the filtered dataframe
                    updated_df = filtered_df.copy()
                    # Find the index of the selected rows
                    selected_indices = filtered_df.index
                    # Update the 'Date', 'Quantity', and 'Consumption Reason' columns for the selected rows
                    updated_df.loc[selected_indices, 'Date'] = date
                    updated_df.loc[selected_indices, 'Quantity'] = quantity
                    updated_df.loc[selected_indices, 'Consumption Reason'] = consumption_reason
                    
                    # Save updated data to CSV file
                    csv_file_path = get_file_path('Consumed_Spare_Parts_List.csv')
                    if os.path.exists(csv_file_path):
                        updated_df.to_csv(csv_file_path, mode='a', header=False, index=False)
                    else:
                        updated_df.to_csv(csv_file_path, index=False)
        else:
            st.error("Column 'Material No' does not exist in the DataFrame.")
    
    else:
        return None
    
    # Read and display consumed spare parts list from CSV file
    csv_file_path = get_file_path('Consumed_Spare_Parts_List.csv')
    try:
        consumed_df = pd.read_csv(csv_file_path)
        
        def save_to_csv(consumed_df, csv_file):
            consumed_df.to_csv(csv_file, index=False)
            
        # Streamlit App
        st.subheader('Consumed Spare Parts List:')
        
        # Display DataFrame initially
        edited_df = st.dataframe(consumed_df)
        def get_consumed_df():
            csv_file_path = get_file_path('Consumed_Spare_Parts_List.csv')
            if os.path.exists(csv_file_path):
                return pd.read_csv(csv_file_path)
            else:
                return pd.DataFrame()
        
        # Display and edit DataFrame with password
        password = st.text_input("Enter password to edit:")
        if password == "12356788":
            # Display edited DataFrame for editing
            edited_df = st.data_editor(consumed_df, num_rows="dynamic")
            
            # Save changes to CSV file
            save_button = st.button("Save Changes")
            if save_button:
                save_to_csv(edited_df, csv_file_path)
                st.success("Saved Changes Successfully!")
                
        elif password.strip() != '' and edited_df is not None:
            st.warning("Incorrect password. You do not have permission to edit.")
            
        # Calculate revenue
        consumed_df['Revenue'] = consumed_df['Moving Average Price'] * consumed_df['Quantity']
        
        # Define function to get week number from date
        def categorize_weeks(input_date):
            year = input_date.year
            month = input_date.month
            first_day = pd.Timestamp(year, month, 1)
            last_day = pd.Timestamp(year, month, calendar.monthrange(year, month)[1])
            current_date = first_day
            categorized_weeks = []
            if current_date.weekday() == 6:
                while current_date <= last_day:
                    week_start = current_date
                    week_end = current_date + pd.Timedelta(days=6)
                    if week_end > last_day:
                        week_end = last_day
                    categorized_weeks.append((week_start, week_end))
                    current_date = week_end + pd.Timedelta(days=1)
            else:
                week_start = current_date - pd.Timedelta(days=current_date.weekday())
                while current_date <= last_day:
                    week_end = week_start + pd.Timedelta(days=6)
                    if week_end.month != month:
                        week_end = pd.Timestamp(year, month, calendar.monthrange(year, month)[1])
                    categorized_weeks.append((week_start, week_end))
                    week_start = week_end + pd.Timedelta(days=1)
                    current_date = week_start
                    
            input_timestamp = pd.Timestamp(input_date)
            week_number = None
            
            for i, (week_start, week_end) in enumerate(categorized_weeks):
                if input_timestamp >= week_start and input_timestamp <= week_end:
                    week_number = i + 1
                    break
                    
            return week_number
        
        # Convert 'Date' column to datetime format
        consumed_df['Date'] = pd.to_datetime(consumed_df['Date'])
        
        # Group by year, month, and week number and sum revenue
        weekly_revenue = consumed_df.groupby([consumed_df['Date'].dt.year.rename('Year'), consumed_df['Date'].dt.month.rename('Month'), consumed_df['Date'].apply(lambda x: categorize_weeks(x)).rename('Week')]).agg({'Revenue': 'sum'}).reset_index()
        
        # Pivot table to rearrange the data for display
        pivot_table = weekly_revenue.pivot_table(index='Month', columns='Week', values='Revenue', aggfunc='sum', fill_value=0, margins=False)
        
        # Drop columns with all zeros
        pivot_table = pivot_table.loc[:, (pivot_table != 0).any(axis=0)]
        
        # Rename columns to 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'
        pivot_table.columns = ['Week ' + str(col) for col in pivot_table.columns]
        
        # Convert month number to month abbreviation
        pivot_table.index = [calendar.month_abbr[month] for month in pivot_table.index]
        
        # Calculate the total revenue for each month
        monthly_totals = pivot_table.sum(axis=1)
        
        # Append the total column to the pivot table
        pivot_table['Total'] = monthly_totals
        
        # Reorder columns, moving 'Total' after 'Week 5' or appending at the end
        column_order = list(pivot_table.columns)
        
        pivot_table = pivot_table[column_order]
        
        # Display revenue in nice table if not hidden
        if not st.sidebar.checkbox('Hide Revenue Analysis'):
            st.subheader("Revenue Analysis:")
            st.write("Weekly and Monthly Revenue:")
            st.table(pivot_table)
        total_weekly_revenue = pivot_table['Total'].sum()

            # Display the small row for total revenue
        st.markdown(f"**Total Revenue:** {total_weekly_revenue:.2f}")

    except FileNotFoundError:
        st.write("No consumed spare parts yet.")

if __name__ == "__main__":
    app()

