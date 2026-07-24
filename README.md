# KCET Predictor & Option Entry Simulator Portal (2026 Edition)

An enterprise-grade, high-performance web portal designed for students, counselors, and institutions to simulate, audit, and forecast Karnataka Common Entrance Test (KCET) engineering seat allotments. 

---

## 🚀 Key Features

* **🔮 Rank Predictor with ML-Based YoY Trend Forecasts**: Compares candidate UGCET rank against three years of official round cutoffs (2024, 2025, 2026) and flags YoY stream demand indexes (`🔥 Tightening` vs `📉 Easing` vs `➡️ Stable`).
* **👥 Counselor Student Session Manager**: Enables advisors to create, swap, and delete candidate portfolios in real-time, saving unique choices checklists and preferences.
* **⚡ Choice List Optimizer & Volatility Auditor**: Scans prioritized choice entries to warn against out-of-order sequence blockages, calculates the annual tuition fee budget, and provides a one-click sequence optimizer.
* **💰 Quota-Based Tuition Fee Calculator**: Computes itemized university and college fees dynamically by Quota (KEA Govt, Aided, SNQ, COMEDK, Management) and Year of Study.
* **⚖️ Side-by-Side College Comparison Matrix**: Visualizes structural features, Est. Year, NAAC grades, NBA accreditation status, placement rate/averages, hostel fee schedules, and transit accessibility metrics side-by-side for up to 3 colleges.
* **📋 Sub-Category Reservation Drawer**: Toggles the official 33 sub-category seat matrix splits (General, Rural, Kannada, HK 371-J) and special reservations (NCC, Sports, Defense, PH) directly inside course rows.
* **📥 High-Contrast Data Download Portal**: Allows administrators to export custom filtered matrices and cutoff closing ranks by year and college group in high-contrast CSV or JSON.
* **📈 Interactive Analytics Dashboard**: Displays interactive **Sunburst Charts** (hierarchical streams to branches breakdown) and **Sankey Flow Diagrams** (KEA seats flowing from source pools to reservation categories and specializations) with real-time center-node tooltips.

---

## 🛠️ Technology Stack
* **Frontend**: Vanilla JavaScript (ES6+), HTML5 Semantic markup, Custom CSS3, and raw SVG math-driven vector graphs (no external dependencies).
* **Backend API**: FastAPI, Python 3.11, Uvicorn, Pydantic, python-dotenv.
* **Databases**: SQLite (for native dev testing) & PostgreSQL 15 (for concurrent production scaling).
* **Network & Proxy Routing**: Nginx with SSL reverse proxying and Gzip content compression.
* **Containerization**: Docker & Docker Compose.

---

## 💻 Local Native Development (SQLite Stack)

Ensure you have Python 3.10+ installed.

### 1. Start the Active Developer Server (Port 8006)
Runs the developer branch featuring local code tweaks:
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8006
```

### 2. Start the Stable Reference Server (Port 8005)
Runs the stable baseline code (from tag `v4.1-stable` checked out in the `/baseline` git worktree):
```bash
cd baseline
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8005
```

---

## 🐳 Production Deployment (PostgreSQL + Docker Stack)

Supports thousands of concurrent active student sessions and partners.

### 1. Configure the Virtual Host Domain Routing
Map the local DNS mapping inside your host operating system:
* **Windows (PowerShell as Administrator)**:
  ```powershell
  Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n127.0.0.1 kcet-predictor.local" -Force
  ```
* **macOS / Linux (Terminal)**:
  ```bash
  echo "127.0.0.1 kcet-predictor.local" | sudo tee -a /etc/hosts
  ```

### 2. Generate SSL/TLS Certificates
Generate a self-signed X.509 certificate and private key with CA constraints so browsers will trust it:
```bash
pip install cryptography
python backend/generate_certs.py
```

### 3. Trust the SSL Certificate (Host Machine)
To display the secure padlock icon in Chrome/Edge, import the key to your User Trust Store:
* **Windows (PowerShell)**:
  ```powershell
  Import-Certificate -FilePath "certs/kcet-predictor.local.crt" -CertStoreLocation "Cert:\CurrentUser\Root"
  ```
* **macOS (Terminal)**:
  ```bash
  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/kcet-predictor.local.crt
  ```

### 4. Boot Up the Containers Stack
Build the FastAPI container and spin up PostgreSQL, Web, and Nginx reverse proxy containers in detached mode:
```bash
docker-compose up --build -d
```

### 5. Seed the PostgreSQL database
Run the database migration seeder directly inside the web container to read the datasets and populate all tables:
```bash
docker exec kcet-web python backend/migrate_to_postgres.py
```

Browse the secure portal at: **[https://kcet-predictor.local](https://kcet-predictor.local)** (or bypass proxy at `http://localhost:8000`).

---

## 🔒 Default Test Accounts Reference

### Global HTTP Authorization credentials:
* **Username**: `admin`
* **Password**: `kcet2025`

### Dashboard Roles log-ins (Password: `kcet2025`):
* **Student Group**: Register dynamically on the page.
* **Institution Group (Administrators)**: `rvgroup`, `bmsgroup`, `pesgroup`, or `dsgroup`
* **Counsellor Group (Advisors)**: `counsellor` or `mentor`
* **Authority Group (KEA Admin)**: `authority`
* **Superuser Group (SysAdmin)**: `superuser`
