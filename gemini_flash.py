"""
gemini_flash.py - 5-Panel Comic Outline Generator using Gemini Flash.
Generates structured 5-panel outlines with titles, scene descriptions, and image prompts.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("comiccraft.gemini_flash")


def _clean_json_text(text: str) -> str:
    """Extract and sanitize JSON from model text responses."""
    text = text.strip()
    # Remove markdown code blocks if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return text


def _build_fallback_outline(
    story_prompt: str, character_name: str, setting: str, tone: str, art_style: str
) -> List[Dict[str, Any]]:
    """
    Intelligent fallback generator when API key is missing or quota is exhausted.
    Ensures the user always gets a rich, perfectly structured 5-panel comic.
    """
    char = character_name.strip() or "The Hero"
    loc = setting.strip() or "Enchanted Forest"
    mood = tone.strip() or "Adventurous"
    style = art_style.strip() or "Comic Book"
    prompt_snippet = story_prompt.strip()

    return [
        {
            "panel": 1,
            "title": "A World Awakes",
            "scene_description": (
                f"In the vibrant expanse of {loc}, {char} stands at the threshold of a new journey. "
                f"The atmosphere is thick with {mood.lower()} energy as signs of a greater mystery begin to unfold."
            ),
            "image_prompt": (
                f"{style} style: Establishing wide-angle shot of {char} exploring {loc}. "
                f"{prompt_snippet}. Dramatic lighting, vivid colors, cinematic comic composition, high detail."
            ),
        },
        {
            "panel": 2,
            "title": "The Unseen Anomaly",
            "scene_description": (
                f"Deep within {loc}, {char} stumbles upon a glowing anomaly that defies nature. "
                f"Curiosity meets caution as ancient mechanisms hum to life."
            ),
            "image_prompt": (
                f"{style} style: Medium close-up of {char} discovering a glowing mystical artifact in {loc}. "
                f"Mysterious glowing aura, dynamic shadows, expressive character face, vibrant comic panel art."
            ),
        },
        {
            "panel": 3,
            "title": "Clash of Destinies",
            "scene_description": (
                f"The environment erupts into chaos. An unforeseen obstacle challenges {char}, "
                f"demanding every ounce of courage and quick thinking."
            ),
            "image_prompt": (
                f"{style} style: Action sequence of {char} leaping across danger in {loc}. "
                f"Dynamic motion blur, comic speed lines, electric energy burst, high tension, detailed background."
            ),
        },
        {
            "panel": 4,
            "title": "The Turning Tide",
            "scene_description": (
                f"Against all odds, {char} unlocks an unexpected surge of insight. "
                f"The balance shifts as the true secret of the encounter is revealed."
            ),
            "image_prompt": (
                f"{style} style: Heroic portrait of {char} channeling newfound power in {loc}. "
                f"Dramatic rim lighting, glowing effects, triumphant stance, rich comic book textures."
            ),
        },
        {
            "panel": 5,
            "title": "A New Horizon",
            "scene_description": (
                f"With peace restored to {loc}, {char} gazes toward the sprawling horizon. "
                f"The legend of this adventure has only just begun."
            ),
            "image_prompt": (
                f"{style} style: Epic cinematic wide vista of {char} standing victorious in {loc}. "
                f"Golden sunset sky, glowing highlights, inspirational atmosphere, beautiful masterwork comic illustration."
            ),
        },
    ]


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[Dict[str, Any]]:
    """
    Generates a structured 5-panel comic outline using Google Gemini Flash API.
    
    Returns:
        List of 5 panel dictionaries containing:
        - panel: int (1..5)
        - title: str
        - scene_description: str
        - image_prompt: str
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.6-flash")

    # If no key or placeholder key, use fallback directly
    if not api_key or "your_" in api_key.lower():
        logger.warning("No valid GEMINI_API_KEY detected. Using intelligent comic generator fallback.")
        return _build_fallback_outline(story_prompt, character_name, setting, tone, art_style)

    system_prompt = (
        "You are an elite comic book director and storyboard artist. "
        "Your task is to generate an exciting, structured 5-panel comic outline based on user input. "
        "You must strictly return a JSON array containing EXACTLY 5 objects (one per panel). "
        "Each object must have these exact keys:\n"
        '- "panel": integer (1 to 5)\n'
        '- "title": concise, punchy comic panel title\n'
        '- "scene_description": 2-3 sentences describing the characters, actions, and environment\n'
        '- "image_prompt": detailed text prompt for an AI image generator matching the requested art style, '
        'including lighting, camera angle, character appearance, and comic book visual style.\n'
        "Do not wrap with commentary. Return valid JSON only."
    )

    user_prompt = f"""
STORY PREMISE: {story_prompt}
MAIN CHARACTER: {character_name}
SETTING: {setting}
TONE: {tone}
ART STYLE: {art_style}

Format: Exactly 5 panels. Ensure clear narrative progression:
Panel 1: Introduction / Inciting incident
Panel 2: Rising action / Discovery
Panel 3: Climax / Sudden obstacle or showdown
Panel 4: Hero's turning point / Revelation
Panel 5: Resolution / Memorable closing punchline or heroic horizon
"""

    # 1. Try modern google-genai SDK first
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key, http_options={"timeout": 10000})
        response = client.models.generate_content(
            model=model_name,
            contents=[system_prompt, user_prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )
        if response and response.text:
            cleaned = _clean_json_text(response.text)
            data = json.loads(cleaned)
            if isinstance(data, list) and len(data) == 5:
                return data
            elif isinstance(data, dict) and "panels" in data and len(data["panels"]) == 5:
                return data["panels"]
    except Exception as e:
        logger.warning(f"google-genai client failed: {e}. Trying google-generativeai fallback.")

    # 2. Try google-generativeai SDK as secondary with timeout
    try:
        import google.generativeai as legacy_genai

        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel(model_name)
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}\n\nJSON output:",
            request_options={"timeout": 10},
        )
        if response and response.text:
            cleaned = _clean_json_text(response.text)
            data = json.loads(cleaned)
            if isinstance(data, list) and len(data) == 5:
                return data
            elif isinstance(data, dict) and "panels" in data and len(data["panels"]) == 5:
                return data["panels"]
    except Exception as e:
        logger.error(f"Gemini API outline generation error: {e}")

    # Fallback if both SDK calls or JSON parsing fail
    logger.info("Using intelligent comic outline fallback generator.")
    return _build_fallback_outline(story_prompt, character_name, setting, tone, art_style)
