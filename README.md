# 🚀 Lok Seva AI

Lok Seva AI is an AI-based complaint classification and routing system designed to automate grievance handling in public service systems. The system uses machine learning to analyze user complaints and automatically assign them to the appropriate department. It also stores complaint data in a PostgreSQL database for tracking and management.

---


## 🏗️ System Architecture

```
Citizen
   │
   ▼
Streamlit Frontend
   │
   ▼
Node.js + Express Backend
   │
   ├────────► PostgreSQL Database
   │
   ▼
Machine Learning Model
(TF-IDF + Scikit-Learn)
   │
   ▼
Department Prediction
Priority Prediction
Complaint Routing
```

---

# 🧠 Machine Learning Pipeline

```
Complaint Text
        │
        ▼
Text Cleaning
        │
        ▼
TF-IDF Vectorization
        │
        ▼
Trained ML Model
        │
        ▼
Department Prediction
        │
        ▼
Priority Classification
        │
        ▼
Complaint Stored in PostgreSQL
```

Model evaluation results and the practical plan for improving accuracy are in
[ml-service/ACCURACY_ROADMAP.md](./ml-service/ACCURACY_ROADMAP.md).

---

# 📊 Workflow

1. User submits complaint
2. Complaint is sent to backend
3. ML model predicts department
4. Priority is determined
5. Complaint is stored in PostgreSQL
6. User receives complaint ID
7. Complaint can be tracked later

---

# 🎯 Use Cases

- Municipal Corporationss
- Smart City Platforms
- Government Grievance Portals
- University Complaint Systems
- Corporate Internal Helpdesks


# 📌 Features

- 🧠 AI-based complaint classification using TF-IDF and Machine Learning
- 📂 Automatic routing of complaints to relevant departments
- 🗄️ PostgreSQL database integration for data storage
- 🔗 REST API built using Node.js and Express
- 🖥️ Streamlit-based frontend for user interaction
- ⚡ Fast predictions using pre-trained ML model

---

# 🏗️ Tech Stack

### Backend
- Node.js
- Express.js

### ML Service
- Python
- Flask
- Scikit-learn
- TF-IDF Vectorization

### Database
- PostgreSQL

### Frontend
- Streamlit (Python)

---

# 📁 Project Structure


lok-seva-ai/
│
├── backend/ # Node.js API
├── frontend/ # Streamlit frontend
├── ml-service/ # Python ML service
├── database/ # Database schema
├── dataset/ # Training dataset
├── docs/ # Documentation/screenshots
│
├── .env.example # Environment variables sample
├── .gitignore # Ignored files
├── README.md # Project documented


---

# ⚙️ Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/lok-seva-ai.git
cd lok-seva-ai
2️⃣ Setup Backend
cd backend
npm install

Create a .env file inside the backend folder:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=lokseva
DB_USER=postgres
DB_PASSWORD=yourpassword

Run backend server:

node server.js
3️⃣ Setup PostgreSQL Database
Create Database
CREATE DATABASE lokseva;
Run Schema File
psql -U postgres -d lokseva -f database/schema.sql
4️⃣ Setup ML Service
cd ml-service
pip install -r requirements.txt

Run ML service:

python app.py
5️⃣ Run Frontend (Streamlit)
cd frontend
pip install -r requirements.txt (if any)
streamlit run app.py
