import time
import streamlit as st
from google import genai

st.title("Sap-lings: connection test")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"].strip())

PREFERRED_MODEL = "gemini-3.8-flash"


def backup_models():
    """Find other 'flash' models this key can use, as backups."""
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


def ask_ai(prompt):
    """Ask the AI. Retries when busy, then tries backup models."""
    models = [PREFERRED_MODEL]
    last_error = None
    tried_backups = False
    i = 0
    while i < len(models):
        model = models[i]
        for attempt in range(3):
            try:
                reply = client.models.generate_content(
                    model=model, contents=prompt
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
            models += backup_models()
            tried_backups = True
    raise last_error


if st.button("Test the AI"):
    with st.spinner("Asking the AI... (it may retry if Google is busy)"):
        try:
            answer, used = ask_ai(
                "Say hello to Team Sap-lings in one friendly sentence."
            )
            st.success(answer)
            st.caption(f"Answered by model: {used}")
        except Exception as e:
            st.error("All attempts failed. The real reason is below:")
            st.code(str(e))
