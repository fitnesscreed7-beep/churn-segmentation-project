import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Customer Churn & Segmentation Dashboard", layout="wide")

# Load data
rfm = pd.read_csv('data/processed/rfm_final.csv')

st.title("E-Commerce Retention Analytics")
st.markdown("### RFM Segmentation & Churn Prediction Dashboard")

# --- KPI Summary ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(rfm):,}")
col2.metric("Avg CLV", f"${rfm['CLV_proxy'].mean():,.0f}")
col3.metric("Avg Churn Risk", f"{rfm['Churn_Probability'].mean():.1%}")
col4.metric("High-Risk Customers", f"{(rfm['Churn_Probability'] > 0.7).sum():,}")

st.divider()

# --- Row 1: Segment Donut + Scatter ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Customer Distribution by Segment")
    fig_donut = px.pie(rfm, names='Segment', hole=0.4)
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    st.subheader("Recency vs Monetary (colored by Churn Risk)")
    fig_scatter = px.scatter(
        rfm, x='Recency', y='Monetary', color='Churn_Probability',
        color_continuous_scale='RdYlGn_r', opacity=0.5,
        hover_data=['Segment', 'CLV_proxy']
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --- Row 2: Churn Risk by Segment ---
st.subheader("Average Churn Risk by Segment")
risk_by_segment = rfm.groupby('Segment')['Churn_Probability'].mean().sort_values(ascending=False).reset_index()
fig_bar = px.bar(risk_by_segment, x='Segment', y='Churn_Probability', color='Churn_Probability', color_continuous_scale='RdYlGn_r')
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# --- Action List: High-Value, High-Risk Customers ---
st.subheader("🎯 Priority Retention List (High-Value, High-Risk)")
clv_threshold = rfm['CLV_proxy'].quantile(0.75)
action_list = rfm[
    (rfm['CLV_proxy'] >= clv_threshold) & (rfm['Churn_Probability'] >= 0.5)
].sort_values('Churn_Probability', ascending=False)

st.dataframe(
    action_list[['Customer Id', 'Segment', 'Recency', 'Frequency', 'Monetary', 'CLV_proxy', 'Churn_Probability']].head(50),
    use_container_width=True
)
st.caption(f"{len(action_list)} customers meet high-value (top 25% CLV) + high-risk (>50% churn probability) criteria")
