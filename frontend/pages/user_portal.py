import streamlit as st
import requests
import io
import os
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

API_URL = "http://localhost:3000"

from utils.data import classify_complaint, DEPARTMENTS


def _register_devanagari_font():
    font_name = "LokSevaDevanagari"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    candidates = [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "Nirmala.ttc",
        Path("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf"),
    ]
    font_path = next((path for path in candidates if path.is_file()), None)
    if font_path is None:
        return "Helvetica"

    font = TTFont(font_name, str(font_path), subfontIndex=0, shapable=True)
    if not font.shapable:
        return "Helvetica"
    pdfmetrics.registerFont(font)
    return font_name


# ── PDF GENERATOR ────────────────────────────────────────────────────────────
def generate_complaint_pdf(name, phone, complaint_id, category, department,
                           priority, complaint_text, deadline):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    navy   = colors.HexColor("#0f2547")
    gold   = colors.HexColor("#f59e0b")
    light  = colors.HexColor("#f0f4f8")
    description_font = _register_devanagari_font()

    title_style = ParagraphStyle(
        "title", parent=styles["Title"],
        fontSize=20, textColor=navy, spaceAfter=4, alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER, spaceAfter=16
    )
    label_style = ParagraphStyle(
        "label", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#64748b"),
        fontName="Helvetica-Bold", spaceAfter=2
    )
    value_style = ParagraphStyle(
        "value", parent=styles["Normal"],
        fontSize=11, textColor=navy, spaceAfter=12,
        fontName="Helvetica"
    )
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#1e293b"),
        leading=16, spaceAfter=8, fontName=description_font
    )
    footer_style = ParagraphStyle(
        "footer", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER
    )

    story = []

    # Header
    story.append(Paragraph("🏛 LokSevaAI", title_style))
    story.append(Paragraph("Municipal Grievance Redressal Portal", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=gold, spaceAfter=16))
    story.append(Paragraph("<b>COMPLAINT RECEIPT</b>", ParagraphStyle(
        "receipt", parent=styles["Heading2"],
        fontSize=14, textColor=navy, alignment=TA_CENTER, spaceAfter=20
    )))

    # Token box
    token_table = Table(
        [[Paragraph(f"Complaint Token: <b>#{complaint_id}</b>",
                    ParagraphStyle("tok", parent=styles["Normal"],
                                   fontSize=16, textColor=gold,
                                   fontName="Helvetica-Bold",
                                   alignment=TA_CENTER))]],
        colWidths=["100%"]
    )
    token_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), navy),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [8]),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(token_table)
    story.append(Spacer(1, 20))

    # Details table
    data = [
        [Paragraph("Full Name", label_style),
         Paragraph(str(name), value_style)],
        [Paragraph("Contact Number", label_style),
         Paragraph(str(phone), value_style)],
        [Paragraph("Category", label_style),
         Paragraph(str(category).title(), value_style)],
        [Paragraph("Assigned Department", label_style),
         Paragraph(str(department), value_style)],
        [Paragraph("Priority Level", label_style),
         Paragraph(str(priority).upper(), value_style)],
        [Paragraph("SLA Deadline", label_style),
         Paragraph(str(deadline)[:19] if deadline else "N/A", value_style)],
    ]
    det_table = Table(data, colWidths=[5*cm, 13*cm])
    det_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), light),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, light]),
        ("GRID",          (0, 0), (-1, -1), .5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(det_table)
    story.append(Spacer(1, 16))

    # Complaint description
    story.append(Paragraph("Grievance Description", ParagraphStyle(
        "sec", parent=styles["Heading3"],
        fontSize=11, textColor=navy, fontName="Helvetica-Bold", spaceAfter=6
    )))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#e2e8f0"), spaceAfter=8))
    desc_table = Table(
        [[Paragraph(escape(str(complaint_text)).replace("\n", "<br/>"), body_style)]],
        colWidths=["100%"]
    )
    desc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), light),
        ("GRID",          (0, 0), (-1, -1), .5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 24))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor("#e2e8f0"), spaceAfter=8))
    story.append(Paragraph(
        "This is an automatically generated receipt from LokSevaAI – "
        "Municipal Corporation Grievance Portal. Please retain this for your records.",
        footer_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ── MAIN RENDER ──────────────────────────────────────────────────────────────
def render():
    col_back, col_space, col_track = st.columns([2, 5, 2.5])

    with col_back:
        st.markdown('<div class="secondary-btn-container">', unsafe_allow_html=True)
        if st.button("← Back to Home", key="portal_back_home_btn"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_track:
        st.markdown('<div class="track-btn-container">', unsafe_allow_html=True)
        if st.button("🔍 Track Complaint", key="track_complaint_top",
                     use_container_width=True):
            st.session_state.page = "track"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-tag">
            <i class="fa-solid fa-file-invoice" style="margin-right:6px;"></i>
            Citizen Portal
        </div>
        <div class="hero-title">File a <span>Grievance</span></div>
        <p class="hero-sub">
        Submit your civic issue below. Our AI system will automatically categorize
        and route your complaint to the appropriate department.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown(
            "<h3 style='color:var(--navy); margin-bottom:1rem;'>"
            "Complaint Registration Form</h3>",
            unsafe_allow_html=True
        )

        name     = st.text_input("Full Name *",
                                  placeholder="Enter your full name",
                                  key="portal_name_input")
        phone    = st.text_input("Mobile Number *",
                                  placeholder="10-digit mobile number",
                                  key="portal_phone_input")
        location = st.text_input("Location / Landmark / Area *",
                                  placeholder="e.g. Sector 4, near Main Market",
                                  key="portal_location_input")

        complaint_text = st.text_area(
            "Grievance Description *",
            placeholder="Please describe the issue in detail...",
            height=150,
            key="portal_text_input"
        )

        uploaded_image = st.file_uploader(
            "Attach Image Evidence (Optional, max 200MB)",
            type=["jpg", "jpeg", "png"],
            key="portal_image_uploader"
        )
        if uploaded_image:
            st.image(uploaded_image, width=280, caption="Preview of attached evidence")

        predicted_dept = None
        if complaint_text and len(complaint_text.strip()) > 10:
            predicted_dept = classify_complaint(complaint_text)
            st.markdown(f"""
            <div style="background:#f0fdf4; border:1px solid #bbf7d0;
                        border-radius:8px; padding:.8rem 1.2rem;
                        margin-top:1rem; color:#166534; font-size:.95rem;">
                🤖 <strong>AI Predicted Department:</strong> {predicted_dept}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="submit-btn-container">', unsafe_allow_html=True)
        submit = st.button("Submit Complaint →",
                           use_container_width=True, key="portal_submit_btn")
        st.markdown('</div>', unsafe_allow_html=True)

        if submit:
            if not name or not phone or not location or not complaint_text:
                st.error("Please fill in all required fields marked with *.")
                return

            files = {}
            if uploaded_image:
                files = {"image": (uploaded_image.name,
                                   uploaded_image.getvalue(),
                                   uploaded_image.type)}
            try:
                response = requests.post(
                    f"{API_URL}/complaints",
                    data={"complaint": complaint_text},
                    files=files
                )

                if response.status_code == 201:
                    data = response.json()
                    c = data["data"]
                    st.session_state["last_complaint"] = c
                    st.session_state["last_user_name"]  = name
                    st.session_state["last_user_phone"] = phone

                    st.success("✅ Complaint Submitted Successfully!")
                    st.markdown("---")

                    # ── Complaint receipt card ────────────────────────────
                    st.markdown(f"""
                    <div class="lk-card" style="border-left:5px solid var(--gold);">
                        <p style="margin:0; font-size:1rem; color:var(--navy);">
                            <strong>Complaint Registered Successfully</strong>
                        </p>
                        <p style="margin:.5rem 0; font-size:1.1rem; color:var(--gold);">
                            Complaint ID:
                            <span class="complaint-id">{c["id"]}</span>
                        </p>
                        <p style="margin:0; font-size:.95rem; color:var(--text-s);">
                            <strong>Assigned Department:</strong> {c["department"]}<br>
                            <strong>Priority:</strong> {c.get("priority","medium").upper()}<br>
                            <strong>SLA Deadline:</strong> {str(c.get("deadline","N/A"))[:19]}<br>
                            <strong>Status:</strong> 🟡 Pending Approval / Action
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── PDF Download ──────────────────────────────────────
                    st.markdown("### 📄 Download Complaint Receipt")
                    pdf_buf = generate_complaint_pdf(
                        name        = name,
                        phone       = phone,
                        complaint_id= c["id"],
                        category    = c.get("category", "General"),
                        department  = c.get("department", "General"),
                        priority    = c.get("priority", "medium"),
                        complaint_text = complaint_text,
                        deadline    = c.get("deadline", "N/A")
                    )
                    st.download_button(
                        label    = "⬇️ Download PDF Receipt",
                        data     = pdf_buf,
                        file_name= f"complaint_{c['id']}_receipt.pdf",
                        mime     = "application/pdf",
                        key      = "download_pdf_btn"
                    )

                    # ── Feedback form ─────────────────────────────────────
                    st.markdown("---")
                    st.markdown("### 💬 Share Your Feedback")
                    st.markdown(
                        "<p style='color:var(--text-s);font-size:.9rem;'>"
                        "Help us improve by rating your experience submitting this complaint."
                        "</p>",
                        unsafe_allow_html=True
                    )

                    rating = st.select_slider(
                        "Your Rating",
                        options=[1, 2, 3, 4, 5],
                        value=5,
                        format_func=lambda x: "⭐" * x,
                        key="feedback_rating"
                    )
                    feedback_text = st.text_area(
                        "Comments (optional)",
                        placeholder="Tell us about your experience...",
                        height=100,
                        key="feedback_text"
                    )

                    if st.button("Submit Feedback", key="submit_feedback_btn"):
                        try:
                            fb_resp = requests.post(
                                f"{API_URL}/feedback",
                                json={
                                    "complaint_id": c["id"],
                                    "rating":       rating,
                                    "comment":      feedback_text
                                }
                            )
                            if fb_resp.status_code == 201:
                                st.success("✅ Thank you for your feedback!")
                            else:
                                st.warning("Feedback could not be saved. Please try again.")
                        except:
                            st.warning("Could not reach the server to save feedback.")

                    # ── Bottom actions ────────────────────────────────────
                    st.markdown("<div style='height:10px;'></div>",
                                unsafe_allow_html=True)
                    colA, colB = st.columns(2)
                    with colA:
                        st.markdown('<div class="track-btn-container">',
                                    unsafe_allow_html=True)
                        if st.button("🔎 Track Complaint Status",
                                     key="track_complaint_bottom",
                                     use_container_width=True):
                            st.session_state.page = "track"
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with colB:
                        st.markdown('<div class="secondary-btn-container">',
                                    unsafe_allow_html=True)
                        if st.button("➕ File Another Grievance",
                                     key="submit_another_complaint",
                                     use_container_width=True):
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                elif response.status_code == 409:
                    res_data = response.json()
                    st.markdown(f"""
                    <div style="background:#fff1f2; border:1px solid #fecdd3;
                                border-radius:8px; padding:1rem; color:#9f1239;
                                margin-top:1rem; font-size:.95rem;">
                        <strong>⚠️ Duplicate Complaint Blocked:</strong>
                        A highly similar active complaint already exists under
                        ID <strong>{res_data.get('duplicate_id')}</strong>.
                    </div>
                    <div style="background:#fffbeb; border:1px solid #fef3c7;
                                border-radius:8px; padding:1rem; color:#b45309;
                                margin-top:.5rem; font-size:.95rem;">
                        <strong>Existing Complaint Text:</strong>
                        "{res_data.get('duplicate_text')}"
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Server Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Failed to connect to the backend server: {e}")

    with right:
        st.markdown("""
        <div class="lk-card">
            <h4 style="color:var(--navy); margin-bottom:.8rem; font-size:1.2rem;">
                📝 Guidelines for Citizens
            </h4>
            <ul style="margin:0; padding-left:1.2rem;
                       color:var(--text-s); font-size:.92rem; line-height:1.7;">
                <li>Identify the exact street name, landmark, or crossroad.</li>
                <li>Write details in clear English or Devanagari.</li>
                <li>An image attachment accelerates validation.</li>
                <li>Submit only one issue per complaint form.</li>
                <li>Keep your unique <strong>Complaint ID</strong> for checking progress.</li>
                <li>You can download a PDF receipt after submission.</li>
            </ul>
        </div>

        <div class="lk-card" style="margin-top:1.5rem;">
            <h4 style="color:var(--navy); margin-bottom:.8rem; font-size:1.2rem;">
                🏛 Supported Departments
            </h4>
            <ul style="margin:0; padding-left:1.2rem;
                       color:var(--text-s); font-size:.92rem; line-height:1.7;">
        """, unsafe_allow_html=True)
        for dept in DEPARTMENTS:
            st.markdown(
                f"<li style='color:var(--text-s); font-size:.9rem;'>{dept}</li>",
                unsafe_allow_html=True
            )
        st.markdown("</ul></div>", unsafe_allow_html=True)
        