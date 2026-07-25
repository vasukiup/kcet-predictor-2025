"""
Calculate total seats sum by adding the last page TOT rows of all colleges.
Let's see what is the sum of total intake and KEA seats in E and V.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

for name, pg_range in [("E", range(122, 324)), ("V", range(325, 361))]:
    tot_intake = 0
    tot_kea = 0
    pages_list = list(pg_range)
    # Let's extract the TOT row of each page
    for pg in pages_list:
        text = pdf.pages[pg-1].extract_text() or ""
        for line in text.splitlines():
            if line.strip().startswith("TOT ") or line.strip().startswith("TOT\t"):
                parts = [int(x) for x in re.findall(r'\d+', line)]
                if parts:
                    # The format of TOT line on each page is:
                    # TOT <intake> <kea_seats> <ph> <spl> <rur_tot> <rur_gm> <rur_sc> <rur_st> ... <urb_tot> ...
                    tot_intake += parts[0]
                    tot_kea += parts[1]
    print(f"Annexure {name} calculated from TOT rows on each page:")
    print(f"  Total Intake: {tot_intake:,}")
    print(f"  Total KEA:    {tot_kea:,}")
