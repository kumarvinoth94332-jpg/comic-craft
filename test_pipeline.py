"""
test_pipeline.py - Verification script for ComicCraft pipeline.
"""
import os
import pytest
from pathlib import Path

from gemini_flash import generate_outline
from gemini_pro import generate_story
from image_generator import generate_image
from layout_builder import build_comic_layout
from exporters import save_pdf
from fastapi.testclient import TestClient
from app.main import app


def test_ai_comic_pipeline():
    # 1. Outline
    outline = generate_outline(
        story_prompt="A brave fox exploring an enchanted forest",
        character_name="Rusty",
        setting="Forest",
        tone="Light-hearted",
        art_style="Comic Book",
    )
    assert len(outline) == 5, f"Expected 5 panels, got {len(outline)}"
    assert "panel" in outline[0]
    assert "title" in outline[0]
    assert "scene_description" in outline[0]
    assert "image_prompt" in outline[0]

    # 2. Story
    story = generate_story(
        outline=outline,
        story_prompt="A brave fox exploring an enchanted forest",
        character_name="Rusty",
        setting="Forest",
        tone="Light-hearted",
        art_style="Comic Book",
    )
    assert len(story) == 5
    assert "narration" in story[0]
    assert "dialogue" in story[0]
    assert "caption" in story[0]

    # 3. Image Generation
    for panel in story:
        panel_num = panel.get("panel", 1)
        prompt = panel.get("image_prompt", "Fox in forest")
        img_url = generate_image(prompt=prompt, panel_num=panel_num, art_style="Comic Book")
        assert img_url.startswith("/static/panels/")
        panel["image_url"] = img_url

    # 4. Layout
    metadata = {
        "character_name": "Rusty",
        "story_prompt": "A brave fox exploring an enchanted forest",
        "setting": "Forest",
        "tone": "Light-hearted",
        "art_style": "Comic Book",
    }
    layout = build_comic_layout(story, metadata)
    assert layout["total_panels"] == 5
    assert len(layout["panels"]) == 5
    assert layout["title"] != ""

    # 5. PDF Export
    pdf_url = save_pdf(comic_layout=layout)
    assert pdf_url.startswith("/static/exports/")
    pdf_file = Path("." + pdf_url)
    assert pdf_file.exists(), f"PDF file not found at {pdf_file}"
    assert pdf_file.stat().st_size > 1000, "PDF file is too small or corrupt"
    print("\n[SUCCESS] AI Comic Pipeline passed all checks!")


def test_fastapi_endpoints():
    client = TestClient(app)

    # Health
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # Homepage
    res = client.get("/")
    assert res.status_code == 200
    assert "COMICCRAFT" in res.text
    assert "GENERATE COMIC" in res.text

    # Developer test image
    res = client.get("/test-image?prompt=Fox+adventurer&art_style=Anime&panel_num=1")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Export success page
    res = client.get("/export-success?filename=test.pdf&title=Rusty+Adventure")
    assert res.status_code == 200
    assert "YOUR COMIC IS READY!" in res.text

    print("\n[SUCCESS] FastAPI endpoints passed all checks!")


if __name__ == "__main__":
    test_ai_comic_pipeline()
    test_fastapi_endpoints()
