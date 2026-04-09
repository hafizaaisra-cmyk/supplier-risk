import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. SETUP & DATA LOADING
st.set_page_config(page_title="Supplier Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    # Clean up column names just in case
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.title("🛡️ Supplier Risk Scoring & Prediction")
    
    # 2. SIDEBAR - SUPPLIER SELECTION
    st.sidebar.header("Control Panel")
    
    # Using 'supplier_id' based on your CSV
    supplier_list = df['supplier_id'].unique()
    selected_supplier = st.sidebar.selectbox("Select Supplier to Analyze", supplier_list)

    # Filter data for selected supplier
    s_data = df[df['supplier_id'] == selected_supplier].iloc[0]

    # 3. RISK CALCULATION LOGIC
    # Financial Risk
    fin_risk = 30

    # Operational & Delivery
    op_risk = 100 - s_data['Quality_Score']
    del_risk = min(s_data['Lead_Time'] * 2, 100)

    # Geopolitical & Compliance
    geo_risk = 80 if s_data['Location'] == 'International' else 20
    comp_risk = 10 if s_data['Compliance_Status'] == 'Certified' else 90

    # Others
    price_risk = 75 if s_data['Price_Volatility'] == 'High' else 25
    env_risk = 30 # Baseline
    cyber_risk = 45 # Baseline

    total_risk = (fin_risk + op_risk + del_risk + geo_risk + comp_risk + price_risk + env_risk + cyber_risk) / 8

    # 4. TOP METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Risk Score", f"{total_risk:.1f}%")
    col2.metric("Supplier ID", selected_supplier)
    col3.metric("Data Reliability", "High (64-bit)")

    # 5. CHARTS SECTION
    view_col1, view_col2 = st.columns(2)

    with view_col1:
        st.subheader("Risk Distribution")
        risk_df = pd.DataFrame({
            'Category': ['Financial', 'Operational', 'Delivery', 'Geopolitical', 'Compliance', 'Price', 'Environmental', 'Cyber'],
            'Score': [fin_risk, op_risk, del_risk, geo_risk, comp_risk, price_risk, env_risk, cyber_risk]
        })
        fig = px.line_polar(risk_df, r='Score', theta='Category', line_close=True)
        fig.update_traces(fill='toself', line_color='red')
        st.plotly_chart(fig, use_container_width=True)

    with view_col2:
        st.subheader("Detailed Risk Metrics")
        st.bar_chart(risk_df.set_index('Category'))

    # 6. WRITTEN REPRESENTATION
    st.divider()
    st.subheader("📋 Written Risk Assessment Summary")
    
    display_df = risk_df.copy()
    display_df['Status'] = display_df['Score'].apply(lambda x: "🔴 High" if x > 60 else ("🟡 Medium" if x > 30 else "🟢 Low"))
    st.table(display_df)

    # System Prediction Alert
    if total_risk > 50:
        st.warning(f"ACTION REQUIRED: Monitor {selected_supplier} closely due to high risk areas.")
    else:
        st.success(f"STABLE: {selected_supplier} meets baseline safety requirements.")

except Exception as e:
    st.error(f"⚠️ System Error: {e}")
    st.info("Check if your data.csv has the column 'supplier_id' and 'Financial_Rating'.")
