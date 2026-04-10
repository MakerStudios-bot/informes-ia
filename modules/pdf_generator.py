from pathlib import Path
from fpdf import FPDF
from html.parser import HTMLParser
import re

OUTPUT_DIR = Path("output_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

class HTMLtoText(HTMLParser):
    """Convierte HTML simple a texto para PDF"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.current_section = None

    def handle_starttag(self, tag, attrs):
        if tag in ['h1', 'h2', 'h3']:
            self.text.append('\n')
        elif tag == 'p':
            pass
        elif tag == 'li':
            self.text.append('\n• ')

    def handle_data(self, data):
        data = data.strip()
        if data:
            self.text.append(data + ' ')

    def handle_endtag(self, tag):
        if tag in ['p', 'div']:
            self.text.append('\n')
        elif tag in ['h1', 'h2', 'h3']:
            self.text.append('\n')

    def get_text(self):
        return ''.join(self.text).strip()

async def generate_pdf(html: str, informe_id: str) -> str:
    # Extraer texto del HTML
    parser = HTMLtoText()
    parser.feed(html)
    text = parser.get_text()

    # Limpiar caracteres especiales que causan problemas
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Agregar contenido (limitar a 3000 caracteres para que quepa en PDF)
    content = text[:3000]
    pdf.multi_cell(0, 5, content, align="L")

    pdf_path = OUTPUT_DIR / f"{informe_id}.pdf"
    pdf.output(str(pdf_path))
    print(f"  PDF generado: {pdf_path}")
    return str(pdf_path)
