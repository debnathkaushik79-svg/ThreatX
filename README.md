# ThreatX

## ML-Based Cybersecurity Threat Detection and Network Intrusion Monitoring System

ThreatX is a machine-learning-based cybersecurity application that detects malicious network traffic, classifies detected attacks, generates security alerts, and displays network security activity through a web-based dashboard.

The system uses the **UNSW-NB15 dataset** and a **two-stage machine learning pipeline** for network intrusion detection.

---

## Features

- Network traffic threat detection
- Normal vs Attack classification
- Attack category classification
- Machine learning confidence score
- Automatic security alert generation
- Threat severity classification
- Real-time traffic simulation
- Network traffic monitoring dashboard
- Attack distribution analytics
- Threat activity timeline
- Recent traffic and security alerts
- PostgreSQL database for storing traffic and alerts
- REST API using FastAPI
- Interactive web dashboard using HTML, CSS and JavaScript
- Light/Dark theme

---

## How ThreatX Works

ThreatX uses a two-stage machine learning architecture.

```text
Network Traffic
       |
       v
Feature Engineering
       |
       v
+----------------------+
| Stage 1              |
| Binary Classification|
+----------------------+
       |
       +------------------+
       |                  |
       v                  v
    Normal              Attack
                          |
                          v
                 +------------------+
                 | Stage 2          |
                 | Attack           |
                 | Classification   |
                 +------------------+
                          |
                          v
                  Attack Category
