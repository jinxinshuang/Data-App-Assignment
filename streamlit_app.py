import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

import numpy as np

st.title("Data App Assignment, on Oct 7th")

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
unique_category= df['Category'].unique()
option=st.selectbox("Select a Category", unique_category)



########### Select unique Sub_Category based on selected category
# selected_column = df.loc[df['Condition_Column'] == 'A', 'Target_Column']

unique_subcategory=df.loc[df["Category"]==option, "Sub_Category"].unique().tolist()

options = st.multiselect(
    "Select Sub_Catogeries",unique_subcategory,
)


####

unique_sub_categories = df.loc[df["Sub_Category"].isin(options),:]
unique_sub_categories_sorted=unique_sub_categories.groupby([unique_sub_categories.index, "Sub_Category"])["Sales"].sum().reset_index()

# Add a header
st.subheader("Sub_Category Sales by Year")
monthly_sales = unique_sub_categories_sorted.groupby([pd.Grouper(key='Order_Date', freq='M'), 'Sub_Category']).sum().reset_index()

st.dataframe(monthly_sales)

st.line_chart(monthly_sales, x="Order_Date",
y="Sales", color="Sub_Category")


#####################

# 2017-12 will end on 2017-11, need to use 2017-12-31 to include all the dates 2017-12
min=monthly_sales["Order_Date"].min()

# print(min)
# 2014-01-31 00:00:00

max= monthly_sales["Order_Date"].max()

# print(max)
# 2017-12-31 00:00:00

original_end_date = pd.to_datetime(max)
# Add Last Day of Month: The pd.offsets.MonthEnd(0) is added to each date, effectively changing it to the last day of that month.
last_Day_of_month= original_end_date + pd.offsets.MonthEnd(0)

# print(last_Day_of_month)
# 2017-12-31 00:00:00

all_months = pd.date_range(start=min, end=last_Day_of_month, freq='M')
# .to_period('M').astype(str)

# Use numpy to repeat each element
duplicated_months = np.repeat(all_months, len(options))

# Print the result
print(duplicated_months)

# Create a new DataFrame with all months and the unique Sub_Category
all_months_df = pd.DataFrame({
    'Order_Date': duplicated_months,
    'Sub_Category': options * len(all_months),
})

print(all_months_df)

# Merge the original DataFrame with the complete month DataFrame
# merged_df = df1.merge(df2, how='join_type', on='key_column')
    # df1: The first DataFrame.
    # df2: The second DataFrame.
    # how: The type of merge to be performed:
    # 'inner': Only include rows with keys present in both DataFrames (default).
    # 'outer': Include rows from both DataFrames, filling in missing values with NaN.
    # 'left': Include all rows from the left DataFrame and matching rows from the right DataFrame.
    
merged_df= all_months_df.merge(monthly_sales, on=['Order_Date', 'Sub_Category'], how='left')

# # Fill missing sales with 0
merged_df['Sales'] = merged_df['Sales'].fillna(0)

# Add a column of Order_Month 
#     Order_Date Sub_Category      Sales Order_Month
# 0   2014-01-31       Phones   2315.400     2014-01
merged_df['Order_Month'] = merged_df['Order_Date'].dt.to_period('M')

print(merged_df)

st.dataframe(merged_df)
st.line_chart(merged_df, x="Order_Month",
y="Sales", color="Sub_Category")

#############################

bookcases=df.loc[df["Sub_Category"]=="Bookcases"].reset_index()

bookcases_new=bookcases.groupby(["Order_Date", "Sub_Category"])["Sales"].sum().reset_index()
st.dataframe(bookcases_new)

####

subcategory_sales_profit= unique_sub_categories.groupby("Sub_Category", as_index=False)[["Sales", "Profit"]].sum()


# the overall average profit margin (all products across all categories):
# profit/sale * 100

df['Profit Margin'] = (df['Profit'] / df['Sales']) * 100
# Calculate the Overall Average Profit Margin
overall_avg_profit_margin = df['Profit Margin'].mean()

formatted_overall_avg_profit_margin="{:.2f}%".format(overall_avg_profit_margin)
# print(formatted_overall_avg_profit_margin)


for i in range(len(options)):
    subcategory=subcategory_sales_profit["Sub_Category"][i]
    
    sales=subcategory_sales_profit["Sales"][i]
    formatted_sale="${:.2f}".format(sales)
    
    profit=subcategory_sales_profit["Profit"][i]
    formatted_profit="${:.2f}".format(profit)
    
    overall_profit_margin = profit / sales *100
    formatted_margin = "{:.2f}%".format(overall_profit_margin)
    
    delta=overall_profit_margin-overall_avg_profit_margin
    formatted_delta="{:.2f}%".format(delta)
    
    st.subheader(subcategory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", formatted_sale)
    col2.metric("Profit", formatted_profit)
    col3.metric("Overall Profit Margin", formatted_margin,formatted_delta)


############ 



# ######## Try bookcases, Succeed!
# bookcases=df.loc[df["Sub_Category"]=="Bookcases"].reset_index()

# bookcases.groupby(["Order_Date", "Sub_Category"])["Sales"].sum().reset_index()


# bookcases_new= bookcases.reset_index()

# bookcases_new['Order_Date']=pd.to_datetime(bookcases_new['Order_Date'], format='%m/%d/%Y')

# # unique["Order_Month"]=unique['Order_Date'].dt.month

# # Create a new column with the year and month (if you want both)
# bookcases_new['Order_Month'] = bookcases_new['Order_Date'].dt.to_period('M')


# # Convert "Order_Year" to string (so that are no extra ticks on x axis)
# bookcases_new["Order_Month"]=bookcases_new["Order_Month"].astype(str)

# # Reset Index: Using .reset_index() converts the result back into a DataFrame instead of a Series.
# book_cases_finished=bookcases_new.groupby(["Order_Month", "Sub_Category"])["Sales"].sum().reset_index()

# min= bookcases_new["Order_Date"].min()
# print(min)

# max= bookcases_new["Order_Date"].max()
# print(max)

# # Create a complete range of months for the year 2014 to 2017

# # 2017-12 will end on 2017-11, need to use 2017-12-31 to include all the dates 2017-12

# original_end_date = pd.to_datetime(max)
# # Add Last Day of Month: The pd.offsets.MonthEnd(0) is added to each date, effectively changing it to the last day of that month.
# last_Day_of_month= original_end_date + pd.offsets.MonthEnd(0)

# # Timestamp('2017-12-31 00:00:00')


# all_months = pd.date_range(start=min, end=last_Day_of_month, freq='M').to_period('M').astype(str)




# # Create a new DataFrame with all months and the unique Sub_Category
# all_months_df = pd.DataFrame({
#     'Order_Month': all_months,
#     'Sub_Category': ['Bookcases'] * len(all_months)
# })


# # book_cases_finished

# # Merge the original DataFrame with the complete month DataFrame
# # merged_df = df1.merge(df2, how='join_type', on='key_column')
#     # df1: The first DataFrame.
#     # df2: The second DataFrame.
#     # how: The type of merge to be performed:
#     # 'inner': Only include rows with keys present in both DataFrames (default).
#     # 'outer': Include rows from both DataFrames, filling in missing values with NaN.
#     # 'left': Include all rows from the left DataFrame and matching rows from the right DataFrame.
    
# merged_df= all_months_df.merge(book_cases_finished, on=['Order_Month', 'Sub_Category'], how='left')


# # Fill missing sales with 0
# merged_df['Sales'] = merged_df['Sales'].fillna(0)
# st.dataframe(merged_df)
# st.line_chart(merged_df, x="Order_Month",
# y="Sales")


