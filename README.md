# 🛡️ FraudGuard Transaction Monitoring Dashboard

<p align="center">
  <img src="assets/logo.png" width="140" alt="FraudGuard Logo">
</p>

<p align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/fraudguard-dashboard)
![GitHub Actions](https://github.com/YOUR_USERNAME/fraudguard-dashboard/actions/workflows/report.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Status](https://img.shields.io/badge/status-Production-success)

</p>

---

## 🚀 Live Demo

🌐 **Dashboard**

https://YOUR_USERNAME.github.io/fraudguard-dashboard/

---

# Dashboard Preview

## Main Dashboard

![Dashboard](assets/dashboard.png)

## Analytics

![Analytics](assets/analytics.png)

## Transaction History

![History](assets/history.png)

---

# Overview

FraudGuard is a lightweight real-time transaction monitoring dashboard designed for fraud analysts and financial institutions.

The platform visualises transaction activity, fraud predictions, analyst overrides, and system health using interactive charts and live reports generated automatically by Python.

The dashboard is built with **HTML, CSS and Vanilla JavaScript**, while automated reporting is handled using **Python** and **GitHub Actions**, making it deployable as a completely static website through GitHub Pages.

---

# Features

✅ Real-time transaction monitoring

✅ Risk score classification

✅ Fraud decision tracking

✅ Analyst override management

✅ Daily transaction analytics

✅ Interactive charts

✅ System health monitoring

✅ CSV export

✅ Automatic report generation

✅ GitHub Actions automation

✅ GitHub Pages deployment

---

# Screenshots

| Dashboard                 | Transactions            |
| ------------------------- | ----------------------- |
| ![](assets/dashboard.png) | ![](assets/history.png) |

| Reports                | Analytics                 |
| ---------------------- | ------------------------- |
| ![](assets/report.png) | ![](assets/analytics.png) |

---

# Technology Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Chart.js

### Backend Automation

* Python
* Requests
* JSON

### Deployment

* GitHub Pages
* GitHub Actions

---

# Project Structure

```text
fraudguard-dashboard/
│
├── .github/
│   └── workflows/
│       └── report.yml
│
├── assets/
│   ├── dashboard.png
│   ├── analytics.png
│   ├── history.png
│   └── report.png
│
├── css/
│   └── style.css
│
├── js/
│   └── dashboard.js
│
├── data/
│   └── reports.json
│
├── reports/
│
├── logs/
│
├── generate_report.py
├── run_report.py
├── requirements.txt
├── render.yaml
├── index.html
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/fraudguard-dashboard.git

cd fraudguard-dashboard
```

Install dependencies

```bash
pip install -r requirements.txt
```

Generate report data

```bash
python run_report.py
```

Start a local server

```bash
python -m http.server 8000
```

Open

```
http://localhost:8000
```

---

# Automated Reporting

Reports are generated automatically using Python.

The automation:

* Retrieves transaction information
* Calculates fraud statistics
* Generates JSON reports
* Updates dashboard data
* Publishes changes using GitHub Actions

---

# GitHub Actions

Every scheduled workflow automatically:

* Generates the latest report
* Commits updated JSON files
* Pushes changes to GitHub
* Deploys the latest dashboard to GitHub Pages

---

# Dashboard Modules

### Transaction Feed

Monitor recent transactions with:

* Risk Score
* Decision
* Status
* Override History

---

### Risk Distribution

Visual breakdown of:

* Low Risk
* Medium Risk
* High Risk
* Critical Risk

---

### System Health

Monitor

* API Status
* Accuracy
* Latency
* Active Analysts
* Alerts
* Uptime

---

### Reports

Automatically generated daily reports including

* Total Transactions
* Approval Rate
* Fraud Detection Rate
* Analyst Performance
* Daily Trends

---

# Deployment

This project is deployed using

* GitHub Pages
* GitHub Actions

Every workflow execution updates the live dashboard automatically.

---

# Future Improvements

* User authentication
* Role-based access control
* Dark mode
* Real-time WebSocket updates
* PDF reporting
* Email alerts
* Machine Learning dashboard

---

# Author

**Marvin Vutshila**

Computer Science Student

Fraud Detection & Machine Learning Enthusiast

GitHub:

https://github.com/YOUR_USERNAME

---

# License

This project is licensed under the MIT License.
