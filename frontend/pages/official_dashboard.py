import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from utils.styles import style_plotly_figure

API_URL = "http://localhost:3000"


def render():
    # ---------------- Header ---------------- #
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <h2 style="color:#1e3a8a;">🏛 Official Overview Console</h2>
        <p style="color:gray;">
            System-wide real-time analytics for government officials
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ---------------- Navigation ---------------- #
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "Access Admin Console",
            key="official_nav_admin",
            use_container_width=True,
        ):
            st.session_state.page = "admin"
            st.rerun()

    with col2:
        if st.button(
            "Access Manager Console",
            key="official_nav_manager",
            use_container_width=True,
        ):
            st.session_state.page = "manager"
            st.rerun()

    with col3:
        if st.button(
            "Secure Logout",
            key="official_nav_logout",
            use_container_width=True,
        ):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("---")

    # ---------------- Load Complaint Data ---------------- #
    try:
        r = requests.get(f"{API_URL}/complaints")

        if r.status_code != 200:
            st.warning("No complaint data found.")
            return

        complaints = r.json()
        df = pd.DataFrame(complaints)

    except Exception as e:
        st.error(f"Backend server not running.\n\n{e}")
        return

    if df.empty:
        st.info("No complaints submitted yet.")
        return

    # ---------------- Metrics ---------------- #
    total = len(df)
    pending = len(df[df["status"] == "pending"])
    progress = len(df[df["status"] == "in progress"])
    resolved = len(df[df["status"] == "resolved"])

    colA, colB, colC, colD = st.columns(4)

    colA.metric("Total Complaints", total)
    colB.metric("Pending", pending)
    colC.metric("In Progress", progress)
    colD.metric("Resolved", resolved)

    st.markdown("---")

    # ---------------- SLA Warning ---------------- #
    if pending > 5:
        st.warning(
            f"⚠️ High number of pending complaints ({pending}). "
            "Immediate action is recommended."
        )

    # ---------------- Charts ---------------- #
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📊 Complaints by Department")

        dept_chart = px.bar(
            df,
            x="department",
            color="department",
            title=None,
        )

        dept_chart.update_layout(showlegend=False)

        st.plotly_chart(style_plotly_figure(dept_chart), use_container_width=True, theme=None)

    with chart_col2:
        st.subheader("📈 Complaint Status")

        status_chart = px.pie(
            df,
            names="status",
            title=None,
        )

        st.plotly_chart(style_plotly_figure(status_chart), use_container_width=True, theme=None)

    st.markdown("---")

    # ---------------- Recent Complaints ---------------- #
    st.subheader("📋 Recent Complaints")

    cols = [
        c
        for c in [
            "id",
            "department",
            "priority",
            "status",
            "created_at",
        ]
        if c in df.columns
    ]

    if cols:
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
        