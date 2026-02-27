import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data

st.set_page_config(page_title="Real Estate Dashboard", layout="wide")

st.title("Abu Dhabi Real Estate Market Dashboard")
st.markdown("<p style='font-size: 18px;'>Developed by Lipei Zhang</p>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    file_path = "recent_sales.txt" 
    return load_data(file_path)

df, error = get_data()

if df is None:
    st.error(f"Failed to load data. {error}")
    st.info("Check if 'recent_sales.txt' is in your GitHub repository and its size in GitHub.")
    st.stop()

# --- Pre-processing for Tabs ---
if 'Registration' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Registration']):
    df['Year'] = df['Registration'].dt.year
    df['Quarter'] = df['Registration'].dt.to_period('Q').astype(str)

# Top level navigation
main_tab1, main_tab2 = st.tabs(["Real Estate Transaction Dashboard", "Real Estate Growth Indicators"])

# --- Sidebar Filters (Shared) ---
st.sidebar.header("Geography Filters")

# We want geography filters to apply to both tabs
districts = ["All"] + sorted(df['District'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("District", districts)

geo_filtered_df = df.copy()
if selected_district != "All":
    geo_filtered_df = geo_filtered_df[geo_filtered_df['District'] == selected_district]

communities = ["All"] + sorted(geo_filtered_df['Community'].dropna().unique().tolist())
selected_community = st.sidebar.selectbox("Community", communities)

if selected_community != "All":
    geo_filtered_df = geo_filtered_df[geo_filtered_df['Community'] == selected_community]

projects = ["All"] + sorted(geo_filtered_df['Project'].dropna().unique().tolist())
selected_project = st.sidebar.selectbox("Project", projects)

if selected_project != "All":
    geo_filtered_df = geo_filtered_df[geo_filtered_df['Project'] == selected_project]

# Registration Year Filter
if 'Year' in geo_filtered_df.columns:
    years = ["All"] + sorted(geo_filtered_df['Year'].dropna().unique().astype(int).tolist())
    selected_year = st.sidebar.selectbox("Select Year", years)
    if selected_year != "All":
        geo_filtered_df = geo_filtered_df[geo_filtered_df['Year'] == selected_year]


with main_tab1:
    st.header("Transaction Analysis")
    
    # Sub-filters specific to this tab
    st.markdown("### Detail Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        asset_types = ["All"] + sorted(geo_filtered_df['Asset Type'].dropna().unique().tolist())
        selected_asset_type = st.selectbox("Asset Type", asset_types)
        tab1_df = geo_filtered_df.copy()
        if selected_asset_type != "All":
            tab1_df = tab1_df[tab1_df['Asset Type'] == selected_asset_type]

    with col_f2:
        property_types = ["All"] + sorted(tab1_df['Property Type'].dropna().unique().tolist())
        selected_property_type = st.selectbox("Property Type", property_types)
        if selected_property_type != "All":
            tab1_df = tab1_df[tab1_df['Property Type'] == selected_property_type]

    with col_f3:
        sale_types = ["All"] + sorted(tab1_df['Sale Type'].dropna().unique().tolist())
        selected_sale_type = st.selectbox("Sale Type", sale_types)
        if selected_sale_type != "All":
            tab1_df = tab1_df[tab1_df['Sale Type'] == selected_sale_type]

    with col_f4:
        sequences = ["All"] + sorted(tab1_df['Sequence'].dropna().unique().tolist())
        selected_sequence = st.selectbox("Sequence", sequences)
        if selected_sequence != "All":
            tab1_df = tab1_df[tab1_df['Sequence'] == selected_sequence]

    # Main Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Transactions", len(tab1_df))
    with m2:
        avg_price = tab1_df['Price (AED)'].mean()
        st.metric("Average Price", f"AED {avg_price:,.0f}" if not pd.isna(avg_price) else "-")
    with m3:
        avg_rate = tab1_df['Rate (AED/sqm)'].mean()
        st.metric("Average Rate (AED/sqm)", f"{avg_rate:,.2f}" if not pd.isna(avg_rate) else "-")

    # Time Series
    st.subheader("Price & Rate Trends")
    interval = st.radio("Select Interval", ["Yearly", "Quarterly", "Monthly"], horizontal=True, key="tab1_interval")

    if 'Registration' in tab1_df.columns and not tab1_df['Registration'].isna().all():
        if interval == "Yearly": group_col = 'Year'
        elif interval == "Quarterly": group_col = 'Quarter'
        else:
            tab1_df['MonthYear'] = tab1_df['Registration'].dt.to_period('M').astype(str)
            group_col = 'MonthYear'
            
        trend_df = tab1_df.groupby(group_col)[['Price (AED)', 'Rate (AED/sqm)']].mean().reset_index()
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.plotly_chart(px.line(trend_df, x=group_col, y='Price (AED)', title=f'Avg Price ({interval})'), use_container_width=True)
        with col_t2:
            st.plotly_chart(px.line(trend_df, x=group_col, y='Rate (AED/sqm)', title=f'Avg Rate ({interval})'), use_container_width=True)

    # Area Analysis
    st.subheader("Average Rate per Area")
    c_a1, c_a2 = st.columns(2)
    with c_a1:
        df_d = tab1_df.groupby('District')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
        st.plotly_chart(px.bar(df_d, x='District', y='Rate (AED/sqm)', title='Top Districts'), use_container_width=True)
    with c_a2:
        df_c = tab1_df.groupby('Community')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
        st.plotly_chart(px.bar(df_c, x='Community', y='Rate (AED/sqm)', title='Top Communities'), use_container_width=True)

    # Drill Downs
    st.subheader("Drill Downs")
    d_tab1, d_tab2, d_tab3 = st.tabs(["District", "Community", "Project"])
    with d_tab1:
        dist_df = tab1_df.groupby('District')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
        st.plotly_chart(px.pie(dist_df, values='Rate (AED/sqm)', names='District', title="Top 10 Districts by Avg Rate"), use_container_width=True)
    with d_tab2:
        comm_df = tab1_df.groupby('Community')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
        st.plotly_chart(px.pie(comm_df, values='Rate (AED/sqm)', names='Community', title="Top 10 Communities by Avg Rate"), use_container_width=True)
    with d_tab3:
        proj_df = tab1_df.groupby('Project')['Rate (AED/sqm)'].mean().reset_index().sort_values('Rate (AED/sqm)', ascending=False).head(10)
        st.plotly_chart(px.pie(proj_df, values='Rate (AED/sqm)', names='Project', title="Top 10 Projects by Avg Rate"), use_container_width=True)


with main_tab2:
    st.header("Real Estate Growth Indicators")
    
    if 'Quarter' not in geo_filtered_df.columns:
        st.warning("Date information missing. Indicators cannot be calculated.")
    else:
        # Calculate Indicators
        # We need data grouped by Quarter and Asset Type/Sale Type
        
        # 1. Ratios: Offplan/Ready
        # Group by Quarter, Asset Type, Sale Type
        base_counts = geo_filtered_df.groupby(['Quarter', 'Asset Type', 'Sale Type']).size().reset_index(name='count')
        
        def calc_ratio(asset):
            sub = base_counts[base_counts['Asset Type'] == asset]
            if sub.empty:
                # Return empty DF with expected columns filled with NaN to avoid ShapeError
                quarters = sorted(geo_filtered_df['Quarter'].unique())
                return pd.DataFrame({f'{asset} Offplan/Ready': [np.nan] * len(quarters)}, index=quarters)
            
            pivot = sub.pivot(index='Quarter', columns='Sale Type', values='count').fillna(0)
            
            # Ensure both columns exist for calculation
            for col in ['Off-plan', 'Ready']:
                if col not in pivot.columns:
                    pivot[col] = 0
            
            pivot[f'{asset} Offplan/Ready'] = pivot['Off-plan'] / pivot['Ready'].replace(0, 1)
            return pivot[[f'{asset} Offplan/Ready']]

        res_ratio = calc_ratio('Residential')
        com_ratio = calc_ratio('Commercial')
        
        ratio_df = res_ratio.join(com_ratio, how='outer').reset_index().sort_values('Quarter')
        ratio_df = ratio_df.rename(columns={'index': 'Quarter'}) # Handle index rename from join
        
        # Exclude Q1 2026 and format
        ratio_df = ratio_df[ratio_df['Quarter'] != '2026Q1']
        
        st.subheader("Market Composition: Offplan vs Ready Ratio")
        # Ensure columns exist before plotting to avoid Plotly errors
        y_cols_ratio = [c for c in ['Residential Offplan/Ready', 'Commercial Offplan/Ready'] if c in ratio_df.columns]
        if y_cols_ratio:
            fig1 = px.line(ratio_df, x='Quarter', y=y_cols_ratio,
                           title="Offplan to Ready Transaction Ratio", markers=True)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data available for Offplan vs Ready Ratio.")
        
        # 2. Growth Rates (QoQ)
        # Group by Quarter and Asset Type for total sales volume
        growth_counts = geo_filtered_df.groupby(['Quarter', 'Asset Type']).size().unstack(fill_value=0)
        
        # Ensure both columns exist
        for col in ['Residential', 'Commercial']:
            if col not in growth_counts.columns:
                growth_counts[col] = 0
                
        qoq_growth = growth_counts.pct_change(fill_method=None) * 100
        qoq_df = qoq_growth[['Residential', 'Commercial']].rename(columns={
            'Residential': 'Residential sales growth rate (QoQ)',
            'Commercial': 'Commercial sales growth rate (QoQ)'
        }).reset_index().sort_values('Quarter')
        
        # Apply filters: Remove Q1 2026 and outliers > 600%
        qoq_df = qoq_df[qoq_df['Quarter'] != '2026Q1']
        for col in ['Residential sales growth rate (QoQ)', 'Commercial sales growth rate (QoQ)']:
            if col in qoq_df.columns:
                qoq_df.loc[qoq_df[col] > 600, col] = None
        
        st.subheader("Sales Growth Momentum (Quarter-on-Quarter)")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if 'Residential sales growth rate (QoQ)' in qoq_df.columns:
                fig2r = px.line(qoq_df, x='Quarter', y='Residential sales growth rate (QoQ)',
                               title="Residential Sales Growth (QoQ %)", markers=True)
                fig2r.update_layout(yaxis_ticksuffix="%")
                st.plotly_chart(fig2r, use_container_width=True)
        with col_g2:
            if 'Commercial sales growth rate (QoQ)' in qoq_df.columns:
                fig2c = px.line(qoq_df, x='Quarter', y='Commercial sales growth rate (QoQ)',
                               title="Commercial Sales Growth (QoQ %)", markers=True)
                fig2c.update_layout(yaxis_ticksuffix="%")
                st.plotly_chart(fig2c, use_container_width=True)
        
        # 3. Growth Rates (YoY)
        yoy_growth = growth_counts.pct_change(periods=4, fill_method=None) * 100
        yoy_df = yoy_growth[['Residential', 'Commercial']].rename(columns={
            'Residential': 'Residential sales growth rate (YoY)',
            'Commercial': 'Commercial sales growth rate (YoY)'
        }).reset_index().sort_values('Quarter')
        
        # Apply filters: Remove Q1 2026 and outliers > 600%
        yoy_df = yoy_df[yoy_df['Quarter'] != '2026Q1']
        for col in ['Residential sales growth rate (YoY)', 'Commercial sales growth rate (YoY)']:
            if col in yoy_df.columns:
                yoy_df.loc[yoy_df[col] > 600, col] = None
        
        st.subheader("Long-term Market Momentum (Year-on-Year)")
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            if 'Residential sales growth rate (YoY)' in yoy_df.columns:
                fig3r = px.line(yoy_df, x='Quarter', y='Residential sales growth rate (YoY)',
                               title="Residential Sales Growth (YoY %)", markers=True)
                fig3r.update_layout(yaxis_ticksuffix="%")
                st.plotly_chart(fig3r, use_container_width=True)
        with col_g4:
            if 'Commercial sales growth rate (YoY)' in yoy_df.columns:
                fig3c = px.line(yoy_df, x='Quarter', y='Commercial sales growth rate (YoY)',
                               title="Commercial Sales Growth (YoY %)", markers=True)
                fig3c.update_layout(yaxis_ticksuffix="%")
                st.plotly_chart(fig3c, use_container_width=True)

        st.info("Growth rates are calculated based on the number of transactions.")

        # 4. Speculation Metrics (Flip Rate & Appreciation)
        st.subheader("Flipping Momentum")
        
        # Property attributes for identification
        prop_cols = ['Sold Area (sqm)', 'Plot Area (sqm)', 'Layout', 'District', 'Community', 'Project']
        available_prop_cols = [c for c in prop_cols if c in geo_filtered_df.columns]
        
        if len(available_prop_cols) > 0 and 'Registration' in geo_filtered_df.columns and 'Sequence' in geo_filtered_df.columns:
            # Sort to identify consecutive transactions
            df_sorted = geo_filtered_df.sort_values(by=available_prop_cols + ['Registration'])
            
            # Identify resales: transactions with Sequence 'Secondary'
            df_sorted['is_resale'] = (df_sorted['Sequence'] == 'Secondary')
            
            # Calculate days since last transaction (of any kind for this property group)
            df_sorted['prev_reg'] = df_sorted.groupby(available_prop_cols)['Registration'].shift(1)
            df_sorted['prev_price'] = df_sorted.groupby(available_prop_cols)['Price (AED)'].shift(1)
            df_sorted['days_since_last'] = (df_sorted['Registration'] - df_sorted['prev_reg']).dt.days
            
            # Definition: Flip is a resale > 0 and <= 183 days after the previous sale
            df_sorted['is_flip'] = df_sorted['is_resale'] & (df_sorted['days_since_last'] > 0) & (df_sorted['days_since_last'] <= 183)
            
            # Calculate appreciation for flips
            df_sorted['appreciation'] = (df_sorted['Price (AED)'] - df_sorted['prev_price']) / df_sorted['prev_price'].replace(0, np.nan)
            
            # Group by Quarter
            # Total Resales = all Secondary transactions in that quarter
            resale_stats = df_sorted.groupby('Quarter').agg(
                total_resales=('is_resale', 'sum'),
                flips=('is_flip', 'sum')
            ).reset_index()
            
            resale_stats['Flip Rate (%)'] = (resale_stats['flips'] / resale_stats['total_resales'].replace(0, 1)) * 100
            
            # Appreciation Stats: Mean of filtered flips
            flips_only = df_sorted[
                (df_sorted['is_flip']) & 
                (df_sorted['Price (AED)'] > 10000) & 
                (df_sorted['prev_price'] > 10000)
            ].copy()
            
            if not flips_only.empty:
                # Outlier filter for appreciation
                flips_only = flips_only[(flips_only['appreciation'] < 5) & (flips_only['appreciation'] > -0.8)]
                apprec_stats = flips_only.groupby('Quarter')['appreciation'].mean().reset_index()
                apprec_stats['Flip Price Appreciation (%)'] = apprec_stats['appreciation'] * 100
            else:
                apprec_stats = pd.DataFrame(columns=['Quarter', 'Flip Price Appreciation (%)'])

            # Filter out current incomplete quarter
            flip_df = resale_stats[resale_stats['Quarter'] != '2026Q1'].sort_values('Quarter')
            apprec_df = apprec_stats[apprec_stats['Quarter'] != '2026Q1'].sort_values('Quarter')
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if not flip_df.empty and flip_df['total_resales'].sum() > 0:
                    fig4 = px.line(flip_df, x='Quarter', y='Flip Rate (%)',
                                   title="Flip Rate (Resales ≤ 183 Days)",
                                   markers=True)
                    fig4.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.info("No resale data available for Flip Rate.")
            
            with col_f2:
                if not apprec_df.empty:
                    fig5 = px.line(apprec_df, x='Quarter', y='Flip Price Appreciation (%)',
                                   title="Flip Price Appreciation (Mean %)",
                                   markers=True)
                    fig5.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig5, use_container_width=True)
                else:
                    st.info("No market-rate flip transactions detected for appreciation.")

            st.caption("Flip Rate = (Resales ≤ 183 days / Total Resales) × 100. Total Resales are transactions with 'Secondary' sequence. Properties are identified by Area, Layout, and Project attributes.")
        else:
            st.warning("Insufficient data (Missing 'Sequence' or Attributes) to calculate Speculation metrics.")

