import pdfplumber
import re

with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue
        # Only check engineering seat matrix pages (Annexure A, B, C, D)
        if not any(f"ANNEXURE : {ann}" in text for ann in ["A", "B", "C", "D"]):
            continue
            
        lines = text.split("\n")
        for line_idx, line in enumerate(lines):
            line = line.strip()
            # If it starts with a course serial number
            if re.match(r'^\d+\s+[A-Z]', line):
                # Count how many numbers are at the end
                nums = re.findall(r'\d+', line)
                if len(nums) < 3: # serial number + at least 2 seat count numbers
                    print(f"Page {idx+1}, Line {line_idx}: {line} (Only {len(nums)} numbers)")
