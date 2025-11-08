import fitz  
import os

# === PARAMETRI PERSONALIZZATI ===
input_folder = r"C:\Users\g.codispoti\Downloads\usd Vanchiglia"
output_folder = os.path.join(input_folder, "PDF_firmati")
signature_path = r"C:\Users\g.codispoti\OneDrive - SIELTE S.p.A\prog python\siae timbro  multiplo\Timbro SIAE.jpg"

# Crea la cartella di output se non esiste
os.makedirs(output_folder, exist_ok=True)

# === IMPOSTAZIONI FIRMA ===
# Margine dal bordo (in punti PDF: 1 punto ≈ 0,35 mm)
margin_x = 30   # distanza dal bordo sinistro
margin_y = 35   # distanza dal bordo inferiore
signature_width = 100  # larghezza firma in punti (~3,5 cm)
# L'altezza si adatta automaticamente mantenendo proporzioni

# === CICLO SU TUTTI I PDF ===
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(".pdf"):
        continue

    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, filename)

    # Apri il PDF
    doc = fitz.open(input_path)
    signature_img = fitz.open(signature_path)
    rect_img = signature_img[0].rect
    ratio = rect_img.height / rect_img.width
    signature_height = signature_width * ratio

    for page in doc:
        page_width = page.rect.width
        page_height = page.rect.height

        # posizione in basso sinistra
        x0 = margin_x
        y0 = page_height - signature_height - margin_y
        x1 = x0 + signature_width
        y1 = y0 + signature_height
        rect = fitz.Rect(x0, y0, x1, y1)
        page.insert_image(rect, filename=signature_path, keep_proportion=True)

    doc.save(output_path)
    doc.close()
    print(f"✅ Firmato: {filename}")

print("\nTutti i PDF sono stati firmati con successo!")
print(f"I file si trovano in: {output_folder}")
