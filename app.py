import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Curve Price Dashboard", layout="wide")

st.title("Four Corners, Mona, Palo Verde, Pinnacle Peak Price Report Dashboard")

# Load data from Excel
@st.cache_data
def load_data():
    df_raw = pd.read_excel("reports/data_report.xlsx", sheet_name="Raw Data", parse_dates=["ASSESSDATE"])
    return df_raw

df = load_data()

# Create tabs
tab1, tab2, tab3 = st.tabs(["Peak & Off-Peak Charts", "Seasonality Trends", "DoD Comparison"])

# === Tab 1: Peak and Off-Peak Charts ===
with tab1:
    st.subheader("Interactive Price Charts")

    peak_df = df[df["DESCRIPTION"].str.contains(" Pk ", case=False)]
    offpeak_df = df[df["DESCRIPTION"].str.contains(" OPk ", case=False)]

    st.markdown("### Peak Curves")
    fig_peak = px.line(peak_df, x="ASSESSDATE", y="VALUE", color="DESCRIPTION",
                       title="Peak Curves Over Time", height=600)
    st.plotly_chart(fig_peak, use_container_width=True)

    st.markdown("### Off-Peak Curves")
    fig_off = px.line(offpeak_df, x="ASSESSDATE", y="VALUE", color="DESCRIPTION",
                      title="Off-Peak Curves Over Time", height=600)
    st.plotly_chart(fig_off, use_container_width=True)

# === Tab 2: Seasonality Chart ===
with tab2:
    st.subheader("Seasonality by Curve")

    df["MONTH"] = df["ASSESSDATE"].dt.strftime("%b")
    df["YEAR"] = df["ASSESSDATE"].dt.year

    grouped = df.groupby(["YEAR", "MONTH", "DESCRIPTION"])["VALUE"].mean().reset_index()
    symbols = grouped["DESCRIPTION"].unique()

    selected_symbol = st.selectbox("Choose a curve to view seasonality", sorted(symbols))

    temp = grouped[grouped["DESCRIPTION"] == selected_symbol]
    fig_season = px.line(temp, x="MONTH", y="VALUE", color="YEAR",
                         title=f"Seasonality Trend: {selected_symbol}", markers=True, height=600)
    st.plotly_chart(fig_season, use_container_width=True)

# === Tab 3: DoD Comparison ===
with tab3:
    st.subheader("Compare Two Curves: Value and Difference")

    curves = sorted(df["DESCRIPTION"].unique())
    curve1 = st.selectbox("Select first curve", curves, key="curve1")
    curve2 = st.selectbox("Select second curve", curves, key="curve2")

    comp_df = df[df["DESCRIPTION"].isin([curve1, curve2])]
    pivot_df = comp_df.pivot(index="ASSESSDATE", columns="DESCRIPTION", values="VALUE").dropna()

    if curve1 in pivot_df.columns and curve2 in pivot_df.columns:
        pivot_df["DIFFERENCE"] = pivot_df[curve1] - pivot_df[curve2]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[curve1], mode='lines', name=curve1))
        fig.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[curve2], mode='lines', name=curve2))
        fig.add_trace(go.Bar(x=pivot_df.index, y=pivot_df["DIFFERENCE"], name='Difference', marker_color='lightblue'))
        fig.update_layout(title=f"Value Comparison and Difference: {curve1} vs {curve2}", barmode='overlay', height=600)

        st.plotly_chart(fig, use_container_width=True)

