"""
Check where the intake mismatch is.
We will compare page-level TOT intake values with the parsed sum of RK intakes on each page.
Let's print pages where page-level TOT intake != parsed RK intake sum.
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

print("=== Checking Annexure E ===")
for pg in range(122, 324):
    text = pdf.pages[pg-1].extract_text() or ""
    page_tot_intake = 0
    parsed_rk_intake = 0
    for line in text.splitlines():
        if line.strip().startswith("TOT "):
            parts = [int(x) for x in re.findall(r'\d+', line)]
            if parts:
                page_tot_intake += parts[0]
        elif line.strip().startswith("RK "):
            parts = [int(x) for x in re.findall(r'\d+', line)]
            if len(parts) >= 2:
                parsed_rk_intake += parts[0]
    if page_tot_intake != parsed_rk_intake:
        print(f"Page {pg}: TOT intake = {page_tot_intake}, parsed RK intake = {parsed_rk_intake}")

print("\n=== Checking Annexure V ===")
for pg in range(325, 361):
    text = pdf.pages[pg-1].extract_text() or ""
    page_tot_intake = 0
    parsed_rk_intake = 0
    for line in text.splitlines():
        if line.strip().startswith("TOT "):
            parts = [int(x) for x in re.findall(r'\d+', line)]
            if parts:
                page_tot_intake += parts[0]
        elif line.strip().startswith("RK "):
            parts = [int(x) for x in re.findall(r'\d+', line)]
            if len(parts) >= 2:
                parsed_rk_intake += parts[0]
    if page_tot_intake != parsed_rk_intake:
        print(f"Page {pg}: TOT intake = {page_tot_intake}, parsed RK intake = {parsed_rk_intake}")
