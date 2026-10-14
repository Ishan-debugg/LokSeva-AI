import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.styles import style_plotly_figure

API_URL = "http://localhost:3000"
IST = "Asia/Kolkata"


def render():
    st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

    col1, col2 = st.columns([8, 2])
    with col1:
        if st.button("Back", key="sla_back"):
            st.session_state.page = "manager"
            st.rerun()
    with col2:
        if st.button("Logout", key="sla_logout"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    now = pd.Timestamp.now(tz=IST)

    st.markdown("## 📊 SLA Monitoring Dashboard")
    st.markdown("Track complaint resolution deadlines and department compliance.")
    st.caption(f"🕐 Last refreshed: {now.strftime('%d %b %Y, %H:%M:%S IST')} · auto-refreshes every 5 minutes")

    # ── Fetch all data ────────────────────────────────────
    try:
        alerts_resp  = requests.get(f"{API_URL}/sla/alerts")
        summary_resp = requests.get(f"{API_URL}/sla/summary")
        all_resp     = requests.get(f"{API_URL}/complaints")

        alerts   = alerts_resp.json()  if alerts_resp.status_code  == 200 else []
        summary  = summary_resp.json() if summary_resp.status_code == 200 else []
        all_data = all_resp.json()     if all_resp.status_code     == 200 else []
    except:
        st.error("❌ Backend not running. Start with: node backend/server.js")
        return

    # ── Normalize summary ─────────────────────────────────
    df = pd.DataFrame()
    if summary:
        df = pd.DataFrame(summary)
        for col in ["total", "resolved", "active", "on_track", "at_risk", "breached"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df["compliance_pct"] = pd.to_numeric(df.get("compliance_pct"), errors="coerce").fillna(0)

    total_breached = int(df["breached"].sum()) if not df.empty else 0
    total_at_risk  = int(df["at_risk"].sum())  if not df.empty else 0

    # ── Alert banner ──────────────────────────────────────
    if total_breached > 0:
        st.error(f"🚨 **{total_breached} complaint(s) have BREACHED their SLA deadline!**")
    if total_at_risk > 0:
        st.warning(f"⚠️ **{total_at_risk} complaint(s) are AT RISK of breaching within 24 hours.**")
    if total_breached == 0 and total_at_risk == 0:
        st.success("✅ All active complaints are within SLA deadlines.")

    # ── 6 metrics — mathematically consistent ────────────
    if not df.empty:
        total    = int(df["total"].sum())
        resolved = int(df["resolved"].sum())
        active   = int(df["active"].sum())
        on_track = int(df["on_track"].sum())

        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("Total Complaints",    total)
        r1c2.metric("Active Complaints",   active)
        r1c3.metric("Resolved Complaints", resolved)

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.metric("🟢 On Track", on_track)
        r2c2.metric("🟠 At Risk",  total_at_risk)
        r2c3.metric("🔴 Breached", total_breached)

        st.caption(
            f"✅ Total ({total}) = Active ({active}) + Resolved ({resolved})  |  "
            f"Active ({active}) = On Track ({on_track}) + At Risk ({total_at_risk}) + Breached ({total_breached})"
        )

    st.divider()

    # ── Department compliance charts ──────────────────────
    if not df.empty:
        st.markdown("### 🏢 Department-wise SLA Compliance")
        st.caption("Compliance % = complaints resolved before deadline ÷ total in department × 100")

        below_target = int((df["compliance_pct"] < 80).sum())
        if below_target > 0:
            st.caption(f"⚠️ {below_target} department(s) below the 80% compliance target")

        fig_bar = px.bar(
            df, x="department", y="compliance_pct",
            color="compliance_pct",
            color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
            range_color=[0, 100],
            labels={"compliance_pct": "Compliance %", "department": "Department"},
            title="SLA Compliance % by Department"
        )
        fig_bar.update_layout(showlegend=False, height=400)
        fig_bar.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="80% target")
        st.plotly_chart(style_plotly_figure(fig_bar), use_container_width=True, theme=None)

        st.markdown("### 📊 Complaint Status Breakdown by Department")
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(name="🟢 On Track", x=df["department"], y=df["on_track"], marker_color="#2ecc71"))
        fig_stack.add_trace(go.Bar(name="🟠 At Risk",  x=df["department"], y=df["at_risk"],  marker_color="#f39c12"))
        fig_stack.add_trace(go.Bar(name="🔴 Breached", x=df["department"], y=df["breached"], marker_color="#e74c3c"))
        fig_stack.add_trace(go.Bar(name="🔵 Resolved", x=df["department"], y=df["resolved"], marker_color="#3498db"))
        fig_stack.update_layout(barmode="stack", height=400, xaxis_tickangle=-30)
        st.plotly_chart(style_plotly_figure(fig_stack), use_container_width=True, theme=None)

        st.download_button(
            "⬇️ Download compliance report (CSV)",
            df.to_csv(index=False),
            file_name="sla_compliance_report.csv",
            mime="text/csv",
        )

    st.divider()

    # ── Active SLA Alerts ─────────────────────────────────
    if alerts:
        st.markdown("### 🔔 Active SLA Alerts")
        STATUS_LABEL = {"breached": "🔴 Breached", "at_risk": "🟠 At Risk"}
        df_a = pd.DataFrame(alerts)
        df_a["sla_status"] = df_a["sla_status"].map(lambda s: STATUS_LABEL.get(s, s))
        df_a["deadline"] = (
            pd.to_datetime(df_a["deadline"], utc=True, errors="coerce")
              .dt.tz_convert(IST)
              .dt.strftime("%d %b %Y %H:%M IST")
        )
        st.dataframe(
            df_a[["id", "complaint_text", "department", "priority", "sla_status", "deadline"]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No active alerts at this time.")

    st.divider()

    # ── All complaints with deadline indicator ────────────
    st.markdown("### 📋 All Complaints with Deadline Indicator")
    st.caption("Sorted by urgency — most overdue first, resolved last.")

    if all_data:
        try:
            df_all = pd.DataFrame(all_data)
            df_all["deadline"]     = pd.to_datetime(df_all["deadline"],   utc=True, errors="coerce")
            df_all["created_at"]   = pd.to_datetime(df_all["created_at"], utc=True, errors="coerce")
            df_all["updated_at"]   = pd.to_datetime(df_all["updated_at"], utc=True, errors="coerce")
            df_all["deadline_ist"] = df_all["deadline"].dt.tz_convert(IST)

            # Vectorized — avoids the tz-aware/naive crash that .apply() causes
            df_all["diff_hours"] = (df_all["deadline_ist"] - now).dt.total_seconds() / 3600
            df_all["diff_days"]  = (df_all["diff_hours"] / 24).round()

            def deadline_indicator(row):
                if row["status"] == "resolved":
                    return "☑️ Resolved"
                if pd.isnull(row["diff_hours"]):
                    return "⚪ No deadline set"
                diff_hours = row["diff_hours"]
                days = int(row["diff_days"])
                if diff_hours < 0:
                    return f"🔴 Overdue by {abs(days)}d"
                elif diff_hours < 24:
                    return "🟠 Less than 1d left"
                else:
                    return f"🟢 {days}d left"

            df_all["deadline_status"] = df_all.apply(deadline_indicator, axis=1)
            df_all["deadline_fmt"]    = df_all["deadline_ist"].dt.strftime("%d %b %Y %H:%M IST")

            df_all["_sort_key"] = df_all.apply(
                lambda r: float("inf") if r["status"] == "resolved" else r["diff_hours"], axis=1
            )
            df_all = df_all.sort_values("_sort_key")

            st.dataframe(
                df_all[["id", "complaint_text", "department",
                        "priority", "status", "deadline_status", "deadline_fmt"]].rename(columns={
                    "id":              "ID",
                    "complaint_text":  "Complaint",
                    "department":      "Department",
                    "priority":        "Priority",
                    "status":          "Status",
                    "deadline_status": "⏰ Deadline Status",
                    "deadline_fmt":    "Deadline (IST)"
                }),
                use_container_width=True, hide_index=True
            )
        except Exception as e:
            st.warning(f"Could not display deadline table: {e}")
    else:
        st.info("No complaints found.")

    st.divider()

    # ── Average resolution time ───────────────────────────
    st.markdown("### ⏱️ Average Resolution Time by Department")

    if all_data:
        df_res = pd.DataFrame(all_data)
        df_res = df_res[df_res["status"] == "resolved"].copy()
        df_res["created_at"] = pd.to_datetime(df_res["created_at"], utc=True, errors="coerce")
        df_res["updated_at"] = pd.to_datetime(df_res["updated_at"], utc=True, errors="coerce")
        df_res = df_res.dropna(subset=["created_at", "updated_at"])

        if not df_res.empty:
            df_res["resolution_days"] = (
                df_res["updated_at"] - df_res["created_at"]
            ).dt.total_seconds() / 86400

            avg_res = df_res.groupby("department")["resolution_days"].mean().reset_index()
            avg_res.columns = ["Department", "Avg Days to Resolve"]
            avg_res["Avg Days to Resolve"] = avg_res["Avg Days to Resolve"].round(1)

            fig = px.bar(
                avg_res, x="Department", y="Avg Days to Resolve",
                color="Avg Days to Resolve",
                color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
                title="Average Days to Resolve per Department"
            )
            fig.add_hline(y=4, line_dash="dash", line_color="orange", annotation_text="4 day SLA target")
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(style_plotly_figure(fig), use_container_width=True, theme=None)
            st.dataframe(avg_res, use_container_width=True, hide_index=True)
        else:
            st.info("No resolved complaints with a recorded resolution time yet.")
    else:
        st.info("No data available.")