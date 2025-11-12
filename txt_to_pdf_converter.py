"""
Convert TXT contract files to PDF format
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from langchain.chains.combine_documents_chain import create_stuff_documents_chain



def txt_to_pdf(txt_file: str, pdf_file: str):
    """Convert a TXT file to PDF"""
    
    # Read the text file
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    
    story.append(Paragraph(Path(txt_file).stem.replace('_', ' ').title(), title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add content
    body_style = styles['BodyText']
    
    # Split by lines and create paragraphs
    for line in content.split('\n'):
        if line.strip():
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {pdf_file}")

def convert_all_txt_to_pdf(input_folder: str = "./contracts", output_folder: str = "./contracts_pdf"):
    """Convert all TXT files in a folder to PDF"""
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Create output folder
    output_path.mkdir(exist_ok=True)
    
    print("📄 Converting TXT files to PDF...\n")
    
    txt_files = list(input_path.glob("*.txt"))
    
    if not txt_files:
        print("❌ No TXT files found!")
        return
    
    for txt_file in txt_files:
        pdf_file = output_path / f"{txt_file.stem}.pdf"
        try:
            txt_to_pdf(str(txt_file), str(pdf_file))
        except Exception as e:
            print(f"❌ Error converting {txt_file.name}: {e}")
    
    print(f"\n✅ Converted {len(txt_files)} files to PDF")
    print(f"📁 Saved to: {output_path.resolve()}")

if __name__ == "__main__":
    # Install: pip install reportlab
    convert_all_txt_to_pdf()