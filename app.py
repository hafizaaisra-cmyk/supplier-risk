import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETUP & DATA LOADING
st.set_page_config(page_title="Supply Chain Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Use your exact filename
    df = pd.read_csv("data.csv")
    return df

try:
    df = load_data()
    st.title("🛡️ Supplier Risk Scoring & Prediction")
    
    # 2. SIDEBAR - SUPPLIER SELECTION
    st.sidebar.header("Control Panel")
    
    # Using 'supplier_id' from your file
    supplier_list = df['supplier_id'].unique()
    selected_supplier = st.sidebar.selectbox("Select Supplier ID", supplier_list)

    # Filter data for selected supplier
    s_data = df[df['supplier_id'] == selected_supplier].iloc[0]

    # 3. RISK CALCULATION LOGIC (Using your actual columns)
    # Mapping the 8 risks to your specific data columns
    lead_risk = min(s_data['supplier_lead_time_days'] * 10, 100)
    qual_risk = 100 - s_data['supplier_quality_score']
    rel_risk  = (1 - s_data['supplier_reliability_index']) * 100
    log_risk  = min(s_data['port_delay_days'] * 15, 100)
    econ_risk = min(s_data['fuel_price_index'] * 40, 100)
    dem_risk  = s_data['market_demand_index'] * 100
    env_risk  = min(s_data['weather_disruption_score'] * 10, 100)
    inv_risk  = min((s_data['pending_orders'] / 600) * 100, 100)

    # Calculate Overall Risk (Average of the 8)
    avg_risk = (lead_risk + qual_risk + rel_risk + log_risk + econ_risk + dem_risk + env_risk + inv_risk) / 8
    
    # Use your file's existing probability for the main gauge
    final_prob = s_data['risk_probability'] * 100

    # 4. TOP METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Risk Score", f"{final_prob:.1f}%")
    col2.metric("Supplier ID", selected_supplier)
    col3.metric("Risk Label", s_data['risk_label'])

    # 5. VISUALIZATIONS
    view_col1, view_col2 = st.columns(2)

    with view_col1:
        st.subheader("Risk Distribution (Radar Chart)")
        risk_df = pd.DataFrame({
            'Category': ['Lead Time', 'Quality', 'Reliability', 'Logistics', 'Economic', 'Demand', 'Environmental', 'Inventory'],
            'Score': [lead_risk, qual_risk, rel_risk, log_risk, econ_risk, dem_risk, env_risk, inv_risk]
        })
        fig = px.line_polar(risk_df, r='Score', theta='Category', line_close=True)
        fig.update_traces(fill='toself', line_color='red')
        st.plotly_chart(fig, use_container_width=True)

    with view_col2:
        st.subheader("Detailed Risk Metrics (Bar Chart)")
        st.bar_chart(risk_df.set_index('Category'))

    # 6. WRITTEN REPRESENTATION (The table you wanted)
    st.divider()
    st.subheader("📋 Written Risk Assessment Summary")
    
    display_df = risk_df.copy()
    display_df['Status'] = display_df['Score'].apply(lambda x: "🔴 High" if x > 60 else ("🟡 Medium" if x > 30 else "🟢 Low"))
    st.table(display_df)

    # Final System Prediction based on your file's Label
    if s_data['risk_label'] == 'High':
        st.error(f"CRITICAL PREDICTION: {selected_supplier} is flagged as HIGH RISK. Immediate mitigation required.")
    elif s_data['risk_label'] == 'Medium':
        st.warning(f"CAUTION PREDICTION: {selected_supplier} is stable but shows vulnerability in {risk_df.loc[risk_df['Score'].idxmax(), 'Category']}.")
    else:
        st.success(f"SAFE PREDICTION: {selected_supplier} is a reliable partner.")

except Exception as e:
    st.error(f"⚠️ Column Error: {e}")
    st.info("Ensure your file is named 'supply_chain_risk_dataset.csv' on GitHub.")
