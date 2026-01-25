import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data

st.set_page_config(page_title="Real Estate Dashboard", layout="wide")

st.title("Real Estate Transaction Dashboard")

@st.cache_data
def get_data():
    file_path = "recent_sales.txt" 
    return load_data(file_path)

df, error = get_data()

if df is None:
    st.error(f"Failed to load data. {error}")
    st.info("Check if 'recent_sales.txt' is in your GitHub repository and its size in GitHub. If it's missing, you may need to commit it again.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Drill Down Filters")

# Initialize filtered_df
filtered_df = df.copy()

# 1. Asset Type
asset_types = ["All"] + sorted(filtered_df['Asset Type'].dropna().unique().tolist())
selected_asset_type = st.sidebar.selectbox("Asset Type", asset_types)

if selected_asset_type != "All":
    filtered_df = filtered_df[filtered_df['Asset Type'] == selected_asset_type]

# 2. Property Type
# Filter options based on previous selection to make it dynamic? Or keep static list? 
# Dynamic is better UX.
property_types = ["All"] + sorted(filtered_df['Property Type'].dropna().unique().tolist())
selected_property_type = st.sidebar.selectbox("Property Type", property_types)

if selected_property_type != "All":
    filtered_df = filtered_df[filtered_df['Property Type'] == selected_property_type]

# 3. Sale Type (Type)
sale_types = ["All"] + sorted(filtered_df['Sale Type'].dropna().unique().tolist())
selected_sale_type = st.sidebar.selectbox("Sale Type", sale_types)

if selected_sale_type != "All":
    filtered_df = filtered_df[filtered_df['Sale Type'] == selected_sale_type]

# 4. Sequence
sequences = ["All"] + sorted(filtered_df['Sequence'].dropna().unique().tolist())
selected_sequence = st.sidebar.selectbox("Sequence", sequences)

if selected_sequence != "All":
    filtered_df = filtered_df[filtered_df['Sequence'] == selected_sequence]

# Filter by District
districts = ["All"] + sorted(filtered_df['District'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("District", districts)

if selected_district != "All":
    filtered_df = filtered_df[filtered_df['District'] == selected_district]

# Filter by Community
communities = ["All"] + sorted(filtered_df['Community'].dropna().unique().tolist())
selected_community = st.sidebar.selectbox("Community", communities)

if selected_community != "All":
    filtered_df = filtered_df[filtered_df['Community'] == selected_community]

# Filter by Project
projects = ["All"] + sorted(filtered_df['Project'].dropna().unique().tolist())
selected_project = st.sidebar.selectbox("Project", projects)

if selected_project != "All":
    filtered_df = filtered_df[filtered_df['Project'] == selected_project]
    
# Filter by Registration (Year)
if 'Registration' in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['Registration']):
    filtered_df['Year'] = filtered_df['Registration'].dt.year
    filtered_df['Quarter'] = filtered_df['Registration'].dt.to_period('Q').astype(str)
    
    years = ["All"] + sorted(filtered_df['Year'].dropna().unique().astype(int).tolist())
    selected_year = st.sidebar.selectbox("Select Year", years)
    
    if selected_year != "All":
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
else:
    st.warning("Registration date parsing issue, time filters disabled.")

# Main Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Transactions", len(filtered_df))
with col2:
    avg_price = filtered_df['Price (AED)'].mean()
    st.metric("Average Price", f"AED {avg_price:,.0f}" if not pd.isna(avg_price) else "-")
with col3:
    avg_rate = filtered_df['Rate (AED/sqm)'].mean()
    st.metric("Average Rate (AED/sqm)", f"{avg_rate:,.2f}" if not pd.isna(avg_rate) else "-")

# --- Time Series Section ---
st.subheader("Price & Rate Trends")

interval = st.radio("Select Interval", ["Yearly", "Quarterly", "Monthly"], horizontal=True)

if 'Registration' in filtered_df.columns and not filtered_df['Registration'].isna().all():
    if interval == "Yearly":
        group_col = 'Year'
    elif interval == "Quarterly":
        group_col = 'Quarter'
    else:
        filtered_df['MonthYear'] = filtered_df['Registration'].dt.to_period('M').astype(str)
        group_col = 'MonthYear'
        
    trend_df = filtered_df.groupby(group_col)[['Price (AED)', 'Rate (AED/sqm)']].mean().reset_index()
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig_price = px.line(trend_df, x=group_col, y='Price (AED)', title=f'Average Price Trend ({interval})')
        st.plotly_chart(fig_price, use_container_width=True)
    with col_t2:
        fig_rate = px.line(trend_df, x=group_col, y='Rate (AED/sqm)', title=f'Average Rate Trend ({interval})')
        st.plotly_chart(fig_rate, use_container_width=True)
else:
    st.info("No Date information available for trends.")

# --- Area Analysis ---
st.subheader("Average Rate per Area")

col_area1, col_area2 = st.columns(2)

with col_area1:
    avg_rate_district = filtered_df.groupby('District')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
    fig_dist = px.bar(avg_rate_district, x='District', y='Rate (AED/sqm)', title='Top 10 Districts by Avg Rate')
    st.plotly_chart(fig_dist, use_container_width=True)

with col_area2:
    avg_rate_comm = filtered_df.groupby('Community')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
    fig_comm = px.bar(avg_rate_comm, x='Community', y='Rate (AED/sqm)', title='Top 10 Communities by Avg Rate')
    st.plotly_chart(fig_comm, use_container_width=True)

# --- Drill Down Section ---
st.subheader("Distribution and Composition (by Rate)")

tab1, tab2, tab3, tab4 = st.tabs(["District", "Community", "Project", "Registration / Sale Type"])

with tab1:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dist_rate = filtered_df.groupby('District')['Rate (AED/sqm)'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_p1 = px.pie(dist_rate, names='District', values='Rate (AED/sqm)', title='Top 10 Districts (Avg Rate Share)')
        st.plotly_chart(fig_p1)
    with col_d2:
        fig_h1 = px.histogram(filtered_df, x='Rate (AED/sqm)', color='District', nbins=50, title="Rate Distribution by District")
        st.plotly_chart(fig_h1)

with tab2:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        comm_rate = filtered_df.groupby('Community')['Rate (AED/sqm)'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_p2 = px.pie(comm_rate, names='Community', values='Rate (AED/sqm)', title='Top 10 Communities (Avg Rate Share)')
        st.plotly_chart(fig_p2)
    with col_c2:
        fig_h2 = px.histogram(filtered_df, x='Rate (AED/sqm)', color='Community', nbins=50, title="Rate Distribution by Community")
        st.plotly_chart(fig_h2)

with tab3:
    col_pr1, col_pr2 = st.columns(2)
    with col_pr1:
        proj_rate = filtered_df.groupby('Project')['Rate (AED/sqm)'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_p3 = px.pie(proj_rate, names='Project', values='Rate (AED/sqm)', title='Top 10 Projects (Avg Rate Share)')
        st.plotly_chart(fig_p3)
    with col_pr2:
        fig_h3 = px.histogram(filtered_df, x='Rate (AED/sqm)', color='Project', nbins=50, title="Rate Distribution by Project")
        st.plotly_chart(fig_h3)

with tab4:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if 'Sale Type' in filtered_df.columns:
            sale_rate = filtered_df.groupby('Sale Type')['Rate (AED/sqm)'].mean().reset_index()
            fig_p4 = px.pie(sale_rate, names='Sale Type', values='Rate (AED/sqm)', title='Sale Type by Avg Rate')
            st.plotly_chart(fig_p4)
    with col_s2:
        if 'Sale Type' in filtered_df.columns:
            fig_h4 = px.histogram(filtered_df, x='Rate (AED/sqm)', color='Sale Type', nbins=50, title="Rate Distribution by Sale Type")
            st.plotly_chart(fig_h4)
