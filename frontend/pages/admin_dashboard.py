import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from utils.styles import style_plotly_figure

API_URL = "http://localhost:3000"

def render():

    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    st.markdown("## Complaint Management")

    try:
        response = requests.get(f"{API_URL}/complaints")
        if response.status_code == 200:
            complaints = response.json()
        else:
            st.error("Failed to load complaints")
            return
    except:
        st.error("Backend server not running")
        return

    if not complaints:
        st.warning("No complaints found")
        return

    df = pd.DataFrame(complaints)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(df))
    with col2:
        st.metric("Pending", len(df[df["status"] == "pending"]))
    with col3:
        st.metric("In Progress", len(df[df["status"] == "in progress"]))
    with col4:
        st.metric("Resolved", len(df[df["status"] == "resolved"]))

    st.markdown("### Complaints Table")
    st.dataframe(df, use_container_width=True)

    department_filter = st.selectbox("Department", [
        "All",
        "Road & Traffic management Department",
        "Solid Waste Management",
        "Electric Department",
        "Water Supply Department",
        "Sewage & Drainage Department",
        "Encroachment Department"
    ])

    filtered_df = df[df["department"] == department_filter] if department_filter != "All" else df

    dept_chart = px.pie(filtered_df, names="department")
    st.plotly_chart(style_plotly_figure(dept_chart), use_container_width=True, theme=None)

    st.markdown("### Complaints by Status")
    status_chart = px.bar(filtered_df, x="status")
    st.plotly_chart(style_plotly_figure(status_chart), use_container_width=True, theme=None)

    st.markdown("### Update Complaint Status")
    complaint_ids = filtered_df["id"].tolist()
    selected_id = st.selectbox("Select Complaint ID", complaint_ids)

    new_status = st.selectbox("New Status", ["pending", "in progress", "resolved"])

    if st.button("Update Status"):
        try:
            response = requests.put(
                f"{API_URL}/complaints/{selected_id}",
                json={"status": new_status}
            )
            if response.status_code == 200:
                st.success("Status Updated")
                st.rerun()
            else:
                st.error("Update failed")
        except:
            st.error("Backend error")