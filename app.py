import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data

st.set_page_config(page_title="Real Estate Dashboard", layout="wide")

st.title("Real Estate Transaction Dashboard")

@st.cache_data
def get_data():
    # Helper to load data
    # Assuming the file is in the parent directory or known path
    # In this environment, we know the path is d:/AI Projects/recent_sales.txt
    file_path = "recent_sales.txt" 
    return load_data(file_path)

df = get_data()

if df is None:
    st.error("Failed to load data. Please check if 'recent_sales.txt' exists.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Drill Down Filters")

# Filter by District
districts = ["All"] + sorted(df['District'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("Select District", districts)

if selected_district != "All":
    df = df[df['District'] == selected_district]

# Filter by Community
communities = ["All"] + sorted(df['Community'].dropna().unique().tolist())
selected_community = st.sidebar.selectbox("Select Community", communities)

if selected_community != "All":
    df = df[df['Community'] == selected_community]

# Filter by Project
projects = ["All"] + sorted(df['Project'].dropna().unique().tolist())
selected_project = st.sidebar.selectbox("Select Project", projects)

if selected_project != "All":
    df = df[df['Project'] == selected_project]
    
# Filter by Registration (Date Range? Or Type?)
# The prompt says "drill dowm ... by ... registration". Registration seems to be a date column.
# Maybe extract Year/Month? Or just use Year filter?
# Let's add Year filter
if 'Registration' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Registration']):
    df['Year'] = df['Registration'].dt.year
    years = ["All"] + sorted(df['Year'].dropna().unique().astype(int).tolist())
    selected_year = st.sidebar.selectbox("Select Year", years)
    
    if selected_year != "All":
        df = df[df['Year'] == selected_year]
else:
    st.warning("Registration date parsing issue, time filters disabled.")

# Main Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Transactions", len(df))
with col2:
    avg_price = df['Price (AED)'].mean()
    st.metric("Average Price", f"AED {avg_price:,.0f}" if not pd.isna(avg_price) else "-")
with col3:
    avg_rate = df['Rate (AED/sqm)'].mean()
    st.metric("Average Rate (AED/sqm)", f"{avg_rate:,.2f}" if not pd.isna(avg_rate) else "-")


# 1. Line chart of price change over the years
st.subheader("Price Trends Over Years")
if 'Registration' in df.columns and not df['Registration'].isna().all():
    # Aggregate by Year or Month
    # Let's do Monthly trend if filtered by year, else Yearly trend
    
    if 'Year' in locals() and selected_year != "All":
         # Monthly
         df['MonthYear'] = df['Registration'].dt.to_period('M').astype(str)
         trend_df = df.groupby('MonthYear')[['Price (AED)', 'Rate (AED/sqm)']].mean().reset_index()
         fig_trend = px.line(trend_df, x='MonthYear', y='Price (AED)', title='Average Price Trend (Monthly)')
    else:
         # Yearly
         if 'Year' not in df.columns:
             df['Year'] = df['Registration'].dt.year
         trend_df = df.groupby('Year')[['Price (AED)', 'Rate (AED/sqm)']].mean().reset_index()
         fig_trend = px.line(trend_df, x='Year', y='Price (AED)', title='Average Price Trend (Yearly)')
         
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No Date information available for trends.")


# 2. Average price per area (by District, Community)
st.subheader("Average Price per Area")

# We can show Top 10 Districts/Communities by Price
col_area1, col_area2 = st.columns(2)

with col_area1:
    # By District
    avg_price_district = df.groupby('District')['Price (AED)'].mean().reset_index().sort_values('Price (AED)', ascending=False).head(10)
    fig_dist = px.bar(avg_price_district, x='District', y='Price (AED)', title='Top 10 Districts by Avg Price')
    st.plotly_chart(fig_dist, use_container_width= True)

with col_area2:
    # By Community
    avg_price_comm = df.groupby('Community')['Price (AED)'].mean().reset_index().sort_values('Price (AED)', ascending=False).head(10)
    fig_comm = px.bar(avg_price_comm, x='Community', y='Price (AED)', title='Top 10 Communities by Avg Price')
    st.plotly_chart(fig_comm, use_container_width=True)


# 3. Drill down histograms/pie charts of average rate
st.subheader("Distribution and Composition")

# Tabs for different drill downs
tab1, tab2, tab3, tab4 = st.tabs(["District", "Community", "Project", "Registration / Sale Type"])

with tab1:
    st.markdown("#### Transactions by District")
    # Pie chart of count
    dist_count = df['District'].value_counts().head(10).reset_index()
    dist_count.columns = ['District', 'Count']
    fig_p1 = px.pie(dist_count, names='District', values='Count', title='Top 10 Districts (Volume)')
    st.plotly_chart(fig_p1)
    
    st.markdown("#### Average Rate Distribution")
    fig_h1 = px.histogram(df, x='Rate (AED/sqm)', color='District', nbins=50, title="Rate Distribution by District")
    st.plotly_chart(fig_h1)

with tab2:
    st.markdown("#### Transactions by Community")
    comm_count = df['Community'].value_counts().head(10).reset_index()
    comm_count.columns = ['Community', 'Count']
    fig_p2 = px.pie(comm_count, names='Community', values='Count', title='Top 10 Communities (Volume)')
    st.plotly_chart(fig_p2)

with tab3:
    st.markdown("#### Transactions by Project")
    proj_count = df['Project'].value_counts().head(10).reset_index()
    proj_count.columns = ['Project', 'Count']
    fig_p3 = px.pie(proj_count, names='Project', values='Count', title='Top 10 Projects (Volume)')
    st.plotly_chart(fig_p3)

with tab4:
    # "Registration" in prompt might refer to "Registration" type? But data only has "Registration" date.
    # The prompt listed "Sale Type" in the columns. Maybe they meant Sale Type?
    # Or maybe "Registration" column is NOT date?
    # View file header: "Registration". Sample values: "24/04/2023". It is a date.
    # The prompt said "average rate by ... registration". Maybe they mean by Year of registration?
    # Or maybe Sale Type?
    # Let's show Sale Type here as it is more categorical.
    
    st.markdown("#### Transactions by Sale Type")
    if 'Sale Type' in df.columns:
        sale_count = df['Sale Type'].value_counts().reset_index()
        sale_count.columns = ['Sale Type', 'Count']
        fig_p4 = px.pie(sale_count, names='Sale Type', values='Count', title='Sale Type Distribution')
        st.plotly_chart(fig_p4)
        
        st.markdown("#### Average Rate by Sale Type")
        avg_rate_sale = df.groupby('Sale Type')['Rate (AED/sqm)'].mean().reset_index()
        fig_b4 = px.bar(avg_rate_sale, x='Sale Type', y='Rate (AED/sqm)', title='Average Rate by Sale Type')
        st.plotly_chart(fig_b4)
