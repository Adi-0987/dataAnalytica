from math import dist
from re import S
import plotly.express as px
import streamlit as st
import pandas as pd
import os
import base64
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="SCAN AND SHARE - ABDM DASHBOARD", page_icon=":bar_chart", layout="wide")

st.title(":bar_chart: SCAN AND SHARE - ABDM DASHBOARD")
st.markdown('<style>div.block-container{padding-top: 2rem} </style>', unsafe_allow_html=True)

# Read data from Excel
df = pd.read_excel(os.path.join("assests", "Facility_Token_Generation_Trend.xlsx"))

st.sidebar.header("Choose your filter: ")
# Create for Region
State = st.sidebar.multiselect("Pick your State", df["State Name"].unique())
if not State:
    df2 = df.copy()
else:
    df2 = df[df["State Name"].isin(State)]

# Create for State
Dist = st.sidebar.multiselect("Pick the District", df2["District Name"].unique())
if not Dist:
    df3 = df2.copy()
else:
    df3 = df2[df2["District Name"].isin(Dist)]

# Create for City
fasName = st.sidebar.multiselect("Pick the Facility",df3["Facility Name"].unique())
if not State and not Dist and not fasName:
    filtered_df = df
elif not State and not Dist:
    filtered_df = df[df["Facility Name"].isin(fasName)]
elif not Dist and not fasName:
    filtered_df = df[df["State Name"].isin(State)]
elif State and fasName:
    filtered_df = df3[df["State Name"].isin(State) & df3["Facility Name"].isin(fasName)]
elif Dist and fasName:
    filtered_df = df3[df["District Name"].isin(Dist) & df3["Facility Name"].isin(fasName)]
elif Dist and State:
    filtered_df = df3[df["District Name"].isin(Dist) & df3["State Name"].isin(State)]
elif fasName:
    filtered_df = df3[df3["Facility Name"].isin(fasName)]
else:
    filtered_df = df3[df3["District Name"].isin(Dist) & df3["State Name"].isin(Dist) & df3["Facility Name"].isin(fasName)]

# Calculate the required metrics
num_states = filtered_df['State Name'].nunique()
num_districts = filtered_df['District Name'].nunique()
num_facilities = filtered_df['Facility Name'].nunique()
num_tokens_generated = filtered_df['Token Count'].sum()
num_partners = filtered_df['Partner Name'].nunique()
# Display the cards horizontally with borders
col1, col2, col3, col4, col5 = st.columns(5)

# Define a CSS style for a bordered container
border_style = """
    border: 2px solid #00768d;
    padding: 15px;
    border-radius: 10px;
    background-color: #002435;
    text-align: center;
"""

# Card 1: No. of States
col1.markdown(f'<div style="{border_style}"> <h5>No. of State(s)</h5> <h3>{num_states}</h3> </div>', unsafe_allow_html=True)

# Card 2: No. of Districts
col2.markdown(f'<div style="{border_style}"> <h5>No. of Districts</h5> <h3>{num_districts}</h3> </div>', unsafe_allow_html=True)

# Card 3: No. of Facilities
col3.markdown(f'<div style="{border_style}"> <h5>No. of Facilities</h5> <h3>{num_facilities}</h3> </div>', unsafe_allow_html=True)

# Card 4: No. of Tokens Generated
col4.markdown(f'<div style="{border_style}"> <h5>No. of Tokens</h5> <h3>{num_tokens_generated}</h3> </div>', unsafe_allow_html=True)
# # Card 5: No. of Tokens Generated
col5.markdown(f'<div style="{border_style}"> <h5>No. of Partners</h5> <h3>{num_partners}</h3> </div>', unsafe_allow_html=True)

# Convert "Date" to datetime format
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

# Convert "Date" to month names
filtered_df['Month'] = filtered_df['Date'].dt.strftime('%B')

# Group by month and state, summing the Token Count
grouped_df = filtered_df.groupby(['Month', 'State Name'])['Token Count'].sum().reset_index()

# Omit November and December
grouped_df = grouped_df[grouped_df['Month'].isin(['January','February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October'])]

st.subheader(':date: Month Wise State, District and Facility Level Analysis')
# Line chart with custom ordering of months
charCol1, charCol2 = st.columns(2)
fig = px.bar(
    grouped_df, 
    x="Month", 
    y="Token Count", 
    color="State Name", 
    category_orders={"Month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
    width=580,
    barmode='group'
)
fig.update_traces(textposition='inside', showlegend=False)
charCol1.plotly_chart(fig)

# Download button for visible chart data
csv_data = filtered_df.to_csv(index=False)
b64 = base64.b64encode(csv_data.encode()).decode()
download_link = f'<a href="data:file/csv;base64,{b64}" download="visible_chart_data.csv">Download Visible Chart Data</a>'
st.markdown(download_link, unsafe_allow_html=True)

sunBurst_fig=px.sunburst(filtered_df, path=['State Name', 'District Name'], values='Token Count', width=500)
sunBurst_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
charCol2.plotly_chart(sunBurst_fig)
st.subheader(':computer: Partner Wise State, District and Facility Level Analysis')
treeMap=px.treemap(
    filtered_df, 
    path=['Partner Name', 'State Name', 'District Name', 'Facility Name'],
    values='Token Count',
    width=980,
    height=500,
    labels='Token Count'
)
st.plotly_chart(treeMap)
partnerGroup_df = filtered_df.groupby('Partner Name')['Token Count'].sum().reset_index()
# Sort the DataFrame by 'Token Count' in descending order
partnerGroup_df_sorted = partnerGroup_df.sort_values(by='Token Count', ascending=True)

col_1, col_2 = st.columns(2)
fig_bar_chart = px.bar(
    partnerGroup_df_sorted,
    x='Token Count',
    y='Partner Name',
    orientation='h',  # 'h' for horizontal bar chart
    labels={'Token Count': 'Sum of Token Count', 'State Name': 'State'},
    text='Token Count',  # Add labels to the bars
    width=580,
)
col_1.plotly_chart(fig_bar_chart)

# Pie chart in col_2
fig_pie_chart = px.pie(
    partnerGroup_df_sorted,
    names='Partner Name',
    values='Token Count',
    width=500,
)
fig_pie_chart.update_traces(textposition='inside', showlegend=False, )
fig_pie_chart.update_layout(paper_bgcolor='rgba(0,0,0,0)')
# Display the pie chart in col_2
col_2.plotly_chart(fig_pie_chart)
st.title("Thank you for your time!")
