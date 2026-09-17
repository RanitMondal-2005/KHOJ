# Khoj — Missing Person & Unidentified Patient Coordination Platform

> A rule-based coordination platform connecting families and hospitals to help identify missing persons and unidentified hospital patients across districts.

## Live URL
https://khoj99.pythonanywhere.com/

---

## What is Khoj?

In India, thousands of missing person cases remain unresolved partly because families filing reports and hospitals admitting unidentified patients operate in complete isolation. There is no unified system connecting these two streams of data.

Khoj bridges this gap.

When a family files a missing person report and a hospital admits an unidentified patient, Khoj's matching engine automatically compares records across physical attributes, demographic markers, clothing, identifying marks, and facial recognition embeddings. When a potential match meets the 40% confidence threshold, both the family and the hospital receive real-time notifications with deep links to review the comparison.

### DISCLAIMER :
Khoj is not a replacement for FIR filing or official law enforcement systems; it serves as an investigative coordination and decision-support tool.

---

## Key Features

- Role-Based Portals — Dedicated dashboards, permissions, and views for two distinct stakeholders: Family and Hospital Staff.
- Automated Signal-Driven Matching — Rule-based scoring engine triggered asynchronously via post-save Django signals whenever a report or patient record is saved.
- Two-Stage Verification — Enforces strict hard filters (gender consistency and admission date feasibility) before computing weighted scores.
- Biometric Face Recognition (dlib) — End-to-end facial recognition pipeline extracting 128-dimensional biometric embeddings via ResNet and measuring Euclidean distance.
- Smart In-App Notifications —
  - 1-hour deduplication window preventing repetitive alert spam for the same match pair.
  - Native anchor deep-linking (#match-<id>) scrolling directly to the target match card.
  - Dynamic status sync: dismissed or inactive matches automatically grey out and disable action buttons across all dashboards.
- Privacy & Identity Protection — Hospital contact details and patient specifics remain restricted until an active match candidate is established.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Django |
| Database | SQLite |
| Frontend | Bootstrap 5.3, Bootstrap Icons, Django Templates |
| Computer Vision & ML | dlib, face_recognition_models, numpy, Pillow |
| Authentication | Custom user model with role-specific login backends |
| Architecture | Django Signals, Custom Anchor Deep-Linking, In-App Notifications |

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- C/C++ compiler and CMake (required for building dlib)
- pip & virtualenv

### 1. Clone the repository
git clone https://github.com/RanitMondal-2005/KHOJ.git
cd KHOJ

### 2. Create and activate a virtual environment
python3 -m venv venv

# Mac / Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
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

## User Roles & Login

Khoj provides distinct authentication entry points tailored to each operational role:

| Role | Login Identifier | Register Fields |
|------|-----------------|-----------------|
| Family | Email + Password | Full name, email, password |
| Hospital Staff | Staff ID + Password | Staff ID, hospital details, password |

---

## Role Capabilities

### Family
- File and manage up to 3 active missing person reports with photographs and physical descriptions.
- Add search updates, clues, and last-known locations to open cases.
- Receive instant match notifications linking directly to candidate patient cards.
- View hospital admission details, emergency contacts, and hospital-uploaded photos on match alerts.
- Dismiss false positives or mark cases as Found or Closed.

### Hospital Staff
- Register unidentified patients with mandatory photo documentation (facial front, full body, side profile).
- Document clothing details, estimated demographics, and physical traits.
- Receive alerts when an admitted patient matches an active missing person report.
- Review side-by-side comparison cards and verify identities or dismiss non-matches.
- Search and archive identified patient records.

---

## Project Structure

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
---

## How the Matching Engine Works

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

## Important Notes

- Khoj is a coordination and decision-support tool, not an official FIR registry.
- Always lodge a formal FIR with your local police jurisdiction for active missing person incidents.
- Sensitive identity attributes and hospital contact details are strictly revealed only when an active match candidate is established.

---

## License

This project is licensed under the MIT License.

---

## Authors

| Name | GitHub |
|------|--------|
| Ranit Mondal | [@RanitMondal-2005](https://github.com/RanitMondal-2005) |
| Biswajit Samanta | [@BiswajitSamanta](https://github.com/Biswajitsamanta1109) |

---

## Live Deployment
Visit the live platform at https://khoj99.pythonanywhere.com/
