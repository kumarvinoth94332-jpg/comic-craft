"""
exporters.py - PDF Comic Book Exporter.
Generates an attractive multi-page comic book PDF using fpdf2.
Each page features:
- Issue Header & Comic Title
- Panel Number & Title Banner
- Comic Artwork Illustration
- Scene Description
- Comic Caption
- Narration and Character Dialogue
"""

import datetime
import os
import re
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from fpdf import FPDF

logger = logging.getLogger("comiccraft.exporters")

BASE_DIR = Path(__file__).resolve().parent
STATIC_EXPORTS_DIR = BASE_DIR / "static" / "exports"
STATIC_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _clean_pdf_text(text: str) -> str:
    """Replaces non-latin1 characters with close ASCII equivalents to prevent PDF encoding errors."""
    if not text:
        return ""
    # Common typography replacements
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
        "✨": "*",
        "🎉": "*",
        "←": "<-",
        "→": "->",
        "⬇": "v",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Encode to latin-1 safe string
    return text.encode("latin-1", "replace").decode("latin-1")


class ComicPDF(FPDF):
    def __init__(self, comic_title: str, character_name: str, art_style: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.comic_title = _clean_pdf_text(comic_title)
        self.character_name = _clean_pdf_text(character_name)
        self.art_style = _clean_pdf_text(art_style)
        self.set_auto_page_break(auto=False)

    def header(self):
        # Dark Comic Banner Header
        self.set_fill_color(15, 17, 26)  # Dark purple-navy
        self.rect(0, 0, 210, 18, "F")

        # Top accent bar
        self.set_fill_color(139, 92, 246)  # Purple neon accent
        self.rect(0, 0, 210, 2, "F")

        self.set_xy(10, 4)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(240, 240, 255)
        self.cell(100, 10, "COMICCRAFT AI - ISSUE #01", ln=0, align="L")

        self.set_xy(100, 4)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(160, 170, 200)
        self.cell(100, 10, f"{self.character_name} | {self.art_style}", ln=1, align="R")

    def footer(self):
        # Dark Comic Banner Footer
        self.set_fill_color(15, 17, 26)
        self.rect(0, 285, 210, 12, "F")

        self.set_xy(10, 286)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(139, 92, 246)
        self.cell(100, 10, "GENERATED WITH COMICCRAFT AI", ln=0, align="L")

        self.set_xy(110, 286)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(180, 190, 210)
        self.cell(90, 10, f"Page {self.page_no()}", ln=1, align="R")


def save_pdf(comic_layout: Dict[str, Any], output_filename: Optional[str] = None) -> str:
    """
    Generates a professional multi-page comic book PDF from comic layout data.
    
    Args:
        comic_layout: dictionary containing 'panels', 'title', and 'metadata'
        output_filename: optional custom filename
        
    Returns:
        Relative web URL path to the generated PDF (e.g., "/static/exports/comic_...pdf")
    """
    title = comic_layout.get("title", "ComicCraft Story")
    metadata = comic_layout.get("metadata", {})
    character_name = metadata.get("character_name", "Hero")
    art_style = metadata.get("art_style", "Comic Book")
    panels = comic_layout.get("panels", [])

    pdf = ComicPDF(
        comic_title=title,
        character_name=character_name,
        art_style=art_style,
    )

    for p in panels:
        pdf.add_page()

        panel_num = p.get("panel", 1)
        panel_title = _clean_pdf_text(p.get("title", f"Panel {panel_num}"))
        scene_desc = _clean_pdf_text(p.get("scene_description", ""))
        caption = _clean_pdf_text(p.get("caption", f"PANEL {panel_num}"))
        narration = _clean_pdf_text(p.get("narration", ""))
        dialogue = _clean_pdf_text(p.get("dialogue", ""))
        image_path = p.get("image_path", "")

        # 1. Panel Header Card
        pdf.set_xy(10, 22)
        pdf.set_fill_color(30, 27, 75)  # Indigo
        pdf.rect(10, 22, 190, 14, "F")
        pdf.set_draw_color(139, 92, 246)
        pdf.set_line_width(0.8)
        pdf.rect(10, 22, 190, 14, "D")

        # Badge
        pdf.set_fill_color(139, 92, 246)
        pdf.rect(12, 24, 28, 10, "F")
        pdf.set_xy(12, 24)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(28, 10, f"PANEL {panel_num}", align="C")

        # Title
        pdf.set_xy(44, 24)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(240, 240, 255)
        pdf.cell(150, 10, panel_title.upper(), align="L")

        # 2. Comic Illustration Frame
        img_x, img_y = 15, 39
        img_w, img_h = 180, 115

        # Check if image file exists
        if image_path and os.path.exists(image_path):
            try:
                pdf.image(image_path, x=img_x, y=img_y, w=img_w, h=img_h)
            except Exception as e:
                logger.error(f"Failed to embed image {image_path}: {e}")
                pdf.set_fill_color(20, 24, 39)
                pdf.rect(img_x, img_y, img_w, img_h, "F")
                pdf.set_xy(img_x, img_y + 40)
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(150, 160, 180)
                pdf.cell(img_w, 10, "[ Comic Illustration ]", align="C")
        else:
            pdf.set_fill_color(20, 24, 39)
            pdf.rect(img_x, img_y, img_w, img_h, "F")
            pdf.set_xy(img_x, img_y + 40)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(150, 160, 180)
            pdf.cell(img_w, 10, "[ Comic Illustration ]", align="C")

        # Comic Frame Border
        pdf.set_draw_color(15, 17, 26)
        pdf.set_line_width(1.5)
        pdf.rect(img_x, img_y, img_w, img_h, "D")

        # 3. Comic Caption Banner (Overlay style below image)
        cur_y = img_y + img_h + 3
        if caption:
            pdf.set_fill_color(255, 230, 0)  # Classic Comic Yellow
            pdf.set_draw_color(10, 10, 10)
            pdf.set_line_width(0.6)
            pdf.rect(15, cur_y, 180, 8, "FD")
            pdf.set_xy(18, cur_y)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(15, 15, 15)
            pdf.cell(174, 8, f"CAPTION: {caption.upper()}", align="L")
            cur_y += 11

        # 4. Narration Box
        if narration:
            pdf.set_fill_color(248, 250, 252)  # Light parchment
            pdf.set_draw_color(203, 213, 225)
            pdf.set_line_width(0.4)
            pdf.rect(15, cur_y, 180, 25, "FD")

            # Left accent stripe
            pdf.set_fill_color(99, 102, 241)
            pdf.rect(15, cur_y, 3, 25, "F")

            pdf.set_xy(21, cur_y + 2)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(79, 70, 229)
            pdf.cell(170, 5, "NARRATION", ln=1)

            pdf.set_xy(21, cur_y + 7)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(170, 5, narration)
            cur_y += 28

        # 5. Dialogue Speech Bubble / Box
        if dialogue:
            pdf.set_fill_color(240, 253, 250)  # Mint/Cyan tint
            pdf.set_draw_color(45, 212, 191)
            pdf.set_line_width(0.5)
            pdf.rect(15, cur_y, 180, 24, "FD")

            pdf.set_fill_color(13, 148, 136)
            pdf.rect(15, cur_y, 3, 24, "F")

            pdf.set_xy(21, cur_y + 2)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(13, 148, 136)
            pdf.cell(170, 5, "DIALOGUE", ln=1)

            pdf.set_xy(21, cur_y + 7)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(170, 5, dialogue)
            cur_y += 26

        # 6. Scene Description & Image Prompt (Footer info on page)
        if scene_desc:
            pdf.set_xy(15, cur_y + 1)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 116, 139)
            desc_snip = f"Scene Note: {scene_desc}"
            if len(desc_snip) > 170:
                desc_snip = desc_snip[:167] + "..."
            pdf.cell(180, 4, desc_snip, ln=1, align="L")

    # Generate timestamped filename
    if not output_filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^a-zA-Z0-9]", "_", character_name.lower())[:12]
        output_filename = f"comic_{slug}_{timestamp}_{uuid.uuid4().hex[:4]}.pdf"

    output_path = STATIC_EXPORTS_DIR / output_filename
    pdf.output(str(output_path))
    logger.info(f"Successfully generated comic PDF at: {output_path}")

    return f"/static/exports/{output_filename}"
