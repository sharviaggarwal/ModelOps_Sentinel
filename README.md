# ModelOps Sentinel 🚨
[Live Demo](https://model-ops-sentinel-1cs8d0lvr-sharvi.vercel.app)

### An End-to-End MLOps Monitoring and AI-Powered Incident Investigation Platform

ModelOps Sentinel is an end-to-end MLOps platform designed to monitor machine learning models in production, detect data and prediction drift, track model health, and investigate incidents using an AI-powered agent with human-in-the-loop approval.

The platform combines machine learning, backend engineering, database management, monitoring systems, and agentic AI into one integrated application.

## 🚀 Key Features

- **Machine Learning Model:** Telco customer churn prediction using Logistic Regression.
- **Prediction API:** Serves real-time predictions through FastAPI.
- **Prediction Logging:** Stores prediction results in PostgreSQL.
- **Feature Drift Detection:** Monitors changes in incoming feature distributions.
- **Prediction Drift Detection:** Identifies changes in production prediction patterns.
- **Performance Monitoring:** Tracks model evaluation metrics.
- **Incident Management:** Detects and records monitoring incidents.
- **AI-Powered Investigation:** Uses an Ollama-powered LLM to investigate incidents.
- **Human-in-the-Loop (HITL):** Supports human approval before completing the investigation workflow.
- **Interactive Dashboard:** Displays model health, incidents, and investigation results.

## 🏗️ Architecture

```text
             Incoming Data
                   |
                   v
           FastAPI Backend
                   |
                   v
           ML Prediction Model
                   |
             Prediction Logs
                   |
                   v
             PostgreSQL
                   |
                   v
          Monitoring Engine
          /       |        \
         /        |         \
   Feature     Prediction   Performance
    Drift        Drift      Monitoring
         \        |         /
          \       |        /
             Incident
                |
                v
          AI Investigator
             (Ollama)
                |
                v
       Human Approval (HITL)
                |
                v
       Investigation Workflow
                |
                v
          React Dashboard


```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Machine Learning | Scikit-learn |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| AI / LLM | Ollama |
| Agentic Workflow | LangGraph |
| Frontend | React |
| Build Tool | Vite |
| API Testing | Swagger UI |

## 📊 Model Performance

The Logistic Regression model was trained on the Telco Customer Churn dataset.

| Metric | Test Score |
|---|---:|
| Accuracy | 74.10% |
| Precision | 50.77% |
| Recall | 78.88% |
| F1 Score | 61.78% |
| ROC-AUC | 84.21% |

## 🔍 Monitoring Capabilities

### 1. Feature Drift
Compares reference and production feature distributions to identify changes in incoming data.

### 2. Prediction Drift
Monitors changes in the distribution of model predictions.

### 3. Performance Monitoring
Tracks model performance using classification metrics.

### 4. Incident Management
Creates and tracks incidents when monitoring detects abnormal conditions.

## 🤖 AI-Powered Incident Investigation

ModelOps Sentinel integrates an AI investigator using Ollama and LangGraph.

The workflow:
1. Receives an incident ID.
2. Collects incident information.
3. Generates an AI-powered investigation report.
4. Pauses for human review.
5. Records the human decision.
6. Resumes the workflow after approval or rejection.

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/predict` | Generate churn prediction |
| GET | `/monitor/drift` | Feature drift monitoring |
| GET | `/monitor/predictions` | Prediction drift monitoring |
| GET | `/monitor/performance` | Model performance monitoring |
| GET | `/monitor/health` | Overall model health |
| GET | `/incidents` | Retrieve incidents |
| GET | `/incidents/{incident_id}` | Retrieve incident details |
| PATCH | `/incidents/{incident_id}/resolve` | Resolve an incident |
| POST | `/agent/investigate/{incident_id}` | Start AI investigation |
| POST | `/agent/approve/{thread_id}` | Submit human decision |

Interactive API documentation is available through Swagger UI.

## ⚙️ Local Setup

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL
- Ollama

### 1. Clone the repository

```bash
git clone https://github.com/sharviaggarwal/ModelOps_Sentinel.git
cd ModelOps-Sentinel
```

### 2. Backend setup

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing your database connection and other required configuration variables. Do not commit actual credentials.

Start the backend:

```bash
python -m uvicorn backend.api.main:app --reload
```

Backend documentation:

`http://127.0.0.1:8000/docs`

### 3. Start the frontend

Open another terminal:

```bash
cd dashboard
npm install
npm run dev
```

Open the local URL printed by Vite.

### 4. Start Ollama

Ensure Ollama is installed and the model used by the project is available locally.

```bash
ollama run llama3.2:3b
```

## 📁 Project Structure

```text
ModelOps-Sentinel/
│
├── backend/
│   └── api/
│       └── main.py
│
├── dashboard/
│   └── src/
│
├── README.md
├── requirements.txt
├── .env
└── .gitignore
```

*The structure above is a simplified overview; additional project modules and configuration files may exist.*

## 🎯 Project Objective

The objective of ModelOps Sentinel is to demonstrate how machine learning systems can be monitored beyond initial model training.

It focuses on production-oriented ML engineering concepts such as model observability, data drift detection, prediction monitoring, incident management, API development, database integration, and human-supervised AI workflows.

---

**Built as an end-to-end Machine Learning Operations project.**
