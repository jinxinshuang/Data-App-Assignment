import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

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

st.write("You selected:", option)

# option = st.selectbox(
#     "How would you like to be contacted?",
#     ("Email", "Home phone", "Mobile phone"),
# )

# st.write("You selected:", option)

# options = st.multiselect(
#     "What are your favorite colors",
#     ["Green", "Yellow", "Red", "Blue"],
#     ["Yellow", "Red"],
# )

# st.write("You selected:", options)

# unique_subcategory= df['Sub_Category'].unique()
# options = st.multiselect(
#     "Select Sub_Catogeries",unique_subcategory,
# )

# st.write("You selected:", options)

# ########## Select unique Sub_Category based on selected category
# selected_column = df.loc[df['Condition_Column'] == 'A', 'Target_Column']
unique_subcategory=df.loc[df["Category"]==option, "Sub_Category"].unique().tolist()

options = st.multiselect(
    "Select Sub_Catogeries",unique_subcategory,
)

st.write("You selected:", options)


####

unique_sub_categories = df.loc[df["Sub_Category"].isin(options),:]
unique_sub_categories_sorted=unique_sub_categories.groupby([unique_sub_categories.index, "Sub_Category"])["Sales"].sum().reset_index()

subcategory_sales_by_year= unique_sub_categories_sorted

subcategory_sales_by_year["Order_Year"]=subcategory_sales_by_year['Order_Date'].dt.year
subcategory_sales_by_year["Order_Year"]=subcategory_sales_by_year["Order_Year"].astype(str)
sales_by_year= subcategory_sales_by_year.groupby(["Order_Year", "Sub_Category"], as_index=False)["Sales"].sum()
# Add a header
st.subheader("Sub_Category Sales by Year")
st.line_chart(sales_by_year,x="Order_Year",
y="Sales", x_label="Year", y_label="Sales",color="Sub_Category")

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
    
    st.subheader(subcategory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", formatted_sale)
    col2.metric("Profit", formatted_profit)
    col3.metric("Overall Profit Margin", formatted_margin,delta)

