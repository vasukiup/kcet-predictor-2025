"""
Extract actual Ins Total from every Annexure O page (104-117) to find per-college discrepancies.
"""
import pdfplumber, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")

# Pull Ins Totals from text pages
pdf_ins = {}
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg in range(104, 118):
        text = pdf.pages[pg-1].extract_text() or ""
        lines = text.splitlines()
        for i,line in enumerate(lines):
            if "Ins Total" in line:
                # The college name is a few lines above - find the nearest college number
                # Look backward for a line starting with a number
                num = None
                name_line = None
                for j in range(i-1, max(0,i-30), -1):
                    m = re.match(r'^(\d{1,2})\s+([A-Z].+)', lines[j])
                    if m:
                        num = int(m.group(1))
                        name_line = m.group(2)
                        break
                nums = [int(x) for x in re.findall(r'\d+', line)]
                if num and nums:
                    intake = nums[0]
                    kea    = nums[1] if len(nums) > 1 else 0
                    pdf_ins[num] = {"page":pg, "name":name_line, "intake":intake, "kea":kea}
                    print(f"  O-{num:>2} pg{pg}: {name_line[:40]:<40} intake={intake:>6}  kea={kea:>6}")

# Also from image page 118 (already read)
pdf_ins[26] = {"page":118, "name":"University of Mysuru",         "intake":420, "kea":210}
pdf_ins[27] = {"page":118, "name":"Vidyashilp University",        "intake":120, "kea": 48}

print(f"\nFound {len(pdf_ins)} college Ins Totals from PDF pages")

# Compare with our data
with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)
our_cols = {c["college_number"]:c for c in d["colleges"] if c["annexure"]=="O"}

print("\n")
print(f"{'#':>3} {'College':<42} {'PDF-Intake':>10} {'Our-Intake':>10} {'Diff':>8}")
print("-"*78)
total_diff = 0
for num in sorted(pdf_ins):
    pdf_i = pdf_ins[num]["intake"]
    col = our_cols.get(num)
    if col:
        our_i = sum(c["total_intake"] for c in col["courses"])
        diff = our_i - pdf_i
        total_diff += diff
        flag = "  <---" if diff != 0 else ""
        print(f"{num:>3} {pdf_ins[num]['name'][:42]:<42} {pdf_i:>10} {our_i:>10} {diff:>+8}{flag}")
    else:
        print(f"{num:>3} {pdf_ins[num]['name'][:42]:<42} {pdf_i:>10} {'MISSING':>10}")
print("-"*78)
print(f"{'Total diff':>58} {total_diff:>+8}")
