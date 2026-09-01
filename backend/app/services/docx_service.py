import io
import re
from typing import Dict, Any, Tuple
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import mammoth
    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False

from app.services.resume_parser import extract_text_from_file


def convert_pdf_to_exact_html(file_path: str) -> Tuple[str, str]:
    """
    Extract high-fidelity exact HTML from PDF preserving exact coordinates,
    font families, sizes, colors, margins, and vector separator lines without modifying the original layout.
    """
    if not PYMUPDF_AVAILABLE:
        raw = extract_text_from_file(file_path) or ""
        return text_to_exact_html(raw), raw

    try:
        doc = fitz.open(file_path)
        pages_html = []
        full_text_list = []

        for page_idx, page in enumerate(doc):
            rect = page.rect
            w, h = rect.width, rect.height

            # Extract drawings / lines (e.g. section separator lines)
            lines_html = []
            try:
                drawings = page.get_drawings()
                for d in drawings:
                    r = d.get('rect')
                    if r and r.height <= 4 and r.width > 15:
                        color = d.get('color')
                        hex_color = '#000000'
                        if color and len(color) >= 3:
                            hex_color = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"
                        lines_html.append(
                            f'<div style="position: absolute; top: {r.y0:.1f}pt; left: {r.x0:.1f}pt; width: {r.width:.1f}pt; height: 1px; background-color: {hex_color}; pointer-events: none;"></div>'
                        )
            except Exception:
                pass

            # Extract HTML text elements
            page_raw_html = page.get_text('html')

            # Inject position: absolute; margin: 0; white-space: pre-wrap; into all <p> elements
            page_fixed_html = re.sub(
                r'<p style="([^"]*)"',
                r'<p style="position: absolute; margin: 0; white-space: pre-wrap; \1"',
                page_raw_html
            )

            # Strip outermost <div id="page..."> ... </div> so we control page styling
            inner = re.sub(r'^<div[^>]*>', '', page_fixed_html.strip(), flags=re.IGNORECASE)
            inner = re.sub(r'</div>$', '', inner.strip(), flags=re.IGNORECASE)

            page_container = f'''<div class="pdf-exact-page" data-page="{page_idx+1}" style="position: relative; width: {w:.1f}pt; min-width: {w:.1f}pt; height: {h:.1f}pt; min-height: {h:.1f}pt; margin: 0 auto 28px auto; background: #ffffff; color: #000000; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); border: 1px solid #cbd5e1; overflow: visible; box-sizing: border-box;">
{"".join(lines_html)}
{inner}
</div>'''
            pages_html.append(page_container)
            full_text_list.append(page.get_text())

        doc.close()
        exact_html = "\n".join(pages_html)
        full_text = "\n".join(full_text_list)
        return exact_html, full_text
    except Exception as e:
        print(f"PyMuPDF PDF exact extraction error: {e}")
        raw = extract_text_from_file(file_path) or ""
        return text_to_exact_html(raw), raw


def convert_docx_to_rich_html(file_path: str) -> Tuple[str, str]:
    """
    Convert Word (.docx) document to rich HTML preserving tables, bolding,
    italics, headings, bullet lists, and original structure.
    """
    if not MAMMOTH_AVAILABLE:
        raw = extract_text_from_file(file_path) or ""
        return text_to_exact_html(raw), raw

    try:
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value
            raw_text = extract_text_from_file(file_path) or ""

            wrapped_html = f'''<div class="docx-exact-page" style="width: 100%; max-width: 612pt; min-height: 792pt; margin: 0 auto; background: #ffffff; color: #0f172a; padding: 48px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; font-family: Calibri, Arial, sans-serif; font-size: 11pt; line-height: 1.45;">
{html}
</div>'''
            return wrapped_html, raw_text
    except Exception as e:
        print(f"Mammoth docx conversion error: {e}")
        raw = extract_text_from_file(file_path) or ""
        return text_to_exact_html(raw), raw


def text_to_exact_html(raw_text: str) -> str:
    """
    Format raw text into clean, exact-layout HTML preserving every line break,
    indent, bold title, and bullet point without forcing any artificial template.
    """
    if not raw_text:
        return '<p class="text-slate-400 italic">Click to start editing your resume...</p>'

    lines = raw_text.split('\n')
    formatted_blocks = []

    section_headers = [
        "summary", "professional summary", "technical skills", "skills",
        "work experience", "experience", "employment history", "projects",
        "key projects", "education", "certifications", "awards", "leadership"
    ]

    first_line = True
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_blocks.append('<div style="height: 8px;"></div>')
            continue

        clean_lower = stripped.lower().strip(":- ")

        # Candidate name (first non-empty line)
        if first_line:
            formatted_blocks.append(
                f'<div style="font-size: 22px; font-weight: 800; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; color: #0f172a;">{stripped}</div>'
            )
            first_line = False
            continue

        # Contact line
        if ('@' in stripped or 'github' in stripped.lower() or 'leetcode' in stripped.lower() or '|' in stripped) and len(formatted_blocks) <= 3:
            formatted_blocks.append(
                f'<div style="font-size: 11px; text-align: center; color: #475569; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #cbd5e1;">{stripped}</div>'
            )
            continue

        # Section Header
        if clean_lower in section_headers or (len(stripped) < 35 and stripped.isupper() and not stripped.startswith(('•', '-', '*'))):
            formatted_blocks.append(
                f'<div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.75px; color: #0f172a; margin-top: 14px; margin-bottom: 4px; padding-bottom: 2px; border-bottom: 1.5px solid #0f172a;">{stripped}</div>'
            )
            continue

        # Bullet point line
        if stripped.startswith(('•', '-', '*', '–', '—', '+')) or re.match(r'^\d+\.\s', stripped):
            bullet_body = re.sub(r'^[•\-\*–—\+\d\.]\s*', '', stripped)
            formatted_blocks.append(
                f'<div style="display: flex; align-items: baseline; font-size: 11.5px; line-height: 1.5; color: #1e293b; margin-bottom: 3px; padding-left: 12px;"><span style="margin-right: 8px; font-weight: bold;">•</span><span>{bullet_body}</span></div>'
            )
            continue

        # Experience / Project Title line with dates/location
        if any(sep in stripped for sep in ['|', '–', '—', '•']) and len(stripped) < 100:
            formatted_blocks.append(
                f'<div style="font-size: 11.5px; font-weight: 700; color: #0f172a; margin-top: 6px; margin-bottom: 2px;">{stripped}</div>'
            )
            continue

        # Normal text paragraph
        formatted_blocks.append(
            f'<div style="font-size: 11.5px; line-height: 1.5; color: #1e293b; margin-bottom: 2px;">{stripped}</div>'
        )

    return "\n".join(formatted_blocks)


def convert_document_to_rich_doc(file_path: str) -> Dict[str, Any]:
    """
    Parse a PDF or Word document into structured exact-layout HTML locally and instantly.
    Preserves 100% exact original coordinates, fonts, tables, and styling.
    """
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        exact_html, raw_text = convert_pdf_to_exact_html(file_path)
        doc_type = "pdf"
    elif lower.endswith(".docx"):
        exact_html, raw_text = convert_docx_to_rich_html(file_path)
        doc_type = "docx"
    else:
        raw_text = extract_text_from_file(file_path) or ""
        exact_html = text_to_exact_html(raw_text)
        doc_type = "text"

    return {
        "raw_text": raw_text,
        "rich_html": exact_html,
        "exact_html": exact_html,
        "document_type": doc_type,
        "word_count": len(raw_text.split())
    }


def generate_docx_from_document(raw_text: str, candidate_name: str = "Candidate_Resume") -> io.BytesIO:
    """
    Generate an authentic Microsoft Word (.docx) document from edited resume text.
    """
    doc = Document()

    # Set standard 0.75 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    section_headers = [
        "summary", "professional summary", "technical skills", "skills",
        "work experience", "experience", "employment history", "projects",
        "key projects", "education", "certifications", "awards", "leadership"
    ]

    lines = raw_text.split('\n')
    first_line = True

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        clean_lower = stripped.lower().strip(":- ")

        # Document Title / Candidate Name
        if first_line:
            p = doc.add_paragraph()
            run = p.add_run(stripped)
            run.font.name = 'Calibri'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(4)
            first_line = False
            continue

        # Section Header
        if clean_lower in section_headers or (len(stripped) < 35 and stripped.isupper()):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(2)
            run = h.add_run(stripped.upper())
            run.font.name = 'Calibri'
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            continue

        # Bullet List Item
        if stripped.startswith(('•', '-', '*', '–', '—', '+')) or re.match(r'^\d+\.\s', stripped):
            bullet_text = re.sub(r'^[•\-\*–—\+\d\.]\s*', '', stripped)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(0)
            run = p.add_run(bullet_text)
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            continue

        # Standard Paragraph / Role Heading
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(stripped)
        run.font.name = 'Calibri'
        run.font.size = Pt(10)
        if any(sep in stripped for sep in ['|', '–', '—', '•']) and len(stripped) < 80:
            run.font.bold = True

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


text_to_rich_html = text_to_exact_html
