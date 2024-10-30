import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from streamlit_gsheets import GSheetsConnection


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="ESD India Sales Dashboard", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
@st.cache_data
def get_data_from_excel():
    # df = pd.read_excel(
    #     io="forecasted_data.xlsx",
    #     engine="openpyxl",
    #     sheet_name="Sheet1",
    #     # skiprows=3,
    #     usecols="A:AD",
    #     nrows=539,
    # )

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)
                     
                    

# Fetch existing vendors data
    df = conn.read(worksheet="Forecasted_data", usecols=list(range(28)), ttl=5)
    df = df.dropna(how="all")
    # Add 'hour' column to dataframe
    # df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['Month'] = df['Timestamp'].dt.month

    return df

df = get_data_from_excel()

# print(df)
# st.dataframe(df)

st.title(":bar_chart: ESD India Sales Dashboard")
# st.markdown("##") #to insert a paragraph



# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
item_description = st.sidebar.multiselect(
    "Select the Item Description:",
    options=df["Item Description"].unique()
    # default=["electronic components"]
    # default=df["Item Description"].unique()
)
abc_category = st.sidebar.multiselect(
    "Select the ABC Category:",
    options=df["ABC Category"].unique()
    # default=df["Item Description"].unique()
)
location_sold = st.sidebar.multiselect(
    "Select the Location Sold:",
    options=df["Location Sold"].unique()
    # default=df["Item Description"].unique()
)

stock_status = st.sidebar.multiselect(
    "Select the Stock Status:",
    options=df["Stock Status"].unique()
    # default=df["Item Description"].unique()
)
spare_part_type = st.sidebar.multiselect(
    "Select the Spare Part Type:",
    options=df["Spare Part Type"].unique()
    # default=df["Item Description"].unique()
)

# df_selection = df.query(
#     "'Item Description' == @item_description & 'ABC Category' ==@abc_category & 'Location Sold' == @location_sold & 'Stock Status' == @stock_status & 'Spare Part Type' == @spare_part_type"
# )

# # Check if the dataframe is empty:
# if df_selection.empty:
#     st.warning("No data available based on the current filter settings!")
#     st.stop() # This will halt the app from further execution.


# Define the query string dynamically based on filter selections
query_string = []

if item_description:
    query_string.append("`Item Description` in @item_description")
if abc_category:
    query_string.append("`ABC Category` in @abc_category")
if location_sold:
    query_string.append("`Location Sold` in @location_sold")
if stock_status:
    query_string.append("`Stock Status` in @stock_status")
if spare_part_type:
    query_string.append("`Spare Part Type` in @spare_part_type")

# Join all the filters with ' & ' and apply query only if there are conditions
if query_string:
    df_selection = df.query(" & ".join(query_string))
else:
    df_selection = df  # No filter selected, so display the full dataframe

# if st.sidebar.button("Add New Vendor"):
#     st.query_params(page="entry_form")


# ---- MAINPAGE ----
# TOP KPI's
total_sales = int(df_selection["Total Sold Price"].sum())
average_level = round(df_selection["Stock Level After Sale"].mean(), 1)
# star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total Sold Price"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"Rs {total_sales:,}")
with middle_column:
    st.subheader("Average Stock Level After Sale:")
    st.subheader(f"{average_level}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"Rs {average_sale_by_transaction}")

st.markdown("""---""")

# Check if the dataframe is empty
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()
else:
    st.write(df_selection) 



# SALES BY PRODUCT LINE [BAR CHART]
sales_by_location_line = df_selection.groupby(by=["Location Sold"])[["Total Sold Price"]].sum().sort_values(by="Total Sold Price")
fig_location_sales = px.bar(
    sales_by_location_line,
    x="Total Sold Price",
    y=sales_by_location_line.index,
    orientation="h",
    title="<b>Sales by Location</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_location_line),
    template="plotly_white",
)
fig_location_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_month = df_selection.groupby(by=["Month"])[["Total Sold Price"]].sum()
fig_monthly_sales = px.bar(
    sales_by_month,
    x=sales_by_month.index,
    y="Total Sold Price",
    title="<b>Sales by month</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_month),
    template="plotly_white",
)
fig_monthly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_monthly_sales, use_container_width=True)
right_column.plotly_chart(fig_location_sales, use_container_width=True)




# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)