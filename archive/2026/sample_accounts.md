# KCET Predictor Portal: Default Test Accounts Reference

This document lists the pre-configured credentials and dashboard privileges for each user group to help you and your users test the system capabilities.

---

## 🔐 Core Portal Credentials (HTTP Basic Authentication)
To access any page on the portal (`https://kcet-predictor.local` or `http://localhost:8000`), you must enter the global secure credentials:
* **Username**: `admin`
* **Password**: `kcet2025`

---

## 👥 Dashboard User Group Accounts

### 1. 🎓 Student Group (Self-Registration)
Students do not require pre-configured logins. They register dynamically on the portal home page:
* **Access**: Fill in the registration form (Name, Email, Rank, Category, Region).
* **Key Features**:
  * Run custom rank predictions based on Round 1 Cutoffs.
  * Dynamically calculate tuition fees under different quotas (Govt, Aided, SNQ, COMEDK).
  * Build option entry lists (Dream vs. Target vs. Safety) up to 100 choices.
  * Audit sequences for out-of-order volatility or insufficient safety options.

---

### 2. 🏛️ Institution Group (College Administrators)
Simulate administrator views for major educational groups:
* **Username / Group ID**: 
  * `rvgroup` (RV Group of Institutions)
  * `bmsgroup` (BMS Group of Institutions)
  * `pesgroup` (PES Group of Institutions)
  * `dsgroup` (Dayananda Sagar Group)
* **Password**: `kcet2025`
* **Key Features**:
  * Manage institutional profile data (NIRF Rank, NAAC accreditations).
  * Edit seat intakes, COMEDK/Management splits, and course details.
  * Track specific placements packages and hostel fees.

---

### 3. ⚖️ Counselor / Mentor Group (Academic Advisors)
Simulate counselor sessions to manage multiple student portfolios:
* **Counsellor ID**: `counsellor` or `mentor`
* **Password**: `kcet2025`
* **Key Features**:
  * Create, save, and delete custom candidate profiles dynamically.
  * Manage independent option entry choice sheets for each candidate.
  * Auto-optimize student preference lists using the Volatility Auditor.

---

### 4. 🛡️ Authority Group (KEA Administrators)
Simulate state-level authorities:
* **Authority ID**: `authority`
* **Password**: `kcet2025`
* **Key Features**:
  * View state-wide admissions statistics (Seat distributions by type, top districts).
  * Export seat matrix sheets or cutoff ranks by year/college type in CSV/JSON.
  * Track historical Year-on-Year seat growth and cutoff popularity shifts.

---

### 5. 👑 Superuser Group (Global System Administrators)
Full platform access:
* **Superuser ID**: `superuser`
* **Password**: `kcet2025`
* **Key Features**:
  * Access the **Viewport Simulator Header** to test responsive layouts (iPad, iPhone 15, S23, Pixel 8) with interactive portrait/landscape rotation.
  * Toggle **Perspective Switching** to view the app as a Student, Institution, or Authority.
