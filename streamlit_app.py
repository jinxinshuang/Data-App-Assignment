import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

import numpy as np

st.title("Xinshuang Jin, Data App Assignment, on Oct 7th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")
st.write("### (1) add a drop down for Category (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)")
st.write("### (2) add a multi-select for Sub_Category *in the selected Category (1)* (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)")
st.write("### (3) show a line chart of sales for the selected items in (2)")
st.write("### (4) show three metrics (https://docs.streamlit.io/library/api-reference/data/st.metric) for the selected items in (2): total sales, total profit, and overall profit margin (%)")
st.write("### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)")

########################################

#################### (1) add a drop down for Category (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)''

# Select unique category from dataframe
unique_category= df['Category'].unique().tolist()
option=st.selectbox("Select a Category",unique_category)


#################### (2) add a multi-select for Sub_Category in the selected Category (1) (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)


#Select unique Sub_Category based on selected category
#Example: selected_column = df.loc[df['Condition_Column'] == 'A', 'Target_Column']

unique_subcategory=df.loc[df["Category"]==option, "Sub_Category"].unique().tolist()

options = st.multiselect(
    "Select Sub_Catogeries",unique_subcategory)


#################### (3) show a line chart of sales for the selected items in (2)

#Select rows from dataframe df where Sub_Category is from user's selections (options)
unique_sub_categories = df.loc[df["Sub_Category"].isin(options),:]

# Group by ["Order_Date"], ["Sub_Category"]
unique_sub_categories_sorted=unique_sub_categories.groupby([unique_sub_categories.index, "Sub_Category"])["Sales"].sum().reset_index()

# Add a header
st.subheader("Sub_Category Sales by Order_Year_Month")

# Group the Order_Date by month (freq='M'), The order date will be the last day of each month
monthly_sales = unique_sub_categories_sorted.groupby([pd.Grouper(key='Order_Date', freq='M'), 'Sub_Category']).sum().reset_index()



##################### (3)  continued: 
##################### some sub_category does NOT have sales in certain monnths)
##################### replace missing values (some sub_category does NOT have sales in certain monnths) with 0

min=monthly_sales["Order_Date"].min()
max= monthly_sales["Order_Date"].max()

# if max is 2017-12, the date_range will end on 2017-11, need to use 2017-12-31 to include all the dates 2017-12
original_end_date = pd.to_datetime(max)
# Add Last Day of Month: The pd.offsets.MonthEnd(0) is added to each date, effectively changing it to the last day of that month.
last_Day_of_month= original_end_date + pd.offsets.MonthEnd(0)

# Set a data_range with all month included 
all_months = pd.date_range(start=min, end=last_Day_of_month, freq='M')

# Use numpy to repeat each element
# each months is supposed to be repeated by number of options 
duplicated_months = np.repeat(all_months, len(options))


# Create a new DataFrame with all months and selected Sub_Category from (options)
# options * len(all_months): options repeat len(all_months) times
all_months_df = pd.DataFrame({
    'Order_Date': duplicated_months,
    'Sub_Category': options * len(all_months),
})

# Merge the original DataFrame "monthly_sales" with the complete month DataFrame "all_months_df"
# merged_df = df1.merge(df2, how='join_type', on='key_column')
    
merged_df= all_months_df.merge(monthly_sales, on=['Order_Date', 'Sub_Category'], how='left')

# Fill missing sales with 0
merged_df['Sales'] = merged_df['Sales'].fillna(0)

# Add a column of Order_Month 
merged_df['Order_Month'] = merged_df['Order_Date'].dt.to_period('M').astype(str)


st.line_chart(merged_df, 
              x="Order_Month",
              y="Sales", 
              x_label="Order_by_Year_Month", 
              y_label="Sales", 
              color="Sub_Category")


#####################  (4) show three metrics (https://docs.streamlit.io/library/api-reference/data/st.metric) for the selected items in (2): total sales, total profit, and overall profit margin (%)
##################### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)

st.header("Metrics (displayed with two decimal places)")

subcategory_sales_profit= unique_sub_categories.groupby("Sub_Category", as_index=False)[["Sales", "Profit"]].sum()

df["Profit"].sum()
df["Sales"].sum()
overall_avg_profit_margin= df["Profit"].sum() / df["Sales"].sum() * 100


for i in range(len(options)):
    subcategory=subcategory_sales_profit["Sub_Category"][i]
    
    sales=subcategory_sales_profit["Sales"][i]
    # Only displays two decimal places
    formatted_sale="${:.2f}".format(sales)
    
    profit=subcategory_sales_profit["Profit"][i]
    formatted_profit="${:.2f}".format(profit)
    
    overall_profit_margin = profit / sales *100
    formatted_margin = "{:.2f}%".format(overall_profit_margin)
    
    delta = overall_profit_margin - overall_avg_profit_margin
    formatted_delta="{:.2f}%".format(delta)
    
    st.subheader(subcategory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", formatted_sale)
    col2.metric("Profit", formatted_profit)
    col3.metric("Overall Profit Margin", formatted_margin, formatted_delta)



