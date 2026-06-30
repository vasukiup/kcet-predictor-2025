import fitz
import os

def render():
    out_dir = "C:/Users/vasuki/.gemini/antigravity/brain/b4b44e55-fd17-439e-aed5-98b872cd4f7a/scratch/"
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open("Seat_Matrix_05072025.pdf")
    for page_num in range(428, len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150) # render at 150 DPI for clarity
        out_path = os.path.join(out_dir, f"page_{page_num+1}.png")
        pix.save(out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    render()
