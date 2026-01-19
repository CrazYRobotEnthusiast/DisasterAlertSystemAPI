# 🚨 High-Reliability Disaster Alert System

A professional, SOLID-compliant alerting system designed to dispatch real-time emergency notifications with high throughput, safety, and observability.

## 🌟 Key Features
- **SOLID Architecture:** Strictly decoupled layers (Interfaces, Infrastructure, Domain, Application).
- **Reliability:** Background multi-threaded workers using a task queue to handle high traffic without blocking the API.
- **Safety:** Automatic contact deduplication to prevent spamming users across overlapping disaster regions.
- **Observability:** Real-time telemetry via Prometheus and a pre-configured Grafana Dashboard.
- **Security:** Admin-only access with persistent session authentication.

---

## 🛠️ Prerequisites
- **Python 3.10+**
- **Docker & Docker Compose** (For Prometheus & Grafana)
- **Twilio Account** (For SMS dispatching)

---

## 🚀 Installation & Setup

### 1. Clone & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your Twilio credentials:
```env
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_MESSAGING_SERVICE_SID=your_service_sid_here
```

### 3. Initialize the Database
This script creates the SQLite tables and inserts dummy admins and regional recipients.
```bash
python setup_db.py
```

---

## 🏃 Running the System

### Step 1: Start the API Server
This starts the Flask server and the background `AlertWorker` thread.
```bash
python app.py
```
*The API will be available at `http://localhost:5000`.*

### Step 2: Start the Monitoring Stack (Docker)
Ensure your Docker Desktop is running, then execute:
```bash
docker-compose up -d
```
- **Grafana:** `http://localhost:3000` (Login: admin/admin)
- **Prometheus:** `http://localhost:9090`

### Step 3: Run the Comprehensive Test
This script simulates logins (success/fail), regional alerts, and high-traffic bursts to populate the dashboard.
```bash
python test_api.py
```

---

## 🏗️ Project Structure (SOLID)
- **`interfaces.py`**: Abstract Base Classes (Contracts). Ensures the system depends on abstractions, not implementations (DIP).
- **`infrastructure.py`**: Concrete adapters for SQLite, Twilio, and Authentication.
- **`domain.py`**: Core Business Logic. Handles deduplication logic and background worker orchestration.
- **`metrics.py`**: Centralized Prometheus instrumentation.
- **`app.py`**: Flask Application Layer & Composition Root.
- **`monitoring/`**: Configuration files for automated Grafana provisioning.

---

## 📊 Dashboard Visuals
Once `test_api.py` completes, open Grafana to see:
- **Regional Distribution:** A bar chart showing alert volume per city.
- **Success Rate:** A gauge tracking Twilio API reliability.
- **Queue Backlog:** Real-time view of tasks waiting for the worker.
- **Latency Trend:** End-to-end processing time for emergency requests.

---

## ⚠️ Safety Warnings
- **Twilio Credits:** Sending alerts to real numbers will consume Twilio credits. 
- **API Security:** The `app.secret_key` should be changed for production deployments.
- **Database:** `setup_db.py` will wipe existing data to ensure a clean state for testing.

---
*Developed for the Group 1 Disaster Alert System Project.*