import streamlit as st
import requests

API_URL = "http://localhost:3000"


def get_stage(status):
    s = (status or "").lower().strip()
    if s == "resolved":
        return 2
    if s in ("in progress", "in_progress", "processing", "under review"):
        return 1
    return 0


def render_tracker(stage):
    DONE    = "#138808"
    ACTIVE  = "#FF9933"
    PENDING = "#d1dae8"

    labels = ["Submitted", "Processing", "Resolved"]
    icons  = ["📋", "⚙️", "✅"]

    steps_html = ""
    for i in range(3):
        # ── Pre-compute every value — NO nested f-strings ──────────────────
        if i < stage:
            circle_bg    = DONE
            circle_inner = "✓"
            shadow       = "0 2px 8px rgba(0,0,0,0.10)"
            lbl_weight   = "600"
            lbl_color    = DONE
        elif i == stage:
            circle_bg    = ACTIVE
            circle_inner = icons[i]
            shadow       = "0 0 0 5px rgba(255,153,51,0.20), 0 4px 14px rgba(255,153,51,0.35)"
            lbl_weight   = "700"
            lbl_color    = ACTIVE
        else:
            circle_bg    = PENDING
            circle_inner = icons[i]
            shadow       = "0 1px 4px rgba(0,0,0,0.06)"
            lbl_weight   = "500"
            lbl_color    = "#94a3b8"

        label = labels[i]

        steps_html += (
            '<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;">'
            '<div style="width:52px;height:52px;border-radius:50%;'
            'background:' + circle_bg + ';color:#fff;'
            'display:flex;align-items:center;justify-content:center;'
            'font-size:1.3rem;font-weight:700;box-shadow:' + shadow + ';">'
            + circle_inner +
            '</div>'
            '<div style="font-size:.8rem;font-weight:' + lbl_weight + ';'
            'color:' + lbl_color + ';text-align:center;'
            'letter-spacing:.05em;text-transform:uppercase;">'
            + label +
            '</div>'
            '</div>'
        )

        # Connector line between steps
        if i < 2:
            line_color = DONE if i < stage else PENDING
            steps_html += (
                '<div style="flex:2;height:3px;border-radius:2px;'
                'background:' + line_color + ';align-self:center;margin-bottom:22px;"></div>'
            )

    return (
        '<div style="display:flex;align-items:flex-start;'
        'padding:2rem 1.5rem 1.5rem 1.5rem;'
        'background:#ffffff;border:1.5px solid #e8edf4;border-radius:16px;'
        'box-shadow:0 4px 20px rgba(15,37,71,0.07);margin-bottom:1.6rem;">'
        + steps_html +
        '</div>'
    )


def render():

    col_back, _ = st.columns([2, 8])
    with col_back:
        st.markdown('<div class="secondary-btn-container">', unsafe_allow_html=True)
        if st.button("← Back to Home", key="track_back_btn"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-wrap" style="padding:2rem 2.5rem;">
        <div class="hero-tag">🔍 GRIEVANCE TRACKING SYSTEM</div>
        <div class="hero-title" style="font-size:2.2rem;">
            Track Your <span>Complaint</span>
        </div>
        <p class="hero-sub">
            Enter your unique Complaint ID below to see real-time
            status and progress updates.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        cid = st.text_input(
            "Complaint ID",
            placeholder="e.g.  22",
            key="track_cid_input",
            label_visibility="collapsed"
        )
    with col_btn:
        search = st.button("🔍 Search", use_container_width=True,
                           key="track_search_btn")

    if search and cid:
        cid = cid.strip()
        try:
            r = requests.get(f"{API_URL}/complaints/{cid}", timeout=5)
        except Exception as e:
            st.error("Could not reach backend server: " + str(e))
            return

        if r.status_code == 404:
            st.error("No complaint found with ID #" + cid + ". Please check and try again.")
            return
        if r.status_code != 200:
            st.error("Server error (" + str(r.status_code) + "). Please try again later.")
            return

        data  = r.json()
        stage = get_stage(data.get("status", "pending"))

        # ── Section heading ──────────────────────────────────────────────
        ref_id = str(data.get("id", cid))
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;margin:1.4rem 0 .6rem 0;">'
            '<div style="height:28px;width:4px;border-radius:4px;'
            'background:linear-gradient(180deg,#FF9933,#138808);"></div>'
            '<h3 style="margin:0;font-family:Rajdhani,sans-serif;'
            'font-size:1.5rem;color:#0f2547;">Grievance Details</h3>'
            '<span style="margin-left:auto;font-family:Rajdhani,sans-serif;'
            'font-size:1.3rem;font-weight:700;color:#f59e0b;">'
            'Reference ID: #' + ref_id + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

        # ── Status tracker ───────────────────────────────────────────────
        st.markdown(render_tracker(stage), unsafe_allow_html=True)

        # ── Status badge values ──────────────────────────────────────────
        status_raw = (data.get("status") or "pending").lower()
        status_map = {
            "pending":     ("🟡", "Pending",     "#b45309", "#fffbeb", "#fef3c7"),
            "in progress": ("🔵", "In Progress", "#1d4ed8", "#eff6ff", "#bfdbfe"),
            "resolved":    ("🟢", "Resolved",    "#166534", "#f0fdf4", "#bbf7d0"),
        }
        badge_icon, badge_label, badge_text, badge_bg, badge_border = \
            status_map.get(status_raw, ("⚪", status_raw.title(), "#475569", "#f8fafc", "#e2e8f0"))

        priority_raw = (data.get("priority") or "medium").lower()
        pri_color = "#dc2626" if priority_raw == "high" else "#d97706"
        pri_bg    = "#fff1f2" if priority_raw == "high" else "#fffbeb"

        department   = data.get("department", "General")
        category     = (data.get("category") or "General").title()
        created_at   = str(data.get("created_at", ""))[:10]
        complaint_txt = data.get("complaint_text", "")

        # ── Details card ─────────────────────────────────────────────────
        st.markdown(
            '<div style="background:#ffffff;border:1.5px solid #e8edf4;'
            'border-radius:14px;padding:1.6rem 1.8rem;'
            'box-shadow:0 4px 18px rgba(15,37,71,0.07);margin-bottom:1.2rem;">'

            # badges
            '<div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;">'
            '<span style="display:inline-flex;align-items:center;gap:6px;'
            'background:' + badge_bg + ';border:1.5px solid ' + badge_border + ';'
            'color:' + badge_text + ';border-radius:99px;'
            'padding:.3rem .9rem;font-size:.82rem;font-weight:700;'
            'letter-spacing:.05em;text-transform:uppercase;">'
            + badge_icon + ' ' + badge_label + '</span>'

            '<span style="display:inline-flex;align-items:center;gap:6px;'
            'background:' + pri_bg + ';border:1.5px solid ' + pri_color + '33;'
            'color:' + pri_color + ';border-radius:99px;'
            'padding:.3rem .9rem;font-size:.82rem;font-weight:700;'
            'letter-spacing:.05em;text-transform:uppercase;">'
            '⚡ ' + priority_raw.title() + ' Priority</span>'
            '</div>'

            # grid
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:.9rem 2rem;">'

            '<div>'
            '<div style="font-size:.7rem;text-transform:uppercase;'
            'letter-spacing:.1em;color:#94a3b8;margin-bottom:3px;">Assigned Department</div>'
            '<div style="font-size:.97rem;font-weight:600;color:#0f2547;">' + department + '</div>'
            '</div>'

            '<div>'
            '<div style="font-size:.7rem;text-transform:uppercase;'
            'letter-spacing:.1em;color:#94a3b8;margin-bottom:3px;">Category</div>'
            '<div style="font-size:.97rem;font-weight:600;color:#0f2547;"> ' + category + '</div>'
            '</div>'

            '<div>'
            '<div style="font-size:.7rem;text-transform:uppercase;'
            'letter-spacing:.1em;color:#94a3b8;margin-bottom:3px;">Date Submitted</div>'
            '<div style="font-size:.97rem;font-weight:600;color:#0f2547;">' + created_at + '</div>'
            '</div>'

            '<div>'
            '<div style="font-size:.7rem;text-transform:uppercase;'
            'letter-spacing:.1em;color:#94a3b8;margin-bottom:3px;">Current Status</div>'
            '<div style="font-size:.97rem;font-weight:600;color:' + badge_text + ';">'
            + badge_icon + ' ' + badge_label + '</div>'
            '</div>'

            '</div>'  # end grid
            '</div>',  # end card
            unsafe_allow_html=True
        )

        # ── Complaint description ─────────────────────────────────────────
        st.markdown(
            '<div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;'
            'color:#94a3b8;margin-bottom:.5rem;">Citizen Description</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="background:#f8fafc;border:1.5px solid #e8edf4;'
            'border-left:4px solid #f59e0b;border-radius:10px;'
            'padding:1.1rem 1.3rem;font-size:.95rem;color:#1e293b;'
            'line-height:1.7;font-style:italic;margin-bottom:1.4rem;">'
            '"' + complaint_txt + '"'
            '</div>',
            unsafe_allow_html=True
        )

        # ── Image evidence ────────────────────────────────────────────────
        image_path = data.get("image_path")
        if image_path:
            st.markdown(
                '<div style="font-size:.7rem;text-transform:uppercase;'
                'letter-spacing:.1em;color:#94a3b8;margin-bottom:.5rem;">'
                'Attached Evidence</div>',
                unsafe_allow_html=True
            )
            st.image(f"{API_URL}/{image_path}",
                     caption="Evidence for Complaint #" + ref_id,
                     width=400)
        else:
            st.markdown(
                '<div style="background:#f8fafc;border:1.5px dashed #d1dae8;'
                'border-radius:10px;padding:1.2rem;text-align:center;'
                'color:#94a3b8;font-size:.88rem;margin-bottom:1.2rem;">'
                '📷 &nbsp; No photo evidence was attached with this complaint.'
                '</div>',
                unsafe_allow_html=True
            )

        # ── Bottom actions ────────────────────────────────────────────────
        colA, colB = st.columns(2)
        with colA:
            st.markdown('<div class="secondary-btn-container">', unsafe_allow_html=True)
            if st.button("← Back to Home", key="track_home_bottom",
                         use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with colB:
            st.markdown('<div class="citizen-btn-container">', unsafe_allow_html=True)
            if st.button("➕ File Another Complaint", key="track_new",
                         use_container_width=True):
                st.session_state.page = "user"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif search and not cid:
        st.warning("Please enter a Complaint ID before searching.")
        