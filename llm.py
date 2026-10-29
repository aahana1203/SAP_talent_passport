import json
import time
import streamlit as st
from google import genai
from google.genai import types

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"].strip())

PREFERRED_MODEL = "gemini-3.8-flash"


def _backup_models():
    found = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            bad = ["image", "tts", "live", "audio", "embedding", "robotics"]
            if "flash" in name and not any(b in name for b in bad):
                if name != PREFERRED_MODEL:
                    found.append(name)
    except Exception:
        pass
    return found


def ask_ai(prompt, as_json=False):
    """Ask the AI. Retries when busy, then tries backup models."""
    config = None
    if as_json:
        config = types.GenerateContentConfig(response_mime_type="application/json")
    models = [PREFERRED_MODEL]
    last_error = None
    tried_backups = False
    i = 0
    while i < len(models):
        model = models[i]
        for attempt in range(3):
            try:
                reply = client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                return reply.text, model
            except Exception as e:
                last_error = e
                text = str(e)
                busy = ("503" in text) or ("429" in text) or ("UNAVAILABLE" in text)
                if busy and attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                break
        i += 1
        if i == len(models) and not tried_backups:
            models += _backup_models()
            tried_backups = True
    raise last_error


def ask_ai_json(prompt):
    """Ask the AI and get back structured data (a Python dictionary)."""
    text, used = ask_ai(prompt, as_json=True)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned), used
