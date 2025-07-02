import streamlit as st
from pymongo import MongoClient
import io
import base64
from fpdf import FPDF
from PIL import Image
import qrcode
from base64 import b64encode

# --- MongoDB connection ---
client = MongoClient("mongodb+srv://bibliotecaluizcarlos:FGVIlVhDcUDuQddG@cluster0.hth6xs5.mongodb.net/?retryWrites=true&w=majority")
db = client["controle_uso"]

# --- Estilos militares ---
def load_styles(imagem_path):
    with open(imagem_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}

    div.stButton > button {{
        background-color: #556B2F;
        color: #fff;
        border: 2px solid #333;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.5em 1.5em;
        font-size: 16px;
    }}
    div.stButton > button:hover {{
        background-color: #6B8E23;
        color: #fff;
        border-color: #000;
    }}

    .stTextInput > div > div > input {{
        background-color: rgba(255,255,255,0.8);
        color: #333;
        font-weight: bold;
    }}
    .stSelectbox > div > div > div > div {{
        background-color: rgba(255,255,255,0.8);
        color: #333;
        font-weight: bold;
    }}
    .stTimeInput > div > div > input {{
        background-color: rgba(255,255,255,0.8);
        color: #333;
        font-weight: bold;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: #556B2F;
        font-weight: bold;
    }}

    .stMarkdown p {{
        color: #ffffff;
        font-weight: bold;
        text-shadow: 1px 1px 2px #000;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Funções auxiliares ---
def generate_qrcode(data):
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def pil_image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- Impressão QR Codes ---
def imprimir_qrcodes():
    st.subheader("🖨️ Impressão de QR Codes")

    opcao = st.radio("Escolha o que deseja imprimir:", ["Mesas", "Equipamentos"])

    if opcao == "Mesas":
        dados = list(db.mesas.find())
        titulo = "Mesa"
    else:
        dados = list(db.equipamentos.find())
        titulo = "Equipamento"

    if not dados:
        st.info(f"Nenhum dado cadastrado para {titulo.lower()}s.")
        return

    imagens = []
    for item in dados:
        if titulo == "Mesa":
            numero = item.get("numero", None)
            texto = f"Mesa {numero}" if numero else "Mesa ?"
        else:
            nome = item.get("nome", None)
            numero = item.get("numero", None)
            texto = f"{nome} #{numero}" if nome and numero else f"{nome if nome else 'Equipamento'} #{numero if numero else '?'}"
        img = generate_qrcode(texto)
        imagens.append((texto, img))

    st.write("🔲 QR Codes Gerados:")
    cols = st.columns(3)
    for i, (texto, img) in enumerate(imagens):
        with cols[i % 3]:
            st.image(pil_image_to_bytes(img), caption=texto, width=120)

    # PDF A4
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    num_cols = 3
    cell_w = 60
    cell_h = 60
    margin_x = 10
    margin_y = 20
    x = margin_x
    y = margin_y

    for i, (texto, img) in enumerate(imagens):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        pdf.image(buf, x=x + 5, y=y, w=cell_w - 10)
        pdf.set_xy(x, y + cell_h - 5)
        pdf.multi_cell(cell_w, 5, texto, align="C")

        x += cell_w
        if (i + 1) % num_cols == 0:
            x = margin_x
            y += cell_h + 10
            if y + cell_h > 280:
                pdf.add_page()
                y = margin_y

    pdf_bytes = bytes(pdf.output(dest="S"))
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="qrcodes_{titulo.lower()}.pdf">📥 Baixar QR Codes em PDF (A4)</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Main ---
def main():
    st.set_page_config(page_title="Controle de Uso", layout="wide")

    # Aplica estilos militares
    load_styles("fundo_militar.png")

    st.sidebar.image("BRASÃO.png", width=120)

    menu_opcoes = ["🖨️ Impressão QR Codes", "🚪 Sair"]
    menu = st.sidebar.radio("Menu", menu_opcoes)

    if menu == "🖨️ Impressão QR Codes":
        imprimir_qrcodes()
    elif menu == "🚪 Sair":
        if st.sidebar.button("🚪 Clique aqui para Sair"):
            for key in ["logado", "usuario_admin", "usuario"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
