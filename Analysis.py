import streamlit as st
import pandas as pd
import os
import calendar
import plotly.express as px


def app():
    title_html = """
    <div style="background-color:#f0f2f6;padding:5px;border-radius:5px;margin-bottom:20px">
    <h2 style="color:black;text-align:center;font-size:28px;">Data Analytics of Consumption:</h2>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    
    def get_file_path(file_name):   
        folder_path = "C:\\Users\\25021648\\Desktop\\last smps"
        file_path = os.path.join(folder_path, file_name)
        return file_path
    
    # Streamlit App
    st.subheader('Consumed Spare Parts List:')

    # Read CSV file
    csv_file_path = get_file_path('Consumed_Spare_Parts_List.csv')
    try:
        consumed_df = pd.read_csv(csv_file_path)

        # Convert 'Date' column to datetime format
        consumed_df['Date'] = pd.to_datetime(consumed_df['Date'])

        # Display DataFrame initially
        st.write("Consumed Spare Parts List:")
        st.dataframe(consumed_df)

        months = [calendar.month_name[i] for i in range(1, 13)]
        months.insert(0, "Null")

        # Filter by selecting a specific month
        selected_month = st.sidebar.selectbox('Select Month to download Particular Months Consumed Data:', months)

        # Filtered DataFrame based on selected month
        if selected_month == "Null":
            filtered_df = pd.DataFrame()  # Empty DataFrame
        else:
            filtered_df = consumed_df[consumed_df['Date'].dt.month_name() == selected_month]

        # Display filtered DataFrame
        if selected_month == "Null":
            st.write("No month selected.")
        else:
            st.write(f"Filtered Data for {selected_month}:")
            st.dataframe(filtered_df)

        # Calculate revenue
        consumed_df['Revenue'] = consumed_df['Moving Average Price'] * consumed_df['Quantity']

        # Sidebar options for filtering data
        st.sidebar.header("Please Filter Here:")
        selected_month = st.sidebar.selectbox("Select Month:", [''] + list(calendar.month_abbr)[1:])
        selected_year = st.sidebar.selectbox("Select Year:", [''] + sorted(consumed_df['Date'].dt.year.unique()))
        selected_quarter = st.sidebar.selectbox("Select Quarter:", [''] + ["Q1", "Q2", "Q3", "Q4"])

        # Filter data based on user selection
        filtered_df = consumed_df
        if selected_year:
            filtered_df = filtered_df[filtered_df['Date'].dt.year == selected_year]

        if selected_month:
            filtered_df = filtered_df[filtered_df['Date'].dt.month == list(calendar.month_abbr).index(selected_month)]

        if selected_quarter:
            if selected_quarter == "Q1":
                filtered_df = filtered_df[(filtered_df['Date'].dt.month >= 1) & (filtered_df['Date'].dt.month <= 3)]
            elif selected_quarter == "Q2":
                filtered_df = filtered_df[(filtered_df['Date'].dt.month >= 4) & (filtered_df['Date'].dt.month <= 6)]
            elif selected_quarter == "Q3":
                filtered_df = filtered_df[(filtered_df['Date'].dt.month >= 7) & (filtered_df['Date'].dt.month <= 9)]
            elif selected_quarter == "Q4":
                filtered_df = filtered_df[(filtered_df['Date'].dt.month >= 10) & (filtered_df['Date'].dt.month <= 12)]

        # Plot the filtered data
        st.subheader("Bar Chart and Line Chart Combination:")
        if not filtered_df.empty:
            # Calculate weekly revenue
            weekly_revenue = filtered_df.groupby(pd.Grouper(key='Date', freq='W')).sum()['Revenue'].reset_index()

            # Add a new column for the week number
            weekly_revenue['Week'] = 'Week' + (weekly_revenue.index + 1).astype(str)

            # Convert values to lakh
            weekly_revenue['Revenue'] /= 100000

            # Create the figure
            fig = px.bar(weekly_revenue, x='Week', y='Revenue', title='Weekly Revenue(Bar Chart)', template='plotly_white')
            fig.add_scatter(x=weekly_revenue['Week'], y=weekly_revenue['Revenue'], mode='lines', name='Weekly Revenue(Line Chart)', line=dict(color='green'))
            fig.update_layout(width=900, height=550)  # Set width and height
            fig.update_xaxes(title_text='Week')
            fig.update_yaxes(title_text='Revenue (Lakh)')
            # Add value labels on top of the bars
            for i, val in enumerate(weekly_revenue['Revenue']):
                fig.add_annotation(x=weekly_revenue['Week'][i], y=val, text=f"{val:.2f} L", showarrow=False)
            st.plotly_chart(fig)

            # Prepare summary table
            summary_table = weekly_revenue[['Week', 'Revenue']]
            summary_table['Revenue'] = summary_table['Revenue'].map(lambda x: f"{x:.2f} L" if not pd.isnull(x) else None)
            # Calculate total revenue
            total_revenue = weekly_revenue['Revenue'].sum()

            # Display summary table
            st.write("Summary Table:")
            st.dataframe(summary_table.T)  # Transpose the DataFrame to display horizontally

            # Display total revenue
            st.write(f"Total Revenue: {total_revenue:.2f} Lakh")

            # Plot the filtered data - Fourth Graph (Weekly Analysis)
        st.subheader("Consumption Reason Analysis:")
        if not filtered_df.empty:
            # Calculate price if 'Moving Average Price' and 'Quantity' columns exist
            if 'Moving Average Price' in filtered_df.columns and 'Quantity' in filtered_df.columns:
                filtered_df['Price'] = filtered_df['Moving Average Price'] * filtered_df['Quantity']
            else:
                st.warning("Unable to calculate price. Required columns 'Moving Average Price' and 'Quantity' are missing.")

            # Group by week and Consumption Reason, and calculate the sum
            weekly_consumption_reason = filtered_df.groupby([pd.Grouper(key='Date', freq='W'), 'Consumption Reason']).sum()['Price'].unstack(fill_value=0).reset_index()

            # Resample to ensure all weeks are included
            all_weeks = pd.date_range(start=weekly_consumption_reason['Date'].min(), end=weekly_consumption_reason['Date'].max(), freq='W')
            weekly_consumption_reason = weekly_consumption_reason.set_index('Date').reindex(all_weeks).reset_index()

            # Fill missing values with zeros
            weekly_consumption_reason = weekly_consumption_reason.fillna(0) 

            # Add a new column for the week number
            weekly_consumption_reason['Week'] = 'Week' + (weekly_consumption_reason.index + 1).astype(str)

            # Convert values to lakh
            weekly_consumption_reason[['PM', 'BD']] /= 100000

            # Create the figure
            fig = px.bar(weekly_consumption_reason, x='Week', y=['PM', 'BD'], title='Weekly Consumption Reason Stacked Bar Chart:', 
                         template='plotly_white', barmode='stack', labels={'value': 'Price', 'variable': 'Consumption Reason'},
                         color_discrete_sequence=['#FFD700', '#FFA07A'])  # Set custom colors for PM and BD

            fig.update_xaxes(title_text='Week')
            fig.update_yaxes(title_text='Price (Lakh)')

            # Add annotations for revenue value
            # Add annotations for revenue value
            for i, row in weekly_consumption_reason.iterrows():
                pm_price = row['PM']
                bd_price = row['BD']
    
    # Calculate the middle of the bar range
                bar_middle = (pm_price + bd_price) / 2
    
    # Convert to lakh if price is greater than zero
                pm_price_display = f"{pm_price:.2f} L" if pm_price > 0 else None
                bd_price_display = f"{bd_price:.2f} L" if bd_price > 0 else None
    
    # Add annotations only when the value is greater than zero
                if pm_price > 0:
                    fig.add_annotation(x=row['Week'], y=bar_middle, text=pm_price_display, font=dict(color='black'), showarrow=False)
                if bd_price > 0:
                    fig.add_annotation(x=row['Week'], y=pm_price + bd_price, text=bd_price_display, font=dict(color='white'), showarrow=False)

            st.plotly_chart(fig)

            # Prepare summary table
            summary_table = weekly_consumption_reason[['Week', 'PM', 'BD']].copy()
            summary_table.loc['Total'] = summary_table[['PM', 'BD']].sum()

            # Format values to have only three digits after the decimal point and add 'L' symbol
            summary_table['PM'] = summary_table['PM'].map(lambda x: f"{x:.3f} L" if x > 0 else None)
            summary_table['BD'] = summary_table['BD'].map(lambda x: f"{x:.3f} L" if x > 0 else None)

            # Display summary table
            st.write("Summary Table:")
            st.dataframe(summary_table.T)
        else:
            st.write("No data available for the selected filters.")

        # Group by month and Consumption Reason for monthly analysis
        filtered_df['Month'] = filtered_df['Date'].dt.month_name()
        monthly_consumption_reason = filtered_df.groupby(['Month', 'Consumption Reason'])['Revenue'].sum().unstack(fill_value=0).reset_index()

        # Order the months
        ordered_months = list(calendar.month_name)
        monthly_consumption_reason['Month'] = pd.Categorical(monthly_consumption_reason['Month'], categories=ordered_months, ordered=True)
        monthly_consumption_reason = monthly_consumption_reason.sort_values('Month')

        # Convert values to lakh
        monthly_consumption_reason.iloc[:, 1:] /= 100000

        # Create monthly analysis plot
        fig_monthly = px.bar(monthly_consumption_reason, x='Month', y=['BD', 'PM'], title='Monthly Consumption Reason Bar Chart:', 
                     template='plotly_white', barmode='stack', labels={'value': 'Price (Lakh)', 'variable': 'Consumption Reason'},
                     color_discrete_sequence=['#FFA07A', '#FFD700'])

        fig_monthly.update_xaxes(title_text='Month')
        fig_monthly.update_yaxes(title_text='Price (Lakh)')

        # Add value labels on top of the bars
        for i, trace in enumerate(fig_monthly.data):
            for j, y in enumerate(trace.y):
                fig_monthly.add_annotation(x=trace.x[j], y=y, text=f"{y:.2f}L", showarrow=False, font=dict(color='black'))

        st.plotly_chart(fig_monthly)

        # Display summary table
        st.write("Summary of Monthly Consumption Reason in Lakhs:")
        monthly_consumption_reason['Total'] = monthly_consumption_reason[['PM', 'BD']].sum(axis=1)
        st.dataframe(monthly_consumption_reason.set_index('Month').T)

        # Calculate total for all months
        total = monthly_consumption_reason['Total'].sum()
        st.write(f"Total for all months: {total:.2f} Lakh")

        # 4. Plot the filtered data - Second Graph (Weekly Consumption by Category)
        st.subheader("Weekly Consumption by Category Grouped Bar Graph:")   
        if not filtered_df.empty:
            if 'Categorized' in filtered_df.columns and 'Price' in filtered_df.columns:
                # Extract week number from date
                filtered_df['Week'] = filtered_df['Date'].dt.isocalendar().week

                # Group by week and category, then calculate the sum of prices
                weekly_category_consumption = filtered_df.groupby(['Week', 'Categorized'])['Price'].sum().reset_index()

                # Convert price to lakh
                weekly_category_consumption['Price'] /= 100000

                # Create the figure
                fig2 = px.bar(weekly_category_consumption, x='Week', y='Price', color='Categorized', barmode='group',
                              title='Weekly Consumption by Category (in Lakh)', template='plotly_white')

                # Update x and y-axis labels
                fig2.update_xaxes(title_text='Week')
                fig2.update_yaxes(title_text='Price (Lakh)')

                # Add annotations for the exact value on each bar
                for i in fig2.data:
                    for j, value in enumerate(i.y):
                        fig2.add_annotation(x=i.x[j], y=value, text=f"{value:.2f} L" if value > 0 else None, showarrow=False)

                st.plotly_chart(fig2)

                # Transpose the DataFrame to make it horizontal
                transposed_weekly_category_consumption = weekly_category_consumption.pivot(index='Categorized', columns='Week', values='Price')

                # Add total column for each category
                transposed_weekly_category_consumption['Total'] = transposed_weekly_category_consumption.sum(axis=1)

                # Format values in lakh with two decimal places
                transposed_weekly_category_consumption = transposed_weekly_category_consumption.applymap(lambda x: f"{x:.3f} L" if x > 0 else None)

                # Display horizontal table of the filtered data used for the second graph
                st.write("Summary of Weekly Consumption by Category:")
                st.dataframe(transposed_weekly_category_consumption)

            else:
                st.warning("Unable to plot weekly consumption by category. Required columns or 'Categorized' column is missing.")
        else:
            st.write("No data available for the selected filters.")

        # Calculate the consumption of each category
        category_consumption = filtered_df['Categorized'].value_counts(normalize=True) * 100

        # 5. Plot the pie chart
        st.subheader("Monthly Consumption by Category:")
        if not category_consumption.empty:
            fig3 = px.pie(values=category_consumption, names=category_consumption.index,
                          title='Monthly Consumption by Category', template='plotly_white')
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig3)

            # Convert the series to DataFrame for horizontal display
            category_df = category_consumption.to_frame().transpose()

            # Display horizontal table
            st.write("Summary of Consumption by Category (Percentage):")
            st.dataframe(category_df)
            
        else:
            st.write("No data available for the selected filters.")

    except FileNotFoundError:
        st.write("No consumed spare parts yet.")

app() 
