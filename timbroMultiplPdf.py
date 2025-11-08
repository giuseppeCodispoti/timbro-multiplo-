import streamlit as st
import fitz 
from PIL import Image
import os
import tempfile
import base64


st.set_page_config(page_title="Firma multipla", page_icon="✍️")


# === FUNZIONE PER AGGIUNGERE SFONDO DA FILE LOCALE ===
def add_header_bg(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        /* Contenitore in alto */
        .header-bg {{
            position: relative;
            width: 100%;
            height: 250px; /* altezza fascia */
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: contain;
            background-position: center;
            border-radius: 0 0 20px 20px; /* angoli inferiori arrotondati */
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        .header-title {{
            position: absolute;
            bottom: 20px;
            left: 40px;
            font-size: 30px;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.6);
        }}
        </style>

        <div class="header-bg">
            
        </div>
        """,
        unsafe_allow_html=True
    )

# 👉 Inserisci qui il percorso della tua foto
add_header_bg(r"C:\Users\g.codispoti\AppData\Local\Programs\Python\Python313\Timbro SIAE.jpg")

st.title("✍️ Firma multipla su PDF e immagini")
st.write("Carica PDF o immagini e applica automaticamente la tua firma/logo in basso a sinistra.")

uploaded_files = st.file_uploader("Carica file (PDF o immagini)", 
                                  type=["pdf", "jpg", "jpeg", "png"],
                                  accept_multiple_files=True)
uploaded_logo = st.file_uploader("Carica logo / firma (JPG o PNG)", 
                                 type=["jpg", "jpeg", "png"])

margin_x = st.number_input("Margine sinistro (pt)",  value=30)
margin_y = st.number_input("Margine inferiore (pt)", value=35)
signature_width = st.number_input("Larghezza firma (pt)", value=100)

if uploaded_files and uploaded_logo and st.button("Applica firma"):
    with tempfile.TemporaryDirectory() as tmpdir:
        logo_path = os.path.join(tmpdir, uploaded_logo.name)
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.read())

        signed_files = []

        for file in uploaded_files:
            input_path = os.path.join(tmpdir, file.name)
            with open(input_path, "wb") as f:
                f.write(file.read())

            ext = os.path.splitext(file.name)[1].lower()

            # === Caso PDF ===
            if ext == ".pdf":
                doc = fitz.open(input_path)
                signature_img = fitz.open(logo_path)
                rect_img = signature_img[0].rect
                ratio = rect_img.height / rect_img.width
                signature_height = signature_width * ratio

                for page in doc:
                    page_width = page.rect.width
                    page_height = page.rect.height
                    x0 = margin_x
                    y0 = page_height - signature_height - margin_y
                    x1 = x0 + signature_width
                    y1 = y0 + signature_height
                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.insert_image(rect, filename=logo_path, keep_proportion=True)

                output_path = os.path.join(tmpdir, f"firmato_{file.name}")
                doc.save(output_path)
                doc.close()

            # === Caso Immagine ===
            elif ext in [".jpg", ".jpeg", ".png"]:
                img = Image.open(input_path).convert("RGBA")
                logo = Image.open(logo_path).convert("RGBA")

                # Ridimensiona logo
                ratio = logo.height / logo.width
                logo_w = signature_width
                logo_h = int(logo_w * ratio)
                logo = logo.resize((int(logo_w), int(logo_h)))

                # Posizione in basso a sinistra
                x = int(margin_x)
                y = img.height - logo_h - int(margin_y)

                img.paste(logo, (x, y), logo)
                output_path = os.path.join(tmpdir, f"firmato_{file.name}")
                img.convert("RGB").save(output_path)

            with open(output_path, "rb") as f:
                signed_files.append((os.path.basename(output_path), f.read()))

        st.success("✅ Firma completata con successo!")
        for name, data in signed_files:
            st.download_button(f"⬇️ Scarica {name}", data, file_name=name)

