# Khoj — Missing Person & Unidentified Patient Coordination Platform

> A rule-based coordination platform connecting families, hospitals, and police to help resolve missing person cases across districts.

## Live URL :
..............
---

## What is Khoj?

In India, thousands of missing person cases remain unresolved partly because families filing reports and hospitals admitting unidentified patients operate in complete isolation. There is no shared system connecting these two pieces of information.

**Khoj bridges this gap.**

When a family files a missing person report and a hospital admits an unidentified patient, Khoj's matching engine automatically compares the two records across physical attributes, location, clothing, identifying marks, and even photo similarity — then notifies the relevant parties if a potential match is found.

Khoj is **not** a replacement for FIR filing or official police systems. It is a coordination and investigation support tool.

---

## Key Features

- **Role-based access** — Three distinct roles (Family, Hospital, Police) each with their own dashboard and permissions
- **Automatic matching** — Rule-based confidence scoring engine triggered via Django signals on every new report or patient record
- **Score breakdown** — Every match shows exactly which factors contributed and how many points each scored
- **Photo similarity** — Perceptual hashing (imagehash) compares uploaded photos as a bonus scoring factor
- **In-app notifications** — Family and hospital users are notified when a potential match is found
- **Photo sliders** — Each role sees the other party's photos (not their own) on match pages
- **Investigation support** — Police can browse regional unidentified patients, explore matches, and find hospital contacts in their district
- **Privacy-conscious** — Hospital contact details are only revealed to families when a valid match exists. Only last 4 digits of any found ID are stored.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django & Python |
| Database | SQLite |
| Frontend | Bootstrap 5.3 + Django Templates |
| Image Comparison | imagehash + Pillow |
| Auth | Custom user model with email/ID-based login |
| Notifications | In-app only (no email/SMS) |

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/RanitMondal-2005/KHOJ.git
cd KHOJ
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py makemigrations accounts
python manage.py makemigrations family
python manage.py makemigrations hospital
python manage.py makemigrations matching
python manage.py makemigrations notifications
python manage.py migrate
```

### 5. Create a superuser *(for Django admin panel only)*

```bash
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## User Roles & Login

Khoj has three roles. Each role has a **separate login page** with a different identifier.

| Role | Login With | Register With |
|------|-----------|---------------|
| Family | Email + Password | Full name, email, password |
| Hospital Staff | Staff ID + Password | Staff ID, hospital details, password |
| Police Officer | Police ID + Password | Police ID, station details, password |

---

## Role Capabilities

### Family
- File up to **3 active** missing person reports with photos
- Include Aadhaar number, relation to missing person, and filer contact
- Add private search updates and clues to their case
- View potential matches with full patient details and hospital contact
- See **hospital's 3 uploaded photos** on match page (not their own)
- Receive in-app notifications when a match is found
- Mark cases as Found or Closed

### Hospital Staff
- Upload unidentified patient records with **3 required photos** (face, full body, side profile)
- Record clothing description and any ID found on the person (last 4 digits only)
- View match alerts showing family's full report details and contact
- See **family's 2 uploaded photos** on match page (not their own)
- Search resolved/identified patients by name
- Mark patients as identified

### Police Officer
- Browse **unidentified patient records** uploaded by hospitals in their district
- View full patient detail page with photo slider (hospital's 3 photos)
- Explore nearby matches between missing persons and patients with full score breakdown
- Search hospital directory for contact information
- View archived (identified) patients in their district
- **Read-only access** — cannot modify any records

---

## Project Structure

```
KHOJ/
├── KHOJ/                   # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/               # Custom user model + registration/login for all 3 roles
│   ├── models.py           # KhojUser, HospitalProfile, PoliceProfile
│   ├── forms.py            # Registration + role-specific login forms
│   ├── views.py            # Login choice, register, dashboard redirect
│   └── backends.py         # Email / StaffID / PoliceID auth backends
│
├── family/                 # Missing person reports
│   ├── models.py           # MissingPerson, CaseUpdate
│   ├── forms.py            # MissingPersonForm with validation
│   └── views.py
│
├── hospital/               # Unidentified patient records
│   ├── models.py           # UnidentifiedPatient (with clothing + found ID fields)
│   ├── forms.py
│   └── views.py
│
├── police/                 # Investigation support (read-only)
│   └── views.py            # Shows hospital patient records in district
│
├── matching/               # The core of Khoj
│   ├── engine.py           # Rule-based scoring engine (the heart of the project)
│   ├── models.py           # MatchResult with score_breakdown JSONField
│   └── signals.py          # Auto-triggers matching on every save
│
├── notifications/          # In-app notifications
│   ├── models.py
│   ├── utils.py            # Creates notifications after matching
│   └── context_processors.py
│
├── templates/              # All HTML templates (Bootstrap 5)
├── static/css/             # khoj.css
├── media/                  # Uploaded photos (auto-created at runtime)
└── requirements.txt
```

---

## How the Matching Engine Works

The matching engine (`matching/engine.py`) is the **heart of Khoj**.

Every time a missing person report or unidentified patient record is saved, Django signals automatically trigger the engine. It compares every active missing person against every unidentified patient and stores matches that score above the threshold (default: 40%).

### Scoring Breakdown

| Factor | Max Points | Logic |
|--------|-----------|-------|
| Gender | 20 | Exact match required |
| Blood Group | 15 | Exact match required |
| Age | 15 | ±3 yrs = 15, ±6 = 10, ±10 = 5 |
| Height | 10 | ±5 cm = 10, ±10 = 6, ±15 = 3 |
| District | 10 | Same district = full points |
| Identifying Marks | 10 | Keyword overlap (Jaccard similarity) |
| Clothing Description | 10 | Keyword overlap (Jaccard similarity) |
| Photo Similarity | 10 | Perceptual hash distance (imagehash) |
| Weight | 5 | ±5 kg = 5, ±10 = 3 |
| Eye Color | 5 | Exact text match |
| Hair Color | 5 | Exact text match |
| Skin Tone | 5 | Exact match |
| **Total (capped)** | **100** | |

Every match stores a `score_breakdown` JSON field so the dashboard can show exactly which factors contributed — making the system fully transparent and explainable.

### Photo Similarity
Photo comparison uses **perceptual hashing** (not facial recognition). Each image is converted to a compact hash based on its visual structure. Similar-looking images produce similar hashes with small hash distances.

```
Distance 0     → +10 pts  (identical or near-identical)
Distance 1–5   → +7 pts   (very similar)
Distance 6–10  → +4 pts   (somewhat similar)
Distance 11–15 → +1 pt    (slight similarity)
Distance > 15  → 0 pts    (too different)
```

---

## Important Notes

- Khoj is a **coordination support tool only** — not an official government or police system
- Always file a proper **FIR** with your local police station for missing person cases
- Khoj does **not** verify institutional IDs through external systems — stored for future integration
- Police officers on Khoj have **read-only access** — they cannot modify any records
- Hospital contact details are **only visible to families** when a valid match exists
- Django admin (`/admin/`) is for developer/database inspection only

---

## License

This project is licensed under the **MIT License** — anyone can use, copy, modify, and distribute this code for free, as long as they give credit to the original authors.

---

## Authors

| Name | GitHub |
|------|--------|
| Ranit Mondal | [@RanitMondal-2005](https://github.com/RanitMondal-2005) |
| Biswajit Samanta | [@BiswajitSamanta](https://github.com/Biswajitsamanta1109) |