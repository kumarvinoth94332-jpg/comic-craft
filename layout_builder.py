"""
layout_builder.py - Comic Layout Assembly Engine.
Combines generated panel data, story dialogue, narration, and illustrations
into a unified layout data structure for Jinja2 template rendering and PDF generation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import datetime

BASE_DIR = Path(__file__).resolve().parent


def build_comic_layout(
    panels_data: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Matches each generated image with its corresponding:
    - panel number
    - title
    - scene description
    - caption
    - narration/dialogue
    - image prompt
    - image url and local filesystem path

    Returns a clean dictionary containing:
    - 'panels': list of sanitized, complete panel dictionaries
    - 'metadata': story metadata (prompt, character, setting, tone, art_style, created_at)
    - 'title': generated or derived comic title
    - 'total_panels': count of panels (5)
    """
    metadata = metadata or {}
    character_name = metadata.get("character_name", "Hero")
    story_prompt = metadata.get("story_prompt", "An epic adventure")
    setting = metadata.get("setting", "Unknown Realm")
    tone = metadata.get("tone", "Dramatic")
    art_style = metadata.get("art_style", "Comic Book")

    # Generate an epic comic title if not provided
    comic_title = metadata.get("comic_title")
    if not comic_title:
        first_panel_title = panels_data[0].get("title", "") if panels_data else ""
        if first_panel_title and first_panel_title.lower() not in ["panel 1", "the beginning"]:
            comic_title = f"{character_name}: {first_panel_title}"
        else:
            comic_title = f"The Chronicles of {character_name} in {setting}"

    clean_panels: List[Dict[str, Any]] = []

    for i, p in enumerate(panels_data):
        panel_num = p.get("panel", i + 1)
        title = p.get("title", f"Panel {panel_num}")
        scene_desc = p.get("scene_description", "").strip()
        image_prompt = p.get("image_prompt", "").strip()
        narration = p.get("narration", "").strip()
        dialogue = p.get("dialogue", "").strip()
        caption = p.get("caption", f"PANEL {panel_num}").strip()
        image_url = p.get("image_url", "").strip()

        # Build clean absolute filesystem path from image_url
        if image_url.startswith("/static/"):
            rel_file = image_url.replace("/static/", "")
            image_path = str(BASE_DIR / "static" / rel_file)
        elif image_url.startswith("static/"):
            image_path = str(BASE_DIR / image_url)
        else:
            image_path = p.get("image_path", "")

        # Combined narration/dialogue field for templates that request it
        combined_text = f"{narration}\n\n{dialogue}".strip() if narration and dialogue else (narration or dialogue)

        panel_entry = {
            "panel": panel_num,
            "panel_number": panel_num,
            "title": title,
            "scene_description": scene_desc,
            "caption": caption,
            "narration": narration,
            "dialogue": dialogue,
            "narration_dialogue": combined_text,
            "image_prompt": image_prompt,
            "image_url": image_url,
            "image_path": image_path,
        }
        clean_panels.append(panel_entry)

    # Sort to guarantee panels 1 to 5 order
    clean_panels.sort(key=lambda x: x["panel"])

    return {
        "title": comic_title,
        "metadata": {
            "character_name": character_name,
            "story_prompt": story_prompt,
            "setting": setting,
            "tone": tone,
            "art_style": art_style,
            "created_at": datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p"),
        },
        "panels": clean_panels,
        "total_panels": len(clean_panels),
    }
