import json
import os
from pathlib import Path
from typing import Dict, Optional
from PIL import Image

from code.config import IMAGES_CSV_PATH, IMAGES_DIR, IMAGE_CACHE_PATH

def get_image_facts(cache_path: Optional[Path] = None) -> Dict[str, dict]:
    path = cache_path or IMAGE_CACHE_PATH
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def extract_image_ocr(image_id: str) -> dict:
    cache = get_image_facts()
    if image_id in cache:
        return cache[image_id]
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(f"Image {image_id} could not be resolved! No valid OCR cache entry found and GEMINI_API_KEY is not set.")
    
    from google import genai
    client = genai.Client(api_key=api_key)
    img_path = IMAGES_DIR / f"{image_id}.png"
    if not img_path.exists():
        raise FileNotFoundError(f"Image file {img_path} does not exist!")
    
    img = Image.open(img_path)
    prompt = """Extract total amount and currency from this document as JSON:
    - "amount": float
    - "currency": string
    - "document_type": string
    """
    resp = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[img, prompt],
        config=dict(response_mime_type="application/json")
    )
    data = json.loads(resp.text)
    if not data or "amount" not in data or data["amount"] is None or data["amount"] <= 0:
        raise ValueError(f"Gemini OCR extraction failed for {image_id}: {resp.text}")
        
    cache[image_id] = data
    with open(IMAGE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
    return data
