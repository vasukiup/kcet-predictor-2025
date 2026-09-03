# KEA Seat Matrix & Prediction Portal - Version Release Manifest

**Version Tag:** `v7.0-2026-R2-stable`  
**Release Date:** September 3, 2026  
**Git Branch:** `scaling-architecture` (Submodule: `baseline-data`)  
**Server Port:** `8050`  

---

## 🚀 Key Release Highlights

### 1. 2026 Round 2 Cutoff Ranks (100% Loaded & Synchronized)
* **237 Engineering Colleges**: Fully loaded with seat matrix and Round 2 Provisional Cutoff ranks across Karnataka.
* **1,635 Matched Courses (98.6% Coverage)**: Enforced strict 1-to-1 course matching per college to eliminate false-positive cutoff sharing across similar branch names.
* **Typo & Line Break Normalization**: Standardized course names (`Commi.inication` -> `Communication`, split line breaks `DA TA SCIENCE`, `CYB ER`, `BLO CK CHAIN`).

### 2. Full Multi-Category & Subcategory View (74 KEA Categories)
* **Interactive Modal Category Selector**: Dynamic `🎯 Cut-off Category View` dropdown added to the college details modal header.
* **Supported Categories & Special Quotas**:
  * **General Quotas**: `GM`, `1G`, `2AG`, `2BG`, `3AG`, `3BG`, `SCG`, `STG`
  * **Rural & Kannada Medium**: `GMR`, `GMK`, `1R`, `1K`, `2AR`, `2AK`, `2BR`, `2BK`, `3AR`, `3AK`, `3BR`, `3BK`, `SCR`, `SCK`, `STR`, `STK`
  * **Hyderabad-Karnataka (371-J)**: `GMH`, `1H`, `2AH`, `2BH`, `3AH`, `3BH`, `SCH`, `STH`
  * **Supernumerary Quota**: `🎁 SNQ` (5% Fee Waiver)
  * **Differently Abled & Physically Handicapped**: `♿ PH`, `♿ D`, `♿ DK`, `♿ XD` (strictly separated into distinct category lookups)
  * **Special Categories**: `🛡️ S1G`, `S2G`, `S3G`, `S4G` (General, Rural, Kannada, HK variants)
  * **Sports, NCC & Defence**: `🏅 SPO`, `🎗️ NCC`, `👮 CAP`, `👮 XCP`, `🌾 AGL`, `🎖️ DEF`

### 3. Database & Backend API Integrity
* **SQLite Backend (`backend/kcet.db`)**: Schema updated with batched parameter queries (chunk size: 300) to prevent SQLite 999 parameter variable limit errors.
* **Static Fallback Data**: `seat_matrix_data_2026.json` and `seat_matrix_data.json` synchronized for instant local offline rendering.
* **FastAPI Server**: Whitelisted public read-only endpoints (`/api/colleges`, `/api/filters`, `/api/stats`, `/api/predict`).

---

## 📌 Verification Checklist
* [x] Port 8050 live and responding with `200 OK` across all API and static endpoints.
* [x] All 237 colleges rendering 2026 Round 2 cutoffs without JS or SQL exceptions.
* [x] E002, E006, E107, E308 verified for exact 1-to-1 category and course cutoffs.
