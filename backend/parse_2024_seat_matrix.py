import json
import pdfplumber
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Scanned engineering colleges data to inject to guarantee 100% accuracy
SCANNED_COLLEGES = [
    # ── Annexure A, Page 11 ──────────────────────────────────────────────────
    {
        "college_number": 22,
        "college_name": "VISVESWARIAH TECHNOLOGICAL UNIVERISTY, BELAGAVI, VIAT, MUDDENAHALLI CAMPUS, CHIKKABALLAPUR",
        "address": "Muddenahalli campus,Chikkaballapur",
        "annexure": "A",
        "college_type": "Government Engineering Colleges/VTU Constitutent Colleges",
        "district": "Chikkaballapura",
        "total_intake": 390, "total_kea_seats": 390,
        "courses": [
            {
                "course_name": "B TECH IN AERONAUTICAL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 1,
                "kea_hk": 4, "kea_rk": 52, "kea_tot": 56,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "B TECH IN COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 120,
                "snq_5pct": 6, "kea_ph": 6, "kea_spl": 1,
                "kea_hk": 9, "kea_rk": 104, "kea_tot": 113,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 6
            },
            {
                "course_name": "B TECH IN ELECTRONICS & COMMUNICATION ENGINEERING",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 52, "kea_tot": 57,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "B TECH IN ELECTRONICS & COMPUTER ENGINEERING",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 52, "kea_tot": 57,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "B Tech in ROBOTICS AND ARTIFICIAL INTELLIGENCE",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 1,
                "kea_hk": 4, "kea_rk": 52, "kea_tot": 56,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "BTECH IN MECHANICAL AND SMART MANUFACTURING",
                "total_intake": 30, "total_kea_seats": 30,
                "snq_5pct": 2, "kea_ph": 2, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 25, "kea_tot": 27,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 2
            }
        ]
    },
    # ── Annexure C, Page 80 ──────────────────────────────────────────────────
    {
        "college_number": 144,
        "college_name": "Vivekananada Institute of Technology,Kengeri, Bangalore",
        "address": "GUDIMAVU VILLAGE,KENGERI(HOBLI)NEAR KUMBALAGODU,BANGALORE",
        "annexure": "C",
        "college_type": "Private Unaided Engineering Colleges",
        "district": "Bangalore",
        "total_intake": 570, "total_kea_seats": 257,
        "courses": [
            {
                "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "total_intake": 90, "total_kea_seats": 41,
                "snq_5pct": 4, "kea_ph": 2, "kea_spl": 0,
                "kea_hk": 3, "kea_rk": 36, "kea_tot": 39,
                "cat2_seats": 27, "cat3_seats": 22, "over_above_5pct": 4
            },
            {
                "course_name": "CIVIL ENGINEERING",
                "total_intake": 30, "total_kea_seats": 14,
                "snq_5pct": 2, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 1, "kea_rk": 11, "kea_tot": 12,
                "cat2_seats": 9, "cat3_seats": 7, "over_above_5pct": 2
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 180, "total_kea_seats": 81,
                "snq_5pct": 9, "kea_ph": 4, "kea_spl": 0,
                "kea_hk": 6, "kea_rk": 70, "kea_tot": 76,
                "cat2_seats": 54, "cat3_seats": 45, "over_above_5pct": 9
            },
            {
                "course_name": "ELECTRONICS AND COMMUNICATION ENGG",
                "total_intake": 120, "total_kea_seats": 54,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 4, "kea_rk": 47, "kea_tot": 51,
                "cat2_seats": 36, "cat3_seats": 30, "over_above_5pct": 6
            },
            {
                "course_name": "INFORMATION SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 54,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 4, "kea_rk": 47, "kea_tot": 51,
                "cat2_seats": 36, "cat3_seats": 30, "over_above_5pct": 6
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 30, "total_kea_seats": 13,
                "snq_5pct": 1, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 1, "kea_rk": 11, "kea_tot": 12,
                "cat2_seats": 9, "cat3_seats": 8, "over_above_5pct": 1
            }
        ]
    },
    {
        "college_number": 145,
        "college_name": "Yenepoya Institute Of Technology,Mangalore",
        "address": "VIDYANAGAR N.H 13THODAR MIJAR POST MOODBIDRI MANGALORE TQ",
        "annexure": "C",
        "college_type": "Private Unaided Engineering Colleges",
        "district": "Dakshina Kannada",
        "total_intake": 480, "total_kea_seats": 216,
        "courses": [
            {
                "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 24, "kea_tot": 26,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGG(INTERNET OF THINGS & CYBER SECURITY INCLUDING BLOCK CHAIN TECH)",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 2, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 23, "kea_tot": 25,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 54,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 4, "kea_rk": 47, "kea_tot": 51,
                "cat2_seats": 36, "cat3_seats": 30, "over_above_5pct": 6
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING(DATA SCIENCE)",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 24, "kea_tot": 26,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "total_intake": 30, "total_kea_seats": 13,
                "snq_5pct": 2, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 1, "kea_rk": 11, "kea_tot": 12,
                "cat2_seats": 0, "cat3_seats": 15, "over_above_5pct": 2
            },
            {
                "course_name": "ELECTRONICS AND COMMUNICATION ENGG",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 24, "kea_tot": 26,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "INFORMATION SCIENCE AND ENGINEERING",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 2, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 22, "kea_tot": 24,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 30, "total_kea_seats": 14,
                "snq_5pct": 2, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 1, "kea_rk": 12, "kea_tot": 13,
                "cat2_seats": 9, "cat3_seats": 7, "over_above_5pct": 2
            }
        ]
    },
    # ── Annexure D, Page 88 ──────────────────────────────────────────────────
    {
        "college_number": 16,
        "college_name": "The Oxford College of Engineering, Bangalore",
        "address": "HOSUR ROAD, BOMMANAHALLI, BANGALORE",
        "annexure": "D",
        "college_type": "Private Unaided Minority Engineering Colleges",
        "district": "Bangalore",
        "total_intake": 780, "total_kea_seats": 312,
        "courses": [
            {
                "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 20, "kea_tot": 22,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            },
            {
                "course_name": "BIO-TECHNOLOGY",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            },
            {
                "course_name": "CIVIL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 20, "kea_tot": 22,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 180, "total_kea_seats": 72,
                "snq_5pct": 9, "kea_ph": 4, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 63, "kea_tot": 68,
                "cat2_seats": 54, "cat3_seats": 54, "over_above_5pct": 9
            },
            {
                "course_name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            },
            {
                "course_name": "ELECTRONICS AND COMMUNICATION ENGG",
                "total_intake": 120, "total_kea_seats": 48,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 3, "kea_rk": 42, "kea_tot": 45,
                "cat2_seats": 36, "cat3_seats": 36, "over_above_5pct": 6
            },
            {
                "course_name": "INFORMATION SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 48,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 3, "kea_rk": 42, "kea_tot": 45,
                "cat2_seats": 36, "cat3_seats": 36, "over_above_5pct": 6
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 20, "kea_tot": 22,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            },
            {
                "course_name": "MECHATRONICS",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 18, "cat3_seats": 18, "over_above_5pct": 3
            }
        ]
    },
    # ── Annexure M, Page 103 (UVCE public autonomous university) ──────────────
    {
        "college_number": 1,
        "college_name": "University of Visvesvaraya College of Engineering",
        "address": "K R Circle, Bangalore",
        "annexure": "M",
        "college_type": "Seats for Government Courses in Public Universities",
        "district": "Bangalore",
        "total_intake": 760, "total_kea_seats": 760,
        "courses": [
            {
                "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 52, "kea_tot": 57,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "CIVIL ENGINEERING",
                "total_intake": 120, "total_kea_seats": 120,
                "snq_5pct": 6, "kea_ph": 6, "kea_spl": 1,
                "kea_hk": 9, "kea_rk": 104, "kea_tot": 113,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 6
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 120,
                "snq_5pct": 6, "kea_ph": 6, "kea_spl": 1,
                "kea_hk": 9, "kea_rk": 104, "kea_tot": 113,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 6
            },
            {
                "course_name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "total_intake": 120, "total_kea_seats": 120,
                "snq_5pct": 6, "kea_ph": 6, "kea_spl": 0,
                "kea_hk": 9, "kea_rk": 105, "kea_tot": 114,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 6
            },
            {
                "course_name": "ELECTRONICS AND COMMUNICATION ENGG",
                "total_intake": 120, "total_kea_seats": 120,
                "snq_5pct": 6, "kea_ph": 6, "kea_spl": 1,
                "kea_hk": 9, "kea_rk": 104, "kea_tot": 113,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 6
            },
            {
                "course_name": "INFORMATION SCIENCE AND ENGINEERING",
                "total_intake": 60, "total_kea_seats": 60,
                "snq_5pct": 3, "kea_ph": 3, "kea_spl": 1,
                "kea_hk": 4, "kea_rk": 52, "kea_tot": 56,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 3
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 160, "total_kea_seats": 160,
                "snq_5pct": 8, "kea_ph": 8, "kea_spl": 1,
                "kea_hk": 12, "kea_rk": 139, "kea_tot": 151,
                "cat2_seats": 0, "cat3_seats": 0, "over_above_5pct": 8
            }
        ]
    },
    # ── Annexure O, Page 116 ─────────────────────────────────────────────────
    {
        "college_number": 28,
        "college_name": "Vidyashilp University",
        "address": "#125, Bettenahalli, Kundana Hobli, Chapparkallu Rd, Bengaluru, Karnataka 562110",
        "annexure": "O",
        "college_type": "Private Universities",
        "district": "Bangalore",
        "total_intake": 120, "total_kea_seats": 48,
        "courses": [
            {
                "course_name": "BTECH (HONS) COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)",
                "total_intake": 120, "total_kea_seats": 48,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 0,
                "kea_hk": 4, "kea_rk": 41, "kea_tot": 45,
                "cat2_seats": 0, "cat3_seats": 72, "over_above_5pct": 6
            }
        ]
    },
    # ── Annexure P, Page 117 ─────────────────────────────────────────────────
    {
        "college_number": 1,
        "college_name": "Sri Siddhartha Institute of Technology, Tumkur",
        "address": "MARALUR, TUMKUR",
        "annexure": "P",
        "college_type": "Seats in Deemed Universities",
        "district": "Tumkur",
        "total_intake": 1050, "total_kea_seats": 420,
        "courses": [
            {
                "course_name": "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 180, "total_kea_seats": 72,
                "snq_5pct": 9, "kea_ph": 4, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 63, "kea_tot": 68,
                "cat2_seats": 0, "cat3_seats": 108, "over_above_5pct": 9
            },
            {
                "course_name": "BIO-MEDICAL ENGINEERING",
                "total_intake": 30, "total_kea_seats": 12,
                "snq_5pct": 1, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 1, "kea_rk": 9, "kea_tot": 10,
                "cat2_seats": 0, "cat3_seats": 18, "over_above_5pct": 1
            },
            {
                "course_name": "CIVIL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 20, "kea_tot": 22,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING (CYBER SECURITY)",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 20, "kea_tot": 22,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING(DATA SCIENCE)",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "ELECTRICAL & ELECTRONICS ENGINEERING",
                "total_intake": 120, "total_kea_seats": 48,
                "snq_5pct": 6, "kea_ph": 2, "kea_spl": 0,
                "kea_hk": 4, "kea_rk": 42, "kea_tot": 46,
                "cat2_seats": 0, "cat3_seats": 72, "over_above_5pct": 6
            },
            {
                "course_name": "ELECTRONICS AND COMMUNICATION ENGG",
                "total_intake": 180, "total_kea_seats": 72,
                "snq_5pct": 9, "kea_ph": 4, "kea_spl": 0,
                "kea_hk": 5, "kea_rk": 63, "kea_tot": 68,
                "cat2_seats": 0, "cat3_seats": 108, "over_above_5pct": 9
            },
            {
                "course_name": "ELECTRONICS AND TELECOMMUNICATION ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "INFORMATION SCIENCE AND ENGINEERING",
                "total_intake": 120, "total_kea_seats": 48,
                "snq_5pct": 6, "kea_ph": 3, "kea_spl": 1,
                "kea_hk": 3, "kea_rk": 41, "kea_tot": 44,
                "cat2_seats": 0, "cat3_seats": 72, "over_above_5pct": 6
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            },
            {
                "course_name": "ROBOTICS AND ARTIFICIAL INTELLIGENCE",
                "total_intake": 60, "total_kea_seats": 24,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 0,
                "kea_hk": 2, "kea_rk": 21, "kea_tot": 23,
                "cat2_seats": 0, "cat3_seats": 36, "over_above_5pct": 3
            }
        ]
    },
    # ── Annexure C, Additional Seat Matrix (basavengcollegeenglish.pdf) ───────
    {
        "college_number": 24,
        "college_name": "BASAV ENGINEERING SCHOOL OF TECHNOLOGY, VIJAYAPURA",
        "address": "ZALKI, TQ. INDI, DIST VIJAYAPURA",
        "annexure": "C",
        "college_type": "Private Unaided Engineering Colleges",
        "district": "Vijayapura",
        "total_intake": 180, "total_kea_seats": 81,
        "courses": [
            {
                "course_name": "CIVIL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 23, "kea_tot": 25,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "COMPUTER SCIENCE AND ENGINEERING",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 23, "kea_tot": 25,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            },
            {
                "course_name": "MECHANICAL ENGINEERING",
                "total_intake": 60, "total_kea_seats": 27,
                "snq_5pct": 3, "kea_ph": 1, "kea_spl": 1,
                "kea_hk": 2, "kea_rk": 23, "kea_tot": 25,
                "cat2_seats": 18, "cat3_seats": 15, "over_above_5pct": 3
            }
        ]
    }
]

# Mapping of page ranges to Engineering Annexures
PAGE_RANGES = {
    "A": list(range(4, 11)),
    "B": list(range(12, 15)),
    "C": list(range(16, 80)),
    "D": list(range(81, 88)),
    "O": list(range(104, 116))
}

COLLEGE_TYPES = {
    "A": "Government Engineering Colleges/VTU Constitutent Colleges",
    "B": "Seats in Aided Courses of Aided Engineering Colleges",
    "C": "Private Unaided Engineering Colleges",
    "D": "Private Unaided Minority Engineering Colleges",
    "O": "Private Universities"
}

def parse_pdf():
    pdf_path = "2024/FinalSeatMatrix16072024english.pdf"
    colleges = []
    
    # Process text-based pages
    with pdfplumber.open(pdf_path) as pdf:
        for ann, pages in PAGE_RANGES.items():
            col_type = COLLEGE_TYPES[ann]
            print(f"Parsing Annexure {ann} ({len(pages)} pages)...")
            
            for page_num in pages:
                page = pdf.pages[page_num - 1]
                tables_with_bboxes = page.find_tables()
                tables_with_bboxes = sorted(tables_with_bboxes, key=lambda t: t.bbox[1])
                
                previous_bottom = 0
                for t in tables_with_bboxes:
                    bbox = t.bbox
                    
                    # Extract college header block text above the table
                    crop = page.crop((0, previous_bottom, page.width, bbox[1]))
                    text_above = crop.extract_text() or ""
                    previous_bottom = bbox[3]
                    
                    # Clean and parse college name/code
                    lines_above = [l.strip() for l in text_above.splitlines() if l.strip()]
                    college_name = ""
                    college_code = None
                    address = ""
                    
                    for l in lines_above:
                        m_header = re.match(r'^(\d+)\s+([A-Za-z].*)$', l)
                        if m_header:
                            college_code = int(m_header.group(1))
                            college_name = m_header.group(2).strip()
                        elif l.startswith("Address"):
                            address = l.replace("Address :", "").strip()
                            
                    cells = t.extract()
                    if cells and len(cells) > 2:
                        courses = []
                        for row in cells:
                            if not row or len(row) < 3:
                                continue
                            
                            # Check if this is a course row
                            sl_no = (row[0] or "").strip()
                            course_name = (row[1] or "").replace("\n", " ").strip()
                            
                            if not sl_no.isdigit() or not course_name:
                                continue
                            
                            # Parse numeric values dynamically based on columns count of the row
                            nums = []
                            for cell in row[2:]:
                                val = (cell or "0").replace("\n", "").strip()
                                nums.append(int(val) if val.isdigit() else 0)
                                
                            intake = nums[0] if len(nums) > 0 else 0
                            kea = nums[1] if len(nums) > 1 else 0
                            
                            ph = 0; spl = 0; hk = 0; rk = 0; tot = 0; comedk = 0; mgmt = 0; over = 0
                            
                            if len(row) == 9: # Ann O
                                ph = nums[2] if len(nums) > 2 else 0
                                spl = nums[3] if len(nums) > 3 else 0
                                hk = nums[4] if len(nums) > 4 else 0
                                rk = nums[5] if len(nums) > 5 else 0
                                tot = nums[6] if len(nums) > 6 else 0
                            elif len(row) == 10: # Ann A
                                ph = nums[2] if len(nums) > 2 else 0
                                spl = nums[3] if len(nums) > 3 else 0
                                hk = nums[4] if len(nums) > 4 else 0
                                rk = nums[5] if len(nums) > 5 else 0
                                tot = nums[6] if len(nums) > 6 else 0
                                over = nums[7] if len(nums) > 7 else 0
                            elif len(row) == 11: # Ann B
                                ph = nums[2] if len(nums) > 2 else 0
                                spl = nums[3] if len(nums) > 3 else 0
                                hk = nums[4] if len(nums) > 4 else 0
                                rk = nums[5] if len(nums) > 5 else 0
                                tot = nums[6] if len(nums) > 6 else 0
                                mgmt = nums[7] if len(nums) > 7 else 0
                                over = nums[8] if len(nums) > 8 else 0
                            elif len(row) == 12: # Ann C, D
                                ph = nums[2] if len(nums) > 2 else 0
                                spl = nums[3] if len(nums) > 3 else 0
                                hk = nums[4] if len(nums) > 4 else 0
                                rk = nums[5] if len(nums) > 5 else 0
                                tot = nums[6] if len(nums) > 6 else 0
                                comedk = nums[7] if len(nums) > 7 else 0
                                mgmt = nums[8] if len(nums) > 8 else 0
                                over = nums[9] if len(nums) > 9 else 0
                                
                            # Resolve district from 2025 mapping or heuristics
                            dist = district_map.get(college_code, "")
                            if not dist:
                                addr_lower = address.lower()
                                name_lower = college_name.lower()
                                if "bangalore" in addr_lower or "bengaluru" in addr_lower or "bangalore" in name_lower or "bengaluru" in name_lower:
                                    dist = "Bangalore"
                                elif "mysore" in addr_lower or "mysuru" in addr_lower or "mysore" in name_lower or "mysuru" in name_lower:
                                    dist = "Mysore"
                                elif "mangalore" in addr_lower or "mangaluru" in addr_lower or "mangalore" in name_lower or "mangaluru" in name_lower:
                                    dist = "Dakshina Kannada"
                                elif "belgaum" in addr_lower or "belagavi" in addr_lower or "belgaum" in name_lower or "belagavi" in name_lower:
                                    dist = "Belagavi"
                                elif "bagalkot" in addr_lower or "bagalkote" in addr_lower or "bagalkot" in name_lower or "bagalkote" in name_lower:
                                    dist = "Bagalkote"
                                elif "tumkur" in addr_lower or "tumakuru" in addr_lower or "tumkur" in name_lower or "tumakuru" in name_lower:
                                    dist = "Tumakuru"
                                elif "gulbarga" in addr_lower or "kalaburagi" in addr_lower or "gulbarga" in name_lower or "kalaburagi" in name_lower:
                                    dist = "Kalaburagi"
                                elif "dharwad" in addr_lower or "hubli" in addr_lower or "dharwad" in name_lower or "hubli" in name_lower:
                                    dist = "Dharwad"
                                elif "davangere" in addr_lower or "davanagere" in addr_lower or "davangere" in name_lower or "davanagere" in name_lower:
                                    dist = "Davanagere"
                                else:
                                    dist = "Unknown"

                            courses.append({
                                "course_name": course_name,
                                "total_intake": intake,
                                "total_kea_seats": kea,
                                "snq_5pct": over, "kea_ph": ph, "kea_spl": spl,
                                "kea_hk": hk, "kea_rk": rk, "kea_tot": tot,
                                "cat2_seats": comedk, "cat3_seats": mgmt,
                                "over_above_5pct": over
                            })
                            
                        if college_name and college_code is not None:
                            colleges.append({
                                "college_number": college_code,
                                "college_name": college_name,
                                "address": address,
                                "annexure": ann,
                                "college_type": col_type,
                                "district": dist,
                                "total_intake": sum(c["total_intake"] for c in courses),
                                "total_kea_seats": sum(c["total_kea_seats"] for c in courses),
                                "courses": courses
                            })
                            
    # Inject scanned colleges
    print(f"Injecting {len(SCANNED_COLLEGES)} scanned colleges...")
    colleges.extend(SCANNED_COLLEGES)
    
    # Save structured 2024 database with metadata and statistics
    districts = sorted(list(set(c["district"] for c in colleges if c.get("district"))))
    all_courses = sorted(list(set(cr["course_name"] for c in colleges for cr in c["courses"])))
    
    total_colleges = len(colleges)
    total_seats = sum(c["total_intake"] for c in colleges)
    total_kea_seats = sum(c["total_kea_seats"] for c in colleges)
    
    ANNEXURE_LABELS = {
        "A": "Government / VTU",
        "B": "Govt Aided",
        "C": "Private Unaided",
        "D": "Private Minority",
        "M": "Public University",
        "O": "Private University",
        "P": "Deemed University"
    }

    by_annexure = {}
    by_district = {}
    by_course = {}
    
    for c in colleges:
        ann = c["annexure"]
        dist = c.get("district", "Unknown") or "Unknown"
        
        by_annexure.setdefault(ann, {
            "label": ANNEXURE_LABELS.get(ann, ann),
            "college_count": 0,
            "total_seats": 0,
            "kea_seats": 0,
            "cat2_seats": 0,
            "cat3_seats": 0
        })
        by_annexure[ann]["college_count"] += 1
        by_annexure[ann]["total_seats"] += c["total_intake"]
        by_annexure[ann]["kea_seats"] += c["total_kea_seats"]
        for cr in c["courses"]:
            by_annexure[ann]["cat2_seats"] += cr.get("cat2_seats", 0)
            by_annexure[ann]["cat3_seats"] += cr.get("cat3_seats", 0)
        
        by_district.setdefault(dist, {
            "total": 0,
            "kea": 0,
            "college_count": 0
        })
        by_district[dist]["college_count"] += 1
        by_district[dist]["total"] += c["total_intake"]
        by_district[dist]["kea"] += c["total_kea_seats"]
        
        for cr in c["courses"]:
            cname = cr["course_name"]
            by_course.setdefault(cname, {
                "total": 0,
                "kea": 0,
                "count": 0
            })
            by_course[cname]["count"] += 1
            by_course[cname]["total"] += cr["total_intake"]
            by_course[cname]["kea"] += cr["total_kea_seats"]
            
    stats = {
        "total_colleges": total_colleges,
        "total_seats": total_seats,
        "total_kea_seats": total_kea_seats,
        "by_annexure": by_annexure,
        "by_district": by_district,
        "by_course": by_course
    }
    
    metadata = {
        "year": 2024,
        "document": "ED 140 TEC 2024",
        "date": "16-07-2024"
    }
    
    output_data = {
        "metadata": metadata,
        "colleges": colleges,
        "all_courses": all_courses,
        "districts": districts,
        "stats": stats
    }
    
    out_path = "seat_matrix_data_2024.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nParsing Complete: saved {len(colleges)} colleges to '{out_path}'.")

def load_districts_map():
    district_map = {}
    if os.path.exists("seat_matrix_data.json"):
        try:
            with open("seat_matrix_data.json", "r", encoding="utf-8") as f:
                d2025 = json.load(f)
                for col in d2025.get("colleges", []):
                    num = col.get("college_number")
                    dist = col.get("district")
                    if num and dist:
                        district_map[num] = dist
        except Exception as e:
            print("Failed to load 2025 districts:", e)
    return district_map

if __name__ == "__main__":
    district_map = load_districts_map()
    parse_pdf()
