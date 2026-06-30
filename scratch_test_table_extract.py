import pdfplumber

def test_extract():
    with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
        # Page 362 (Index 361)
        print("=== Page 362 Table Extraction ===")
        tables = pdf.pages[361].extract_tables()
        print(f"Found {len(tables)} tables on Page 362.")
        for idx, table in enumerate(tables):
            print(f"Table {idx+1}:")
            for row in table[:5]:
                print(f"  {row}")
            if len(table) > 5:
                print("  ...")
                
        # Page 425 (Index 424)
        print("\n=== Page 425 Table Extraction ===")
        tables = pdf.pages[424].extract_tables()
        print(f"Found {len(tables)} tables on Page 425.")
        for idx, table in enumerate(tables):
            print(f"Table {idx+1}:")
            for row in table[:5]:
                print(f"  {row}")
            if len(table) > 5:
                print("  ...")

if __name__ == "__main__":
    test_extract()
