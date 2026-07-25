import pdfplumber

def test_fuzzy():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        page = pdf.pages[361] # Page 362
        tables = page.find_tables()
        print(f"Found {len(tables)} tables on Page 362.")
        
        # Bounding box of tables
        previous_bottom = 0
        for idx, t in enumerate(tables):
            bbox = t.bbox
            print(f"\nTable {idx+1} Bounding Box: {bbox}")
            # Crop the page to extract text above the table
            crop = page.crop((0, previous_bottom, page.width, bbox[1]))
            text_above = crop.extract_text() or ""
            print(f"Text above table {idx+1}:")
            print(repr(text_above))
            previous_bottom = bbox[3]

if __name__ == "__main__":
    test_fuzzy()
