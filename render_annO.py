"""Render all Annexure O pages as images for visual inspection."""
import pdfplumber, sys
sys.stdout.reconfigure(encoding="utf-8")
with pdfplumber.open("Seat_Matrix_05072025.pdf") as pdf:
    for pg in range(104, 118):
        pdf.pages[pg-1].to_image(resolution=130).save(f"annO_p{pg}.png")
        print(f"Saved annO_p{pg}.png")
