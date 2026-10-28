# 🔍 Khoj (खोज)(খোঁজ)
### Missing Person & Unidentified Patient Coordination Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![dlib](https://img.shields.io/badge/dlib-ResNet--128d-blue?style=flat-square)](http://dlib.net/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Demo-Live_Deployment-success?style=flat-square)](https://khoj99.pythonanywhere.com/)

An automated, signal-driven decision-support platform designed to bridge information silos between families filing missing person reports and hospitals admitting unidentified patients across districts.

[Live Platform](https://khoj99.pythonanywhere.com/) • [Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Matching Engine](#-how-the-matching-engine-works) • [Installation](#-installation--setup) • [References](#-technical-references)

---

> **⚠️ Disclaimer:**
> **Khoj is not a substitute for an official First Information Report (FIR) or law enforcement investigation systems.** It serves as an investigative decision-support and coordination system to assist families and healthcare institutions in expediting identity verification.

---

## 📌 Problem Overview

In India, missing-person reports and unidentified hospital patient records can remain disconnected across families and healthcare institutions. This separation can make it difficult to identify potential connections between missing individuals and patients admitted without identification.

- **Families** file missing person reports with local police stations or search informally across social groups.
- **Hospitals** admit trauma victims, amnesia cases, or unconscious patients as "Unknown / Unidentified" with internal logs that rarely cross district or institutional boundaries.

**Khoj** unifies these disparate data streams into a single event-driven coordination pipeline. When a report or admission is logged, a multi-stage scoring engine pairs physical attributes, clothing descriptions, temporal feasibility, and deep biometric facial embeddings to notify both parties in real time.

---

## ✨ Key Features

- **Role-Based Access Control (RBAC):** Tailored operational portals with dedicated authentication backends, permissions, and dashboards for **Families** and **Hospital Staff**.
- **Signal-Driven Scoring Pipeline:** Asynchronous post-save Django hooks trigger match calculations on every new case or patient update without manual polling.
- **Two-Stage Candidate Filtering:** Eliminates logically impossible candidate pairs through strict hard-gate checks (gender consistency and admission date feasibility) before computing computational scores.
- **Biometric Facial Recognition:** Deep metric learning pipeline computing Euclidean distance on 128-dimensional facial feature vectors extracted via ResNet.
- **Smart Notification Engine:**
  - **1-Hour Deduplication Window:** Suppresses redundant alerts for repeated updates on the same candidate pair.
  - **Anchor Deep-Linking (`#match-<id>`):** Directs users straight to the target candidate comparison card from notification payloads.
  - **Active State Synchronization:** Closed, resolved, or dismissed candidate matches automatically update and disable action triggers across all linked dashboards.
- **Privacy by Design:** Hospital operational details and patient data are masked until a verified match threshold is satisfied.

---

## 🏗 System Architecture & Workflow :

## 📂 Project Structure (Overview)

```text
KHOJ/
├── KHOJ/                   # Project settings, URL routing, WSGI
├── accounts/               # Custom user model & role authentication backends
├── family/                 # Missing person case filing & case updates
├── hospital/               # Unidentified patient admission & records
├── matching/               # Algorithmic engine, signal handlers & MatchResult model
│   ├── engine.py           # Core rule-based matching & scoring calculations
│   ├── models.py           # MatchResult (PENDING / VERIFIED / REJECTED)
│   └── signals.py          # Post-save hooks triggering matching checks
├── notifications/          # In-app notification pipeline & active-state sync
│   ├── models.py           # Notification model with related_match_id
│   ├── utils.py            # Deduplication & automated dispatch logic
│   └── views.py            # Active state synchronization & batch reads
├── templates/              # Bootstrap 5 responsive UI templates
├── static/                 # CSS stylesheets and UI assets
└── requirements.txt        # Python dependencies

```
---

## 🧠 How the Matching Engine Works

The matching engine (`matching/engine.py`) runs automatically whenever a missing person or an unidentified patient record is saved.

### 1. Hard Filters (Logical Impossibility Checks)
Before computing any scores, the engine evaluates two mandatory gates:
- **Gender Match:** Strict check (`missing.gender == patient.gender`). Mismatches are skipped immediately.
- **Date Feasibility:** A patient admitted *before* the missing date represents an impossibility (`patient.admission_date >= missing.last_seen_date`). Pairs failing this check are eliminated with zero evaluation.

### 2. Weighted Factor Scoring (100 Points Total)
Pairs passing both hard filters are scored across 11 distinct attributes:

| Factor | Max Points | Evaluation Logic |
|--------|-----------|------------------|
| Face Similarity (dlib) | 30 | Euclidean distance of 128-d ResNet embeddings: <=0.30 (30 pts), <=0.45 (22 pts), <=0.60 (14 pts) |
| Identifying Marks | 15 | Jaccard similarity index on normalized keyword tokens (excluding stopwords) |
| Age Similarity | 15 | Difference margin: <=3 yrs (15 pts), <=6 yrs (10 pts), <=10 yrs (5 pts) |
| Height Similarity | 12 | Difference margin: <=5 cm (12 pts), <=10 cm (8 pts), <=15 cm (4 pts) |
| Clothing Overlap | 10 | Jaccard similarity index on clothing description tokens (excluding stopwords) |
| Blood Group | 5 | Exact match required (excludes UNKNOWN) |
| District Proximity | 5 | Exact district match |
| Weight Similarity | 4 | Difference margin: <=5 kg (4 pts), <=10 kg (2 pts) |
| Skin Tone | 2 | Exact match (excludes UNKNOWN) |
| Eye Color | 1 | Exact text match (case-insensitive) |
| Hair Color | 1 | Exact text match (case-insensitive) |
| **Total Available** | **100** | **Match Threshold: >= 40 pts** |

Candidate pairs meeting or exceeding the 40-point threshold generate or update a `MatchResult` record containing an itemized `score_breakdown` JSON field for complete diagnostic transparency.

---

## 👥 Role Capabilities

### 👨‍👩‍👧 Family
- File and manage up to 3 active missing person reports with photographs and physical descriptions.
- Add search updates, clues, and last-known locations to open cases.
- Receive instant match notifications linking directly to candidate patient cards.
- View hospital admission details, emergency contacts, and hospital-uploaded photos on match alerts.
- Dismiss false positives or mark cases as Found or Closed.

### 🏥 Hospital Staff
- Register unidentified patients with mandatory photo documentation (facial front, full body, side profile).
- Document clothing details, estimated demographics, and physical traits.
- Receive alerts when an admitted patient matches an active missing person report.
- Review side-by-side comparison cards and verify identities or dismiss non-matches.
- Search and archive identified patient records.

---

## 🔑 Authentication

Khoj provides distinct authentication entry points tailored to each operational role:

| Role | Login Identifier | Register Fields |
|------|-----------------|-----------------|
| Family | Email + Password | Full name, email, password |
| Hospital Staff | Staff ID + Password | Staff ID, hospital details, password |

---

## 🛠 Tech Stack

| Domain | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Django 6.2+ |
| **Database** | SQLite (Development / Demo) |
| **Frontend UI** | Bootstrap 5.3, Bootstrap Icons, Django Template Engine |
| **Computer Vision & ML** | `dlib`, `face_recognition_models`, `numpy`, `Pillow` |
| **Architecture Patterns** | Event-driven Django Signals, Role-Based Access Control (RBAC), Custom Auth Backends |

---

## 🚀 Setup & Installation

Follow these steps to run KHOJ locally.
### Prerequisites
- Python 3.10 or higher
- C/C++ compiler and CMake (required for building dlib)
- pip & virtualenv

Note: dlib installation requirements depend on the operating system, Python version, and available prebuilt packages.

### 1. Clone the repository
git clone https://github.com/RanitMondal-2005/KHOJ.git
cd KHOJ

### 2. Create and activate a virtual environment
python3 -m venv venv

### Mac / Linux:
source venv/bin/activate

### Windows (Command Prompt):
venv\Scripts\activate

### Windows (PowerShell):
venv\Scripts\Activate.ps1

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run migrations
python manage.py makemigrations accounts family hospital matching notifications
python manage.py migrate

### 5. Create a superuser (optional, for Django admin)
python manage.py createsuperuser

### 6. Start the development server
python manage.py runserver

Visit http://127.0.0.1:8000 in your browser.

---

## ⚙️ Configuration & Deployment

- Before deploying KHOJ or adapting it for production, review the following:
- Keep SECRET_KEY and other sensitive configuration values out of version control.
- Set DEBUG = False in production.
- Configure ALLOWED_HOSTS for the intended deployment domains.
- Configure HTTPS and secure session and CSRF settings.
- Ensure that uploaded photographs and patient records have appropriate access - restrictions.
- Review role-based permissions for sensitive information.-
- Configure database backups, logging, and error monitoring.
- Verify database migrations, media storage, and dependency compatibility in the target environment.

The local development configuration should not automatically be considered production-ready.
---


## 📚 Technical References

The following resources document the libraries and models underlying KHOJ's facial-recognition implementation.

### dlib

#### 1.[dlib Face Recognition Example](http://dlib.net/face_recognition.py.html)
Demonstrates face recognition and face-descriptor comparison using dlib.

#### 2.[dlib Python API Documentation](http://dlib.net/python/index.html)
Reference documentation for dlib's Python API and computer-vision functionality.

### Face Recognition Models & Implementation

#### 3.[face_recognition_models](https://github.com/ageitgey/face_recognition_models)
GitHub Repository containing pretrained models used by the face_recognition ecosystem.

#### 4.[face_recognition](https://github.com/ageitgey/face_recognition)
Reference implementation of the face-recognition library, including face_recognition/api.py, which contains face-encoding and comparison functionality.

These resources describe the underlying libraries and models. KHOJ's eligibility filters, weighted scoring rules, candidate threshold, and notification workflow are application-level logic.

---

## 🔒 Privacy & Responsible Use

- KHOJ handles potentially sensitive information, including missing-person - reports, patient photographs, physical characteristics, and hospital admission - details.
- The platform is designed to support coordination and investigation, not replace - official procedures.
- No automatic identity confirmation: A score above the threshold indicates a - potential candidate, not proof of identity.
- Human verification: Candidate matches should be reviewed using available - evidence and appropriate verification procedures.
- Official reporting: Families should report missing-person incidents to the - appropriate police authorities and follow official procedures.
- Access control: Sensitive information should be available only to authorized - users with a legitimate need.
- Biometric limitations: Facial-recognition results may contain false positives or - false negatives.
- Responsible data handling: Personal information and photographs should be handled in accordance with applicable privacy and data-protection requirements.

## 🚩Important Notes

- Khoj is a coordination and decision-support tool, not an official FIR registry.
- Always lodge a formal FIR with your local police jurisdiction for active missing person incidents.
- Sensitive identity attributes and hospital contact details are strictly revealed only when an active match candidate is established.

---

## 👨‍💻 Authors

| Name | GitHub |
|------|--------|
| Ranit Mondal | [@RanitMondal-2005](https://github.com/RanitMondal-2005) |
| Biswajit Samanta | [@BiswajitSamanta](https://github.com/Biswajitsamanta1109) |

---

## 📄 License
This project is licensed under the MIT License.
See the LICENSE file for details.
---

## 🌐 Live Deployment
Visit the live platform at https://khoj99.pythonanywhere.com/
