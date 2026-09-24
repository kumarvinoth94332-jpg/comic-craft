"""
app/routes.py - FastAPI Application Routes.
Handles comic generation workflow, template rendering, JSON API, image testing, and PDF downloads.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Core AI & Service Modules
from gemini_flash import generate_outline
from gemini_pro import generate_story
from image_generator import generate_image
from layout_builder import build_comic_layout
from exporters import save_pdf

logger = logging.getLogger("comiccraft.routes")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STATIC_EXPORTS_DIR = STATIC_DIR / "exports"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router = APIRouter()


# -------------------------------------------------------------------
# Pydantic Request Models
# -------------------------------------------------------------------

class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=3, description="Story prompt or premise")
    character_name: str = Field(..., min_length=1, description="Hero/Protagonist name")
    setting: str = Field(..., description="Story setting: Forest, School, City, Space, or custom")
    custom_setting: Optional[str] = Field(None, description="Optional custom setting description")
    tone: str = Field("Light-hearted", description="Light-hearted, Dramatic, Poetic, Funny")
    art_style: str = Field("Comic Book", description="Anime, Pixel Art, Comic Book, Realistic")


# -------------------------------------------------------------------
# 1. Homepage Route (GET /)
# -------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the modern AI creative studio homepage."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft – AI Comic Story Creator",
        },
    )


# -------------------------------------------------------------------
# 2. Comic Generation Route (POST /generate)
# -------------------------------------------------------------------

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    custom_setting: Optional[str] = Form(None),
    tone: str = Form("Light-hearted"),
    art_style: str = Form("Comic Book"),
):
    """
    Form submission workflow:
    1. Validate inputs
    2. generate_outline() -> 5-panel structured outline
    3. generate_story() -> narration, dialogue, captions
    4. generate_image() -> illustrations for each of the 5 panels
    5. build_comic_layout() -> structured comic object
    6. save_pdf() -> multi-page comic PDF
    7. Render comic_preview.html
    """
    # 1. Validation
    prompt_clean = story_prompt.strip()
    char_clean = character_name.strip()

    if not prompt_clean:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter a valid story prompt.",
            },
            status_code=400,
        )

    if not char_clean:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter your hero's name.",
            },
            status_code=400,
        )

    # Determine final setting
    final_setting = custom_setting.strip() if (setting.lower() == "custom" and custom_setting and custom_setting.strip()) else setting.strip()
    if not final_setting:
        final_setting = "Enchanted Forest"

    logger.info(f"Generating comic for character: {char_clean} in setting: {final_setting} (Tone: {tone}, Style: {art_style})")

    try:
        # Step 2: Generate 5-panel outline (Gemini Flash)
        raw_outline = generate_outline(
            story_prompt=prompt_clean,
            character_name=char_clean,
            setting=final_setting,
            tone=tone,
            art_style=art_style,
        )

        # Step 3: Enrich with narration, dialogue, and comic captions (Gemini Pro)
        story_panels = generate_story(
            outline=raw_outline,
            story_prompt=prompt_clean,
            character_name=char_clean,
            setting=final_setting,
            tone=tone,
            art_style=art_style,
        )

        # Step 4: Generate comic illustration for every panel
        for i, panel in enumerate(story_panels):
            panel_num = panel.get("panel", i + 1)
            img_prompt = panel.get("image_prompt", f"Illustration of {char_clean} in {final_setting}")
            image_url = generate_image(prompt=img_prompt, panel_num=panel_num, art_style=art_style)
            panel["image_url"] = image_url

        # Step 5: Build unified comic layout
        metadata = {
            "character_name": char_clean,
            "story_prompt": prompt_clean,
            "setting": final_setting,
            "tone": tone,
            "art_style": art_style,
        }
        comic_layout = build_comic_layout(panels_data=story_panels, metadata=metadata)

        # Step 6: Generate professional PDF export
        pdf_path = save_pdf(comic_layout=comic_layout)
        pdf_filename = Path(pdf_path).name

        # Step 7: Render the comic preview page
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic_layout,
                "panels": comic_layout["panels"],
                "title": comic_layout["title"],
                "metadata": comic_layout["metadata"],
                "pdf_path": pdf_path,
                "pdf_filename": pdf_filename,
            },
        )

    except Exception as e:
        logger.exception(f"Error during comic generation: {e}")
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"An error occurred while crafting your comic: {str(e)}",
            },
            status_code=500,
        )


# -------------------------------------------------------------------
# 3. JSON API Endpoint (POST /generate-comic/json)
# -------------------------------------------------------------------

@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    """
    API endpoint returning structured comic layout data and PDF path.
    """
    final_setting = req.custom_setting.strip() if (req.setting.lower() == "custom" and req.custom_setting) else req.setting.strip()
    if not final_setting:
        final_setting = "Enchanted Forest"

    try:
        # Outline
        raw_outline = generate_outline(
            story_prompt=req.story_prompt,
            character_name=req.character_name,
            setting=final_setting,
            tone=req.tone,
            art_style=req.art_style,
        )

        # Story
        story_panels = generate_story(
            outline=raw_outline,
            story_prompt=req.story_prompt,
            character_name=req.character_name,
            setting=final_setting,
            tone=req.tone,
            art_style=req.art_style,
        )

        # Images
        for i, panel in enumerate(story_panels):
            panel_num = panel.get("panel", i + 1)
            img_prompt = panel.get("image_prompt", "")
            image_url = generate_image(prompt=img_prompt, panel_num=panel_num, art_style=req.art_style)
            panel["image_url"] = image_url

        # Layout
        metadata = {
            "character_name": req.character_name,
            "story_prompt": req.story_prompt,
            "setting": final_setting,
            "tone": req.tone,
            "art_style": req.art_style,
        }
        comic_layout = build_comic_layout(panels_data=story_panels, metadata=metadata)

        # PDF
        pdf_path = save_pdf(comic_layout=comic_layout)

        return JSONResponse(
            content={
                "status": "success",
                "comic_layout": comic_layout,
                "generated_panels": comic_layout["panels"],
                "pdf_path": pdf_path,
                "pdf_url": pdf_path,
            }
        )
    except Exception as e:
        logger.exception(f"JSON comic generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# 4. Developer Testing Endpoint (GET /test-image)
# -------------------------------------------------------------------

@router.get("/test-image")
async def test_image(
    prompt: str = Query("A courageous cybernetic fox exploring a neon cyberpunk city", description="Image prompt"),
    art_style: str = Query("Comic Book", description="Art style: Comic Book, Anime, Pixel Art, Realistic"),
    panel_num: int = Query(1, ge=1, le=5, description="Panel number 1-5"),
):
    """
    Developer testing endpoint for verifying image generation.
    Returns JSON with the generated image URL and test metadata.
    """
    try:
        image_url = generate_image(prompt=prompt, panel_num=panel_num, art_style=art_style)
        return {
            "status": "success",
            "prompt": prompt,
            "art_style": art_style,
            "panel_num": panel_num,
            "image_url": image_url,
            "full_preview_url": f"http://127.0.0.1:8000{image_url}",
        }
    except Exception as e:
        logger.exception(f"Test image error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# 5. Direct PDF Download Route (GET /download-pdf/{filename})
# -------------------------------------------------------------------

@router.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """
    Serves the PDF file as a downloadable attachment.
    """
    safe_filename = Path(filename).name
    file_path = STATIC_EXPORTS_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested PDF file not found.")

    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )


# -------------------------------------------------------------------
# 6. Export Success Page (GET /export-success)
# -------------------------------------------------------------------

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    filename: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
):
    """
    Displays the successful comic creation and download confirmation page.
    """
    pdf_url = f"/download-pdf/{filename}" if filename else None
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "filename": filename,
            "pdf_url": pdf_url,
            "title": title or "Your Comic",
        },
    )
