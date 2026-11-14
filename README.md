# 🏛️ LokSevaAI — Smart Civic Grievance Redressal System

<div align="center">

![LokSevaAI Banner](https://img.shields.io/badge/LokSevaAI-Smart%20Grievance%20System-0f2547?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-22-339933?style=flat-square&logo=nodedotjs&logoColor=white)](https://nodejs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF%20%2B%20SVC-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**An AI-powered municipal grievance redressal and management platform**  
**developed in collaboration with Kalyan-Dombivli Municipal Corporation (KDMC)**

[Features](#-features) · [Architecture](#-architecture) · [Setup](#-setup) · [API Reference](#-api-reference) · [ML Pipeline](#-ml-pipeline) · [Screenshots](#-screenshots)

</div>

---

## 🏆 Project Recognition

> **Certificate of Project Completion — KDMC/IT/388 · 02 November 2026**
>
> This project was completed in official collaboration with the **Kalyan-Dombivli Municipal Corporation (KDMC), Information & Technology Department**, Kalyan, Maharashtra.
---

## 📌 Overview

**LokSevaAI** is an end-to-end AI-powered civic grievance redressal platform built for the **Kalyan-Dombivli Municipal Corporation (KDMC)**. It replaces manual, paper-based complaint systems with an intelligent pipeline that:

- Accepts complaints in **English, Hindi, and Marathi**
- Automatically **classifies** them into the correct municipal department using a TF-IDF + LinearSVC ensemble
- **Assigns SLA deadlines** (2 days for high-priority, 4 days for standard)
- **Monitors breaches** in real time via a cron-based SLA engine
- Gives citizens a **downloadable PDF receipt** and live tracking
- Provides managers a **SLA compliance dashboard** with per-department analytics
---

## ✨ Features

### Citizen Portal
- 🗂️ Submit complaints in English, Hindi, or Marathi
- 🤖 Real-time AI department prediction before submission
- 📸 Optional image evidence upload
- 📄 Downloadable PDF receipt with Complaint Token, category, and SLA deadline
- 🔍 Live complaint tracking with Submitted → Processing → Resolved status stepper
- ⭐ Post-resolution feedback form

### Official Console
- 🔐 Role-based login (Admin / Manager)
- 📊 Department-wise bar charts and status pie charts
- ✏️ Update complaint status (Pending → In Progress → Resolved)
- 🚀 Escalation management

### SLA Monitoring Dashboard
- 📈 Real-time metrics: Total / Active / Resolved / On Track / At Risk / Breached
- 🏢 Department-wise compliance percentage charts
- 🔔 Auto-breach alerts with 24-hour at-risk warnings
- ⬇️ CSV compliance report export
- ⏱️ Average resolution time per department
- 🔄 Auto-refresh every 5 minutes

### ML System
- 🌐 Multilingual support: English + Hindi (Devanagari + Romanised) + Marathi
- 🔑 Three-layer classification: Compound phrase rules → Keyword rules → ML model
- 📉 Confusion matrix and F1-score charts generated on every training run
- 🔁 Duplicate complaint detection via Jaccard similarity

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CITIZEN / OFFICIAL                       │
│                    Browser → localhost:8501                     │
│                     Python · Streamlit                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────────┐
│                       BACKEND API                               │
│                   Node.js · Express · :3000                     │
│  Complaint CRUD · SLA cron · Auth · Image upload (Multer)       │
└───────────────────┬──────────────────────────┬──────────────────┘
                    │ SQL                       │ HTTP
┌───────────────────▼──────────┐  ┌────────────▼──────────────────┐
│        PostgreSQL 17         │  │       ML SERVICE              │
│      Database · :5432        │  │  Python · Flask · :5000       │
│  complaints · users          │  │  TF-IDF + LinearSVC Ensemble  │
│  feedback · sla_config       │  │  Hindi · Marathi · English    │
└──────────────────────────────┘  └───────────────────────────────┘
```

**Port Map**

| Service | Technology | Port |
|---|---|---|
| Frontend | Python / Streamlit | 8501 |
| Backend API | Node.js / Express | 3000 |
| ML Service | Python / Flask | 5000 |
| Database | PostgreSQL 17 | 5432 |

---


## 🤖 ML Pipeline

### Classification System — Three-Layer Architecture

```
Complaint Text (any language)
        │
        ▼
┌───────────────────────────────────┐
│ Layer 1: Marathi Phrase Match     │  "नाल्याची सफाई" → Sewage (exact match)
│ Layer 2: Drain Anchor Rule        │  nala + safai → Sewage (not Solid Waste)
│ Layer 3: Compound Regex Patterns  │  "power cut" regex → Electric
└───────────────────────────────────┘
        │ No rule matched
        ▼
┌───────────────────────────────────┐
│  Multilingual Preprocessing       │
│  Hindi Devanagari expansion       │
│  Marathi inflection map           │
│  Romanised transliteration        │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  TF-IDF Feature Engineering       │
│  Word bigrams  (1,2) max 12,000   │
│  Char n-grams  (3,5) max  8,000   │  handles typos: SEPITC→SEPTIC
│  sublinear_tf=True                │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│  Soft Voting Ensemble             │
│  60% LinearSVC + 40% LogReg       │
└───────────────────────────────────┘
        │
        ▼
   Predicted Department
```

### Departments (6 canonical classes after label cleaning)

| Department Key | Department Name |
|---|---|
| `streetlight` | Electric Department |
| `water` | Water Supply Department |
| `sewage` | Sewage & Drainage Department |
| `road` | Road & Traffic Management Department |
| `garbage` | Solid Waste Management |
| `encroachment` | Encroachment Department |

### Model Performance

| Metric | Score |
|---|---|
| Overall Accuracy | ~93–95% (after label cleaning + ensemble) |
| Weighted F1 | ~0.93 |
| Sewage → Solid Waste cross-errors | Reduced from 23 → <5 via drain anchor rule |

> Training generates `metrics_bar_chart.png`, `confusion_matrix.png`, and `evaluation_metrics.json` automatically.

---

---

---

## 📁 Project Structure

```
lok-seva-ai/
├── backend/
│   ├── config/
│   │   └── db.js                   # PostgreSQL connection
│   ├── controllers/
│   │   └── complaintController.js  # Complaint CRUD + SLA exports + Feedback
│   ├── routes/
│   │   └── complaintRoutes.js      # All API routes
│   ├── services/
│   │   └── slaService.js           # SLA check, summary, alerts
│   ├── uploads/                    # Image evidence storage
│   └── server.js                   # Express server + cron job
│
├── ml-service/
│   ├── preprocess.py               # Multilingual NLP pipeline
│   ├── predict.py                  # Three-layer classification
│   ├── train.py                    # Model training + evaluation
│   ├── app.py                      # Flask prediction API
│   ├── extract_disputed.py         # Boundary complaint extractor
│   ├── retrain_from_reviewed.py    # Post-review retraining
│   ├── benchmark_tracker.py        # Metric history tracker
│   ├── model.pkl                   # Trained ensemble model
│   └── vectorizer.pkl              # Fitted TF-IDF vectorizer
│
├── frontend/
│   ├── app.py                      # Streamlit router
│   ├── utils/
│   │   ├── styles.py               # CSS theme injection
│   │   ├── auth.py                 # Role-based auth
│   │   └── data.py                 # Department map + classifier
│   └── pages/
│       ├── home.py                 # Landing page (KDMC branding)
│       ├── login.py                # Portal secure access
│       ├── user_portal.py          # Complaint submission + PDF
│       ├── track_complaint.py      # Status stepper
│       ├── manager_dashboard.py    # Operations console
│       ├── admin_dashboard.py      # Admin analytics
│       └── sla_dashboard.py        # SLA monitoring
│
├── database/
│   ├── schema.sql                  # Base tables
│   └── schema_sla_update.sql       # SLA columns + config table
│
└── dataset/
    └── kdmc_data.xlsx              # Real KDMC complaint data
```

---

## 🔄 SLA Engine

The backend runs a cron job every 60 seconds that:

1. Marks active complaints past their deadline as **Breached**
2. Marks complaints within 24 hours of deadline as **At Risk**
3. Auto-escalates complaints pending for more than 7 days

```javascript
// server.js
cron.schedule("*/1 * * * *", () => {
  checkSLA();  // → slaService.js
});
```

---

## 🌐 Multilingual Support

| Language | Input Format | Handling |
|---|---|---|
| English | Plain text | Direct TF-IDF |
| Hindi | Devanagari script | Keyword expansion map (100+ entries) |
| Hindi | Romanised (bijli, paani, kachra) | Transliteration map (40+ phrases) |
| Marathi | Devanagari script | Phrase dictionary + inflection map |
| Marathi | Mixed script | Marathi grammatical marker detection |

No external translation API is used — the entire pipeline runs offline with zero latency.

---

## 🤝 Collaboration

This project was developed in official collaboration with:

<div align="center">

**Kalyan-Dombivli Municipal Corporation (KDMC)**  
Information & Technology Department  
Kalyan, Maharashtra — India

*Certificate No. KDMC/IT/388 · Dated 02/11/2026*  
*Signed by Pramod Kamble, System Analyst, KDMC*

</div>

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---


<div align="center">
 
**K.J. Somaiya Institute of Technology · AI & Data Science · 2026**

</div>
