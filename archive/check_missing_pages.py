"""
Look up pages around 146, 172, 180, 221, 230 to see why college #25, #47, #50, #75, #113, #123, #124, #159, #168 are not matching the standard regex.
Standard regex: `^(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)$`
Wait! `25 B V V Sangha`s ...` has a backtick `\`` in the name!
`170 V S M`s ...` also has a backtick `\`` in the name!
Let's print the lines around page 172 (college #47), page 180 (college #50), page 221 (college #75), page 296 (college #170).
"""
import pdfplumber, re

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")

# Let's print first 15 lines of pages around the missing ones
pages_to_check = {
    47: 172,
    50: 180,
    75: 221,
    113: 259,
    123: 265,
    124: 266,
    159: 289,
    168: 295
}

for num, pg in pages_to_check.items():
    print(f"\n--- Checking Page {pg} for college #{num} ---")
    text = pdf.pages[pg-1].extract_text() or ""
    lines = text.splitlines()
    for l in lines[:10]:
        print(l.strip())
