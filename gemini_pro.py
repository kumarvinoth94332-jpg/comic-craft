"""
gemini_pro.py - Full Story, Dialogue & Caption Generator using Gemini Pro.
Takes a 5-panel outline and enriches it with narrative storytelling, dialogue, and comic captions.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("comiccraft.gemini_pro")


def _clean_json_text(text: str) -> str:
    """Extract and sanitize JSON from model text responses."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return text


def _build_fallback_story(
    outline: List[Dict[str, Any]],
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[Dict[str, Any]]:
    """
    Fallback story script generator when Gemini Pro API is unavailable.
    Generates rich, consistent comic storytelling, captions, and authentic dialogue.
    """
    char = character_name.strip() or "The Hero"
    loc = setting.strip() or "Mysterious Realm"
    mood = tone.strip().lower()

    captions = [
        f"INTO THE HEART OF {loc.upper()}...",
        "A SHADOW FLICKERS IN THE DISTANCE...",
        "CRACK! THE MOMENT OF TRUTH!",
        "AGAINST IMPOSSIBLE ODDS...",
        "WHEN THE DUST FINALLY SETTLES...",
    ]

    narrations = [
        f"The tranquil silence of {loc} was broken by the quiet footsteps of {char}, driven by the whispers of an untold destiny.",
        f"Every instinct warned {char} to turn back, yet the pulsating glow ahead demanded answers that no map could provide.",
        f"With sudden fury, the ground trembled! Danger struck without warning, testing every fiber of {char}'s resolve.",
        f"Drawing upon deep reserves of bravery, {char} found clarity in the eye of the storm.",
        f"As dawn broke over {loc}, the challenge had been overcome, leaving {char} ready for whatever adventures lay beyond.",
    ]

    dialogues = [
        f'{char}: "There is no turning back now. The answer lies somewhere deep within these grounds."',
        f'{char}: "Wait... that luminescence. It’s reacting to my presence!"',
        f'{char}: "Not on my watch! Hold your ground!"',
        f'{char}: "I see it now... the missing piece to the puzzle!"',
        f'{char}: "We did it. And this is only the beginning of our story."',
    ]

    enriched = []
    for i, panel in enumerate(outline):
        idx = min(i, 4)
        enriched_panel = {
            "panel": panel.get("panel", i + 1),
            "title": panel.get("title", f"Panel {i + 1}"),
            "scene_description": panel.get(
                "scene_description", f"{char} takes decisive action in {loc}."
            ),
            "image_prompt": panel.get("image_prompt", f"Comic art of {char} in {loc}"),
            "narration": narrations[idx],
            "dialogue": dialogues[idx],
            "caption": captions[idx],
        }
        enriched.append(enriched_panel)

    return enriched


def generate_story(
    outline: List[Dict[str, Any]],
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> List[Dict[str, Any]]:
    """
    Enriches a 5-panel outline with narration, character dialogue, and comic captions.
    
    Returns:
        List of 5 enriched panel dictionaries containing:
        - panel: int
        - title: str
        - scene_description: str
        - image_prompt: str
        - narration: str
        - dialogue: str
        - caption: str
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")

    if not api_key or "your_" in api_key.lower():
        logger.warning("No valid GEMINI_API_KEY detected. Using fallback comic story generation.")
        return _build_fallback_story(outline, story_prompt, character_name, setting, tone, art_style)

    system_prompt = (
        "You are an acclaimed comic book writer and dialogue specialist. "
        "Take the 5-panel outline and write vivid comic storytelling for each panel.\n"
        "Requirements:\n"
        "1. Maintain strict continuity across all 5 panels.\n"
        "2. Keep the hero's voice distinct and true to the character name and tone.\n"
        "3. For each panel, output:\n"
        '   - "panel": panel number (1 to 5)\n'
        '   - "title": panel title\n'
        '   - "scene_description": refined scene description\n'
        '   - "image_prompt": the panel image prompt\n'
        '   - "narration": 1-2 sentences of atmospheric comic narrator text\n'
        '   - "dialogue": spoken dialogue in format: Character: "Quote"\n'
        '   - "caption": a punchy classic comic banner caption (e.g. MEANWHILE..., SUDDENLY!)\n'
        "4. Return ONLY a valid JSON array of 5 panel objects. No markdown preamble."
    )

    user_prompt = f"""
STORY PROMPT: {story_prompt}
MAIN CHARACTER: {character_name}
SETTING: {setting}
TONE: {tone}
ART STYLE: {art_style}

EXISTING OUTLINE:
{json.dumps(outline, indent=2)}

Please write the narration, dialogue, and caption for each of the 5 panels, retaining the titles and image prompts.
"""

    # 1. Try modern google-genai SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key, http_options={"timeout": 10000})
        response = client.models.generate_content(
            model=model_name,
            contents=[system_prompt, user_prompt],
            config=types.GenerateContentConfig(
                temperature=0.75,
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
        logger.warning(f"google-genai client failed: {e}. Trying fallback to google-generativeai.")

    # 2. Try google-generativeai SDK
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
        logger.error(f"Gemini Pro story generation error: {e}")

    # Fallback if both fail
    logger.info("Using intelligent comic story fallback generator.")
    return _build_fallback_story(outline, story_prompt, character_name, setting, tone, art_style)
