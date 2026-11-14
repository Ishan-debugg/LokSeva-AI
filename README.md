# 🏛️ LokSevaAI — Smart Civic Grievance Redressal System

**An AI-powered municipal grievance redressal platform developed in collaboration with Kalyan-Dombivli Municipal Corporation (KDMC).**

---

## 🏆 Project Recognition

**Certificate of Project Completion — KDMC/IT/388 · 02 November 2026**

This project was completed in official collaboration with the **Kalyan-Dombivli Municipal Corporation (KDMC), Information & Technology Department**, Kalyan, Maharashtra.

---

## 📌 Overview

LokSevaAI is an end-to-end civic grievance redressal platform built for KDMC. It replaces manual, paper-based complaint handling with an intelligent pipeline that:

- Accepts complaints in **English, Hindi, and Marathi**
- Automatically **classifies** complaints into the correct municipal department using a TF-IDF + LinearSVC ensemble
- **Assigns SLA deadlines** (2 days for high priority, 4 days for standard)
- **Monitors breaches** in real time through a cron-based SLA engine
- Gives citizens a **downloadable PDF receipt** and live tracking
- Provides managers an **SLA compliance dashboard** with per-department analytics

---

## ✨ Features

### 👥 Citizen Portal
- 🗂️ Submit complaints in English, Hindi, or Marathi
- 🤖 Real-time AI department prediction before submission
- 📸 Optional image evidence upload
- 📄 Downloadable PDF receipt with Complaint Token, category, and SLA deadline
- 🔍 Live tracking with a Submitted → Processing → Resolved status stepper
- ⭐ Post-resolution feedback form

### 🛠️ Official Console
- 🔐 Role-based login (Admin / Manager)
- 📊 Department-wise bar charts and status pie charts
- ✏️ Status updates (Pending → In Progress → Resolved)
- 🚀 Escalation management

### 📈 SLA Monitoring Dashboard
- Real-time metrics: Total / Active / Resolved / On Track / At Risk / Breached
- Department-wise compliance percentage charts
- Breach alerts with 24-hour at-risk warnings
- CSV compliance report export
- Average resolution time per department
- Auto-refresh every 5 minutes

### 🧠 ML System
- Multilingual support: English, Hindi (Devanagari and Romanised), and Marathi
- Three-layer classification: phrase rules → keyword rules → ML model
- Confusion matrix and F1-score charts generated on every training run
- Duplicate complaint detection via Jaccard similarity

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────┐
│ CITIZEN / OFFICIAL │
│ Browser → localhost:8501 │
│ Python · Streamlit │
└──────────────────────────────┬──────────────────────────────────┘
│ REST API
┌──────────────────────────────▼──────────────────────────────────┐
│ BACKEND API │
│ Node.js · Express · :3000 │
│ Complaint CRUD · SLA cron · Auth · Image upload (Multer) │
└───────────────────┬──────────────────────────┬──────────────────┘
│ SQL │ HTTP
┌───────────────────▼──────────┐ ┌────────────▼──────────────────┐
│ PostgreSQL 17 │ │ ML SERVICE │
│ Database · :5432 │ │ Python · Flask · :5000 │
│ complaints · users │ │ TF-IDF + LinearSVC Ensemble │
│ feedback · sla_config │ │ Hindi · Marathi · English │
└──────────────────────────────┘ └───────────────────────────────┘


**Port Map**

| Service | Technology | Port |
|---|---|---|
| Frontend | Python / Streamlit | 8501 |
| Backend API | Node.js / Express | 3000 |
| ML Service | Python / Flask | 5000 |
| Database | PostgreSQL 17 | 5432 |

---

## 🤖 ML Pipeline

### Classification Flow
Complaint Text (any language)
│
▼
┌───────────────────────────────────┐
│ Layer 1: Marathi Phrase Match │ "नाल्याची सफाई" → Sewage
│ Layer 2: Drain Anchor Rule │ nala + safai → Sewage (not Solid Waste)
│ Layer 3: Compound Regex Patterns │ “power cut” → Electric
└───────────────────────────────────┘
│ No rule matched
▼
┌───────────────────────────────────┐
│ Multilingual Preprocessing │
│ Hindi Devanagari expansion │
│ Marathi inflection map │
│ Romanised transliteration │
└───────────────────────────────────┘
│
▼
┌───────────────────────────────────┐
│ TF-IDF Feature Engineering │
│ Word bigrams (1,2) max 12,000 │
│ Char n-grams (3,5) max 8,000 │ handles typos: SEPITC → SEPTIC
│ sublinear_tf = True │
└───────────────────────────────────┘
│
▼
┌───────────────────────────────────┐
│ Soft Voting Ensemble │
│ 60% LinearSVC + 40% LogReg │
└───────────────────────────────────┘
│
▼
Predicted Department


### Departments

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
| Overall Accuracy | ~93–95% (after label cleaning and ensemble) |
| Weighted F1 | ~0.93 |
| Sewage → Solid Waste cross-errors | Reduced from 23 to under 5 via drain anchor rule |

> Training generates `metrics_bar_chart.png`, `confusion_matrix.png`, and `evaluation_metrics.json` automatically.

---

## 🌐 Multilingual Support

| Language | Input Format | Handling |
|---|---|---|
| English | Plain text | Direct TF-IDF |
| Hindi | Devanagari script | Keyword expansion map (100+ entries) |
| Hindi | Romanised (bijli, paani, kachra) | Transliteration map (40+ phrases) |
| Marathi | Devanagari script | Phrase dictionary + inflection map |
| Marathi | Mixed script | Marathi grammatical marker detection |

No external translation API is used. The pipeline runs fully offline.

---

## 📁 Project Structure
lok-seva-ai/
├── backend/
│ ├── config/
│ │ └── db.js # PostgreSQL connection
│ ├── controllers/
│ │ └── complaintController.js # Complaint CRUD, SLA exports, feedback
│ ├── routes/
│ │ └── complaintRoutes.js # All API routes
│ ├── services/
│ │ └── slaService.js # SLA check, summary, alerts
│ ├── uploads/ # Image evidence storage
│ └── server.js # Express server + cron job
│
├── ml-service/
│ ├── preprocess.py # Multilingual NLP pipeline
│ ├── predict.py # Three-layer classification
│ ├── train.py # Model training and evaluation
│ ├── app.py # Flask prediction API
│ ├── extract_disputed.py # Boundary complaint extractor
│ ├── retrain_from_reviewed.py # Post-review retraining
│ ├── benchmark_tracker.py # Metric history tracker
│ ├── model.pkl # Trained ensemble model
│ └── vectorizer.pkl # Fitted TF-IDF vectorizer
│
├── frontend/
│ ├── app.py # Streamlit router
│ ├── utils/
│ │ ├── styles.py # CSS theme injection
│ │ ├── auth.py # Role-based auth
│ │ └── data.py # Department map and classifier
│ └── pages/
│ ├── home.py # Landing page (KDMC branding)
│ ├── login.py # Portal secure access
│ ├── user_portal.py # Complaint submission and PDF
│ ├── track_complaint.py # Status stepper
│ ├── manager_dashboard.py # Operations console
│ ├── admin_dashboard.py # Admin analytics
│ └── sla_dashboard.py # SLA monitoring
│
├── database/
│ ├── schema.sql # Base tables
│ └── schema_sla_update.sql # SLA columns and config table
│
└── dataset/
└── kdmc_data.xlsx # KDMC complaint data


---

## 📸 Screenshots

| Home Page (KDMC Portal) | SLA Monitoring Dashboard |
|---|---|
| ![Home](docs/screenshots/home.png) | ![SLA](docs/screenshots/sla_dashboard.png) |

| Complaint PDF Receipt | Live Status Tracker |
|---|---|
| ![PDF](docs/screenshots/pdf_receipt.png) | ![Tracker](docs/screenshots/status_tracker.png) |

| Admin Analytics Dashboard |
|---|
| ![Admin](docs/screenshots/admin_dashboard.png) |

---

## 🤝 Collaboration

**Kalyan-Dombivli Municipal Corporation (KDMC)**
Information & Technology Department · Kalyan, Maharashtra, India

*Certificate No. KDMC/IT/388 · Dated 02/11/2026*
*Signed by Pramod Kamble, System Analyst, KDMC*

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
