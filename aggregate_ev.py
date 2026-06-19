"""
Write a quick script to find the total seat counts and sums of the other columns for E and V to verify our exact numbers.
Let's aggregate:
1. Intake
2. KEA seats (total_kea)
3. PH (kea_ph)
4. SPL (kea_spl)
5. HK (kea_hk)
6. RK (kea_rk)
7. TOT (kea_tot)
"""
import pdfplumber, re, sys
sys.stdout.reconfigure(encoding="utf-8")

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for name, pg_range in [("E", range(122, 324)), ("V", range(325, 361))]:
    intake = 0
    kea = 0
    ph = 0
    spl = 0
    hk = 0
    rk = 0
    tot = 0
    
    pages = list(pg_range)
    for pg in pages:
        text = pdf.pages[pg-1].extract_text() or ""
        # Let's find each college's TOT row (starts with "TOT")
        # In E and V, we have:
        # "TOT <intake> <total_kea> <ph> <spl> <rur> ..." or something.
        # Wait! Let's check how many "TOT" rows are on a page, and print them.
        for line in text.splitlines():
            if line.strip().startswith("TOT "):
                parts = [int(x) for x in re.findall(r'\d+', line)]
                if len(parts) >= 6:
                    # Let's check the columns of TOT row on page 122:
                    # TOT 240 226 12 2 34 16 6 2 0 4 2 2 2 181 80 32 14 6 28 6 6 9
                    # Let's map them.
                    # Index 0: Intake = 240
                    # Index 1: KEA = 226
                    # Index 2: PH = 12
                    # Index 3: SPL = 2
                    # Let's calculate HK and RK.
                    # Wait, let's write a parser that parses the course-by-course rows or the college-level totals.
                    # Let's see if we can parse course-by-course lines!
                    pass

print("Done")
