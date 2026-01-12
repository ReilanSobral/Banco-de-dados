
import markdown
from fpdf import FPDF
import re

def normalize_text(text):
    """Substitui caracteres problemáticos para ISO-8859-1 (Latin-1)"""
    replacements = {
        '–': '-', '—': '-',
        '“': '"', '”': '"',
        "’": "'", "‘": "'",
        '•': '-',
        '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Tenta codificar para latin-1, substituindo erros se persistirem
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ONG Vida Plena - Relatorio Tecnico', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        label = normalize_text(label)
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        body = normalize_text(body)
        self.multi_cell(0, 5, body)
        self.ln()

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

try:
    with open('relatorio tecnico.md', 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        if line.startswith('#'):
            clean_line = line.replace('#', '').strip()
            pdf.chapter_title(clean_line)
        elif line.startswith('![alt'):
            match = re.search(r'\((.*?)\)', line)
            if match:
                img_path = match.group(1)
                try:
                    # Centralizar e limitar tamanho
                    # A4 width = 210mm. Margins ~10mm. Usable ~190mm
                    pdf.image(img_path, w=140, x=35) 
                    pdf.ln(5)
                except:
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 5, f"[Imagem nao encontrada: {img_path}]", 0, 1)
        else:
            pdf.chapter_body(line)

    pdf.output('RELATORIO_TECNICO_FINAL.pdf')
    print("PDF Gerado com sucesso!")

except Exception as e:
    print(f"Erro CRITICO: {e}")
