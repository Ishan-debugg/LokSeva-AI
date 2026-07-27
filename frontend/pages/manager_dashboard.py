import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:3000"

def render():
    col1, col2, col3 = st.columns([6, 2, 2])

    with col1:
        st.markdown('<div class="secondary-btn-container">', unsafe_allow_html=True)
        if st.button("← Back to Home", key="manager_back_home_btn"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if st.button(" SLA Dashboard", key="manager_sla_btn", use_container_width=True):
            st.session_state.page = "sla"
            st.rerun()

    with col3:
        st.markdown('<div class="secondary-btn-container">', unsafe_allow_html=True)
        if st.button("Logout", key="manager_logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h2 style='color: var(--primary-blue); margin-bottom: 1.5rem;'>🏛 District Management Overview Console</h2>", unsafe_allow_html=True)

    try:
        response = requests.get(f"{API_URL}/complaints")
        if response.status_code == 200:
            complaints = response.json()
        else:
            st.error("Failed to fetch complaint database from server.")
            return
    except Exception as e:
        st.error(f"Backend connection failed: {e}")
        return

    if not complaints:
        st.warning("No complaint records currently exist in the database System .")
        return

    df = pd.DataFrame(complaints)

    total       = len(df)
    pending     = len(df[df["status"] == "pending"])
    in_progress = len(df[df["status"] == "in progress"])
    resolved    = len(df[df["status"] == "resolved"])
    escalated   = len(df[df["escalated"] == True]) if "escalated" in df.columns else 0

    colA, colB, colC, colD, colE = st.columns(5)
    with colA:
        st.markdown(f'<div class="stat-tile"><div class="num">{total}</div><div class="lbl">Total Complaints</div></div>', unsafe_allow_html=True)
    with colB:
        st.markdown(f'<div class="stat-tile"><div class="num">{pending}</div><div class="lbl">Pending</div></div>', unsafe_allow_html=True)
    with colC:
        st.markdown(f'<div class="stat-tile"><div class="num">{in_progress}</div><div class="lbl">In Progress</div></div>', unsafe_allow_html=True)
    with colD:
        st.markdown(f'<div class="stat-tile"><div class="num">{resolved}</div><div class="lbl">Resolved</div></div>', unsafe_allow_html=True)
    with colE:
        st.markdown(f'<div class="stat-tile" style="border-color: var(--red-danger);"><div class="num" style="color: var(--red-danger);">{escalated}</div><div class="lbl">Escalated</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    color_palette = ["#1e3a8a", "#0284c7", "#b45309", "#16a34a", "#dc2626", "#64748b"]
    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown("<h3 style='color: var(--text-dark); font-size: 1.3rem; margin-bottom: 0.8rem;'>Complaints by Department</h3>", unsafe_allow_html=True)
        dept_chart = px.bar(
            df, x="department", title=None,
            color="department", color_discrete_sequence=color_palette
        )
        dept_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#334155', xaxis_title="Department", yaxis_title="Count",
            showlegend=False, margin=dict(t=10)
        )
        st.plotly_chart(dept_chart, use_container_width=True)

    with chart_col2:
        st.markdown("<h3 style='color: var(--text-dark); font-size: 1.3rem; margin-bottom: 0.8rem;'>Complaints by Status</h3>", unsafe_allow_html=True)
        status_chart = px.pie(
            df, names="status", title=None,
            color_discrete_sequence=color_palette
        )
        status_chart.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#334155', margin=dict(t=10)
        )
        st.plotly_chart(status_chart, use_container_width=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if "escalated" in df.columns:
        esc = df[df["escalated"] == True]
        st.markdown("<h3 style='color: var(--red-danger); font-size: 1.3rem; margin-bottom: 0.8rem;'>⚠️ Urgent Escalations (SLA Overdue)</h3>", unsafe_allow_html=True)
        if len(esc) > 0:
            st.dataframe(esc[["id", "complaint_text", "department", "priority", "deadline"]], use_container_width=True)
        else:
            st.markdown("""
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1rem; color: #166534; font-size: 0.95rem; text-align: center; margin-bottom: 1.5rem;">
                All active complaints are currently operating within SLA deadlines. No escalations.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: var(--text-dark); font-size: 1.4rem; margin-bottom: 0.8rem;'>View / Update Complaint Details</h3>", unsafe_allow_html=True)

    complaint_ids = df["id"].tolist()
    selected_id = st.selectbox("Select Complaint ID to View Details", complaint_ids, key="manager_select_cid")

    if selected_id:
        selected_row = df[df["id"] == selected_id].iloc[0]

        st.markdown(f"""
        <div class="lk-card" style="border-left: 5px solid var(--primary-blue);">
            <h4 style="margin: 0; color: var(--primary-blue); font-size: 1.15rem;">Grievance ID Reference: #{selected_id}</h4>
            <p style="margin: 0.8rem 0; font-size: 0.98rem; line-height: 1.6; color: var(--text-body); background-color: var(--bg-main); padding: 1rem; border-radius: 6px; border: 1.5px solid var(--border-color);">
                <strong>Citizen Description:</strong> "{selected_row['complaint_text']}"
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.92rem; color: var(--text-body);">
                <div>
                    <strong>Category:</strong> {selected_row.get('category', 'N/A').upper()}<br>
                    <strong>Priority:</strong> {selected_row.get('priority', 'N/A').upper()}<br>
                    <strong>Current Status:</strong> {selected_row.get('status', 'N/A').upper()}
                </div>
                <div>
                    <strong>Assigned Department:</strong> {selected_row.get('department', 'N/A')}<br>
                    <strong>SLA Deadline:</strong> {selected_row.get('deadline', 'N/A')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        image_path = selected_row.get("image_path")
        if pd.notna(image_path) and image_path:
            st.image(f"{API_URL}/{image_path}", caption=f"Evidence for ID: {selected_id}", width=400)
        else:
            st.markdown("""
            <div style="background-color: var(--bg-card); border: 1.5px dashed var(--border-color); padding: 0.8rem; border-radius: 8px; font-size: 0.9rem; color: var(--text-muted); text-align: center; margin-bottom: 1.5rem;">
                📷 No photo evidence was uploaded with this complaint.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h4 style='color: var(--text-dark); margin-top: 1rem; margin-bottom: 0.5rem;'>Set Complaint Status</h4>", unsafe_allow_html=True)

        current_status = selected_row.get("status", "pending")
        status_options = ["pending", "in progress", "resolved"]
        default_index = status_options.index(current_status) if current_status in status_options else 0

        new_status = st.selectbox("Target Status", status_options, index=default_index, key="manager_new_status")

        if st.button("Apply Status Modification", key="manager_update_status_btn"):
            try:
                resp = requests.put(
                    f"{API_URL}/complaints/{selected_id}",
                    json={"status": new_status}
                )
                if resp.status_code == 200:
                    st.success("Grievance status modified successfully!")
                    st.rerun()
                else:
                    st.error("Failed to commit status change to backend.")
            except Exception as e:
                st.error(f"Database update error: {e}")