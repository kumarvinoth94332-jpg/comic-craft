# ComicCraft – AI Comic Story Creator

> **Turn your imagination into a complete 5-panel comic with Google Gemini & AI image generation.**

ComicCraft is a modular AI-powered comic generator that allows anyone to turn a story concept into a complete 5-panel graphic comic strip. It generates narrative story arcs, authentic character dialogue, comic captions, stylized illustrations, and an exportable multi-page PDF comic book ready for print or sharing.

---

## 🌟 Key Features

- **Intuitive Studio UI**: Modern dark cinematic AI studio with vibrant neon purple/blue accents, comic-inspired patterns, and interactive workflow tracking (`IDEA → STORY → ART → COMIC`).
- **Google Gemini Flash (Outline)**: `gemini_flash.py` strictly structures a 5-panel storyboard with titles, scene descriptions, and image prompts.
- **Google Gemini Pro (Story & Dialogue)**: `gemini_pro.py` enriches each panel with continuity-aware narration, character dialogue, and comic captions.
- **Multi-Backend Comic Artwork**: `image_generator.py` connects with Hugging Face Inference API (`FLUX.1-schnell` / Stable Diffusion) or instantly renders comic artwork through an offline procedural Pillow comic canvas engine.
- **Unified Comic Layout**: `layout_builder.py` bundles text, visual assets, and metadata into a clean Jinja2-ready structure.
- **Printable PDF Export**: `exporters.py` generates an attractive multi-page comic book PDF using `fpdf2`.
- **Developer Endpoints**: Includes `/generate-comic/json` for REST API integrations and `/test-image` for rapid artwork testing.
- **Zero-Failure Architecture**: Built-in intelligent fallbacks keep the application functional even when offline or without external API keys.

---

## 📁 Project Structure

```
ComicCraft/
│
├── app/
│   ├── __init__.py           # Application package
│   ├── config.py             # Pydantic settings & environment manager
│   ├── main.py               # FastAPI application entry point & static mounting
│   └── routes.py             # Web routes, API endpoints, and validation
│
├── templates/
│   ├── index.html            # Studio creator homepage with stage loader
│   ├── comic_preview.html    # 5-panel comic reading interface
│   └── export_success.html   # Download confirmation & restart page
│
├── static/
│   ├── css/
│   │   └── style.css         # Dark cinematic studio theme
│   ├── panels/               # Generated panel PNG illustrations
│   └── exports/              # Generated comic PDF documents
│
├── gemini_flash.py           # 5-panel structured outline generator
├── gemini_pro.py             # Story narration, dialogue, & caption generator
├── image_generator.py        # Hugging Face & Pillow comic artwork engine
├── layout_builder.py         # Comic panel layout builder
├── exporters.py              # Multi-page PDF comic generator (fpdf2)
├── requirements.txt          # Python dependencies
├── .env                      # Local environment configuration
├── .env.example              # Template environment variables
├── .gitignore                # Git exclusions
└── README.md                 # Documentation & setup guide
```

---

## 🚀 Quick Start Guide (Windows / VS Code)

### 1. Prerequisites
- Python 3.10+ installed and added to your system `PATH`.
- VS Code or your preferred terminal.

### 2. Setup Virtual Environment

Open PowerShell inside the project directory:

```powershell
# Create virtual environment
python -m venv env

# Activate virtual environment
.\env\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit `.env` (or copy `.env.example` to `.env`):

```env
APP_NAME=ComicCraft – AI Comic Story Creator
APP_VERSION=1.0.0
DEBUG=true

# Google Gemini API Key (https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_FLASH_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-2.5-pro

# Hugging Face API Configuration (Optional: https://huggingface.co/settings/tokens)
HF_API_KEY=your_huggingface_api_key_here
HF_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell

# Backend: 'auto', 'hf', or 'demo'
IMAGE_BACKEND=auto
```

*(Note: If you leave `GEMINI_API_KEY` or `HF_API_KEY` empty, ComicCraft will automatically run in demo mode with intelligent generators so you can test the entire workflow immediately without errors!)*

### 5. Launch the Application

```powershell
uvicorn app.main:app --reload
```

- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Redoc API**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📖 API Reference

### 1. Web Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Studio Homepage form with prompt & style selections |
| `POST` | `/generate` | Submits form, generates 5 panels, and displays preview |
| `GET` | `/download-pdf/{filename}` | Downloads the generated comic PDF |
| `GET` | `/export-success` | Confirmation page after PDF download |
| `GET` | `/health` | System health check |

### 2. JSON API Endpoint

#### `POST /generate-comic/json`

**Request Body (`application/json`)**:
```json
{
  "story_prompt": "A brave astronaut discovering an ancient crystalline monument on Mars",
  "character_name": "Captain Nova",
  "setting": "Space",
  "tone": "Dramatic",
  "art_style": "Comic Book"
}
```

**Response (`200 OK`)**:
```json
{
  "status": "success",
  "comic_layout": {
    "title": "Captain Nova: A World Awakes",
    "metadata": { ... },
    "total_panels": 5
  },
  "generated_panels": [
    {
      "panel": 1,
      "title": "A World Awakes",
      "scene_description": "...",
      "narration": "...",
      "dialogue": "...",
      "caption": "...",
      "image_url": "/static/panels/panel_1_abc.png"
    }
  ],
  "pdf_path": "/static/exports/comic_captain_nova_20260924.pdf"
}
```

### 3. Developer Test Endpoint

#### `GET /test-image`
Test image generation with custom parameters:
```
http://127.0.0.1:8000/test-image?prompt=A+cybernetic+ninja+in+a+neon+city&art_style=Anime&panel_num=1
```

---

## 🛠️ Testing

Run integration tests using pytest:

```powershell
pytest
```

---

## 🛡️ License & Credits

Built with ❤️ for comic creators and AI enthusiasts.
Powered by FastAPI, Google Gemini, and Hugging Face.
