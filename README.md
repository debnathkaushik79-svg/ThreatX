# ThreatX

## ML-Based Cybersecurity Threat Detection & Network Intrusion Monitoring System

ThreatX is an end-to-end machine-learning-based cybersecurity monitoring system that analyzes network traffic, detects potential threats, classifies attack categories, assigns security severity, and visualizes security events through an interactive dashboard.

The system combines **machine learning, feature engineering, REST APIs, database persistence, traffic simulation, and a web-based monitoring dashboard** into a single cybersecurity workflow.

---

## Overview

ThreatX processes network traffic through a two-stage machine learning pipeline:

1. **Stage 1 — Threat Detection**

   * Determines whether network traffic is **Normal** or an **Attack**.

2. **Stage 2 — Attack Classification**

   * If an attack is detected, the system classifies it into a specific attack category.

3. **Security Analysis**

   * Assigns a severity level based on the detected attack category.

4. **Monitoring & Storage**

   * Stores traffic and security events in PostgreSQL.

5. **Visualization**

   * Displays network activity, threats, alerts, attack distribution, and recent predictions through the ThreatX dashboard.

---

## System Architecture

```mermaid
flowchart TD
    A[Network Traffic] --> B[FastAPI Backend]

    B --> C[Feature Engineering]

    C --> D[Stage 1<br/>Binary Classification]

    D -->|Normal| E[Normal Traffic]

    D -->|Attack| F[Stage 2<br/>Attack Classification]

    F --> G[Attack Category]

    G --> H[Severity Analysis]

    E --> I[(PostgreSQL)]
    H --> I

    I --> J[ThreatX Dashboard]

    J --> K[Traffic Analytics]
    J --> L[Threat Analytics]
    J --> M[Attack Distribution]
    J --> N[Security Alerts]
    J --> O[Recent Traffic]
```

---

## Machine Learning Pipeline

```mermaid
flowchart LR
    A[UNSW-NB15 Dataset] --> B[Data Preparation]
    B --> C[Feature Engineering]
    C --> D[Train / Validation Split]

    D --> E[Stage 1 Model]
    E --> F[Normal / Attack]

    F -->|Attack| G[Stage 2 Model]
    G --> H[Attack Category]

    F -->|Normal| I[Normal Traffic]

    H --> J[Severity Assignment]
    I --> K[Traffic Log]
    J --> K

    K --> L[PostgreSQL]
    L --> M[Dashboard]
```

---

## Key Features

### 🔍 Machine Learning Threat Detection

* Binary classification of network traffic
* Normal vs Attack detection
* Attack category classification
* Prediction confidence
* Feature engineering for network-flow behavior

### 🛡️ Security Monitoring

* Real-time traffic simulation
* Continuous ML prediction
* Attack detection
* Attack category identification
* Severity-based security alerts
* Recent traffic monitoring

### 📊 Security Dashboard

* Total traffic statistics
* Detected threat statistics
* Normal vs attack distribution
* Critical alert count
* Traffic activity timeline
* Threat activity timeline
* Attack category distribution
* Alert severity summary
* Recent security alerts
* Recent ML predictions

### 🗄️ Data Persistence

ThreatX stores important monitoring information in PostgreSQL, including:

* Traffic predictions
* Attack categories
* Prediction confidence
* Protocol
* Service
* Network state
* Security alerts
* Alert severity
* Alert descriptions
* Timestamps

---

## Attack Categories

The attack-classification pipeline supports categories represented in the UNSW-NB15 dataset, including:

* Generic
* Exploits
* Fuzzers
* DoS
* Reconnaissance
* Analysis
* Backdoor
* Shellcode
* Worms

---

## Threat Severity Classification

ThreatX converts detected attack categories into security severity levels.

| Severity | Categories                 |
| -------- | -------------------------- |
| Critical | DoS, Backdoor, Shellcode   |
| High     | Exploits, Fuzzers, Generic |
| Medium   | Reconnaissance, Analysis   |
| Low      | Other categories           |

This provides an additional security-analysis layer between machine-learning predictions and dashboard alerts.

---

## Feature Engineering

ThreatX creates additional behavioral features from the original network-flow attributes.

Examples include:

* Bytes per packet
* Packet rate
* Total bytes
* Total packets
* Byte ratio
* Packet ratio
* Load ratio
* Load difference
* Total packet loss
* Loss ratio
* Packet interval ratio
* Jitter ratio
* Mean packet difference
* Mean packet ratio
* TCP handshake time
* TTL difference
* TCP window difference
* Total handshake time

The feature-engineering process is shared between model development and backend inference to maintain consistency between training and prediction.

---

## Model Performance

### Stage 1 — Binary Threat Detection

Validation results:

| Metric    |  Score |
| --------- | -----: |
| Accuracy  | 97.41% |
| Precision | 98.20% |
| Recall    | 97.07% |
| F1 Score  | 97.63% |

Evaluation on the UNSW-NB15 test split:

| Metric    |  Score |
| --------- | -----: |
| Accuracy  | 90.96% |
| Precision | 98.70% |
| Recall    | 87.87% |
| F1 Score  | 92.97% |

### Stage 2 — Attack Classification

Validation results:

| Metric             |  Score |
| ------------------ | -----: |
| Accuracy           | 80.48% |
| Weighted Precision | 80.12% |
| Weighted Recall    | 80.48% |
| Weighted F1 Score  | 79.70% |

These metrics document the performance of the current experimental models and provide a baseline for further model improvement.

---

## Prediction Workflow

A prediction request follows this flow:

```mermaid
sequenceDiagram
    participant D as Dashboard
    participant A as FastAPI
    participant F as Feature Engineering
    participant M1 as Stage 1 Model
    participant M2 as Stage 2 Model
    participant DB as PostgreSQL

    D->>A: Send network traffic
    A->>F: Prepare features
    F-->>A: Engineered features

    A->>M1: Normal / Attack prediction
    M1-->>A: Prediction + confidence

    alt Normal
        A->>DB: Store traffic log
    else Attack
        A->>M2: Classify attack
        M2-->>A: Category + confidence
        A->>A: Assign severity
        A->>DB: Store traffic + alert
    end

    A-->>D: Return prediction result
```

---

# Dashboard

## Dashboard Overview

![ThreatX Dashboard](screenshots/dashboard-overview.png)

The main dashboard provides a centralized view of network traffic, detected threats, normal traffic, active alerts, and monitoring status.

## Live Monitoring

![ThreatX Live Monitoring](screenshots/monitoring_live.png)

The live monitoring interface allows the traffic simulation to continuously send network records through the ML pipeline.

## Traffic Activity

![Traffic Activity](screenshots/traffic_activity.png)

The traffic activity section provides a timeline-based view of recent network activity.

## Threat Activity

![Threat Activity](screenshots/threat_activity.png)

Threat activity visualizes detected attack categories across the monitoring timeline.

## Security Alerts

![Security Alerts](screenshots/security_alerts.png)

The security-alert section organizes detected threats according to their assigned severity.

## Recent Alerts

![Recent Alerts](screenshots/recent_alerts.png)

Recent security events are displayed with attack type, severity, confidence, protocol, service, and network state.

## Recent Traffic

![Recent Traffic](screenshots/recent_traffic.png)

The recent traffic section displays the latest machine-learning predictions and their associated network information.

---

# REST API

ThreatX uses FastAPI to expose the machine-learning and monitoring functionality through REST endpoints.

| Method | Endpoint                 | Description                           |
| ------ | ------------------------ | ------------------------------------- |
| GET    | `/`                      | API status                            |
| GET    | `/api/health`            | Health check                          |
| POST   | `/api/predict`           | Analyze network traffic               |
| GET    | `/api/traffic`           | Retrieve traffic records              |
| GET    | `/api/alerts`            | Retrieve security alerts              |
| GET    | `/api/statistics`        | Retrieve dashboard statistics         |
| GET    | `/api/analytics`         | Retrieve traffic and threat analytics |
| POST   | `/api/simulation/start`  | Start traffic simulation              |
| POST   | `/api/simulation/stop`   | Stop traffic simulation               |
| GET    | `/api/simulation/status` | Retrieve simulation status            |

---

# Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Browser APIs

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy

## Machine Learning

* Python
* NumPy
* Pandas
* Scikit-learn
* Joblib

## Database

* PostgreSQL
* SQLAlchemy

## Dataset

* UNSW-NB15

## Development Tools

* Git
* GitHub
* VS Code
* Python Virtual Environment

---

# Project Structure

```text
ThreatX/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── model_service.py
│   └── simulator_service.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── ml/
│   ├── feature_engineering.py
│   └── ...
│
├── data/
│   ├── UNSW_NB15_training-set.csv
│   └── UNSW_NB15_testing-set.csv
│
├── models/
│   ├── targeted_feature_engineered_rf.pkl
│   └── hierarchical_attack_classifier.pkl
│
├── docs/
│
├── screenshots/
│   ├── dashboard-overview.png
│   ├── monitoring_live.png
│   ├── traffic_activity.png
│   ├── threat_activity.png
│   ├── security_alerts.png
│   ├── recent_alerts.png
│   └── recent_traffic.png
│
├── tests/
│
├── .gitignore
├── .python-version
├── requirements.txt
└── README.md
```

> The trained model files are excluded from Git source tracking because of their size and are distributed separately through GitHub Releases.

---

# Dataset

ThreatX uses the **UNSW-NB15** dataset for machine-learning development and traffic simulation.

The dataset contains network-flow attributes representing normal network behavior and multiple categories of malicious traffic.

The dataset is intentionally excluded from Git tracking because of its size.

Expected local files:

```text
data/
├── UNSW_NB15_training-set.csv
└── UNSW_NB15_testing-set.csv
```

---

# Installation & Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/debnathkaushik79-svg/ThreatX.git
cd ThreatX
```

## 2. Create a Virtual Environment

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure PostgreSQL

Create a `.env` file in the project root:

```env
DATABASE_URL=your_postgresql_connection_string
```

Keep database credentials private and never commit `.env` to GitHub.

## 5. Download the ML Models

Download the required trained models from the project's GitHub Releases and place them inside:

```text
models/
```

Required files:

```text
models/
├── targeted_feature_engineered_rf.pkl
└── hierarchical_attack_classifier.pkl
```

## 6. Start the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

## 7. Start the Frontend

Serve the `frontend` directory using a local development server such as VS Code Live Server.

Example:

```text
http://127.0.0.1:5501
```

Open the dashboard and select **Start Monitoring** to begin the traffic simulation.

---

# Model Management

Large trained models are maintained separately from the source-code repository.

Current model release:

**v1.0-models**

Required model files:

```text
targeted_feature_engineered_rf.pkl
hierarchical_attack_classifier.pkl
```

This approach keeps the Git repository focused on source code, configuration, documentation and project assets while allowing the trained models to be versioned independently.

---

# Engineering Highlights

ThreatX demonstrates several software-engineering and machine-learning concepts in one project:

* End-to-end ML inference pipeline
* Hierarchical classification architecture
* Reusable feature-engineering module
* FastAPI REST API design
* PostgreSQL database integration
* SQLAlchemy ORM
* Backend-driven dashboard statistics
* Automated traffic simulation
* Security alert generation
* Severity-based threat analysis
* Prediction confidence tracking
* Modular frontend JavaScript
* Environment-variable-based configuration
* Git-based version control
* Separate versioning of large ML artifacts

---

# Future Enhancements

The current architecture provides a foundation for extending ThreatX into a more advanced network-security platform.

Planned enhancement areas include:

### 🔬 Machine Learning

* Advanced ensemble models
* XGBoost-based experiments
* Improved handling of minority attack classes
* Hyperparameter optimization
* Cross-validation experiments
* Model comparison and benchmarking
* Explainable AI using SHAP

### 🌐 Network Monitoring

* Live network packet capture
* Network-interface integration
* Streaming traffic ingestion
* WebSocket-based real-time updates
* Extended protocol-level analysis

### 📊 Security Analytics

* Advanced historical analytics
* Threat filtering and search
* Attack trend analysis
* Custom time-range reports
* Security event correlation
* Automated security reports

### 🔐 Platform Features

* JWT-based authentication
* Role-based access control
* User-specific dashboards
* Alert acknowledgement and management
* Model version management
* Audit logging

### ⚙️ Infrastructure

* Docker containerization
* Production-oriented database configuration
* Scalable inference architecture
* Background task processing
* Cloud deployment on infrastructure sized for ML workloads

These enhancements provide a clear path from the current academic/portfolio implementation toward a more scalable cybersecurity monitoring platform.

---

# Project Objective

ThreatX was developed to explore how **machine learning and software engineering can be combined to build a practical cybersecurity monitoring workflow**.

The project brings together:

```text
Network Dataset
      ↓
Data Preparation
      ↓
Feature Engineering
      ↓
Machine Learning
      ↓
Threat Detection
      ↓
Attack Classification
      ↓
Severity Analysis
      ↓
Database
      ↓
REST API
      ↓
Security Dashboard
```

The project demonstrates the integration of **ML models, backend services, databases, APIs, simulation, and frontend visualization** into a complete application.

---

# Author

**Kaushik Debnath**

B.Tech Computer Science & Engineering

---

# License

This project is developed for educational, academic, portfolio, and research purposes.
