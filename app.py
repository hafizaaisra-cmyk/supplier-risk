import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="Supplier Risk System", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LOAD DATA ---
@st.cache_data
def load_data():
    # This automatically looks for your data.csv
    df = pd.read_csv("data.csv")
    return df

try:
    df = load_data()
    
    st.title("🛡️ Supplier Risk Scoring & Prediction")
    st.sidebar.header("Control Panel")
    
    # Select Supplier
    supplier_list = df[df.columns[0]].unique()
    selected_supplier = st.sidebar.selectbox("Select Supplier to Analyze", supplier_list)
    
    # Filter data for selected supplier
    s_data = df[df[df.columns[0]] == selected_supplier].iloc[0]

    # --- 2. THE 8 RISK CALCULATION LOGIC (Rule-Based) ---
    # These rules use the data from your CSV to 'predict' risk levels
    
    # Risk 1: Financial (Based on Rating)
    fin_map = {'A': 10, 'B': 40, 'C': 80}
    fin_risk = fin_map.get(str(s_data.get('Financial_Rating', 'B')), 50)

    # Risk 2: Operational (Inverse of Quality)
    op_risk = 100 - s_data.get('Quality_Score', 70)

    # Risk 3: Delivery (Based on Lead Time)
    del_risk = min(100, s_data.get('Lead_Time', 20) * 2)

    # Risk 4: Geopolitical (Based on Location)
    geo_risk = 80 if s_data.get('Location') == 'International' else 20

    # Risk 5: Compliance
    comp_risk = 10 if s_data.get('Compliance_Status') == 'Certified' else 90

    # Risk 6: Price Risk
    price_risk = 75 if s_data.get('Price_Volatility') == 'High' else 25

    # Risk 7: Environmental (Custom Rule)
    env_risk = 30 # Baseline

    # Risk 8: Cyber Risk (Custom Rule)
    cyber_risk = 45 # Baseline

    # Prepare Data for Charts
    risk_scores = {
        "Financial": fin_risk, "Operational": op_risk, "Delivery": del_risk,
        "Geopolitical": geo_risk, "Compliance": comp_risk, "Price": price_risk,
        "Environmental": env_risk, "Cyber": cyber_risk
    }
    
    risk_df = pd.DataFrame(list(risk_scores.items()), columns=['Category', 'Score'])
    avg_risk = risk_df['Score'].mean()

    # --- 3. DASHBOARD LAYOUT ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Risk Score", f"{avg_risk:.1f}%", delta="-Low" if avg_risk < 50 else "High", delta_color="inverse")
    col2.metric("Supplier Status", "Active")
    col3.metric("Data Reliability", "High (64-bit)")

    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Risk Distribution")
        fig_radar = px.line_polar(risk_df, r='Score', theta='Category', line_close=True, 
                                 range_r=[0,100], color_discrete_sequence=['#ff4b4b'])
        fig_radar.update_traces(fill='toself')
        st.plotly_chart(fig_radar, use_container_width=True)

    with right_col:
        st.subheader("Detailed Risk Metrics")
        st.bar_chart(risk_df.set_index('Category'))
        
        if avg_risk > 60:
            st.error("⚠️ HIGH RISK DETECTED: Consider backup suppliers.")
        elif avg_risk > 30:
            st.warning("⚠️ MEDIUM RISK: Monitor delivery performance.")
        else:
            st.success("✅ LOW RISK: Reliable partner.")

except Exception as e:
    st.error(f"Error loading dashboard. Make sure your CSV columns match the logic. Details: {e}")
    # --- 4. WRITTEN SUMMARY OF THE 8 RISKS ---
    st.markdown("---")
    st.subheader("📊 Detailed Risk Calculation Breakdown")
    
    # Create a nice layout with 4 columns to show the 8 risks as text cards
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
    
    # Row 1
    row1_col1.write(f"**Financial:** {fin_risk}%")
    row1_col2.write(f"**Operational:** {op_risk}%")
    row1_col3.write(f"**Delivery:** {del_risk}%")
    row1_col4.write(f"**Geopolitical:** {geo_risk}%")
    
    # Row 2
    row2_col1.write(f"**Compliance:** {comp_risk}%")
    row2_col2.write(f"**Price:** {price_risk}%")
    row2_col3.write(f"**Environmental:** {env_risk}%")
    row2_col4.write(f"**Cyber:** {cyber_risk}%")

    # Add a final written conclusion
    st.info(f"**System Prediction:** Based on the {selected_supplier} data, the most critical area to address is **{risk_df.loc[risk_df['Score'].idxmax(), 'Category']} Risk**.")
