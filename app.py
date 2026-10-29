import os
import streamlit as st
from llm import ask_ai_json

st.set_page_config(page_title="Sap-lings Talent Passport", page_icon="🌱", layout="wide")
st.title("🌱 Sap-lings Talent Passport")
st.caption("Agent 1 · Skills Discovery Agent")

HERE = os.path.dirname(os.path.abspath(__file__))


def load_sample():
    path = os.path.join(HERE, "data", "resume_priya.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


PROMPT = """You are the Skills Discovery Agent for an inclusive hiring platform.
Read the resume below. Infer the professional skills this person has shown, including skills from non-traditional experience such as caregiving, volunteering, community work, family business, freelance work and self-study.

Rules:
- Only list skills supported by evidence in the text. Never invent skills.
- Ignore name, age, gender, college name, city and career gaps. Do not judge them.
- Give between 6 and 12 skills.
- Reply ONLY with JSON in exactly this shape:
{"summary": "2 sentences on this person's strengths", "skills": [{"skill": "name", "category": "e.g. Data, Communication, Operations", "level": "Beginner or Intermediate or Advanced", "confidence": "High or Medium or Low", "evidence": "short evidence from the resume"}]}

RESUME:
"""

st.subheader("Step 1: Resume")
resume_text = st.text_area(
    "Paste a resume here (sample resume of Priya is already loaded):",
    value=load_sample(),
    height=300,
)

if st.button("🔍 Discover skills", type="primary"):
    with st.spinner("The agent is reading the resume..."):
        try:
            result, used = ask_ai_json(PROMPT + resume_text)
            st.session_state["agent1_result"] = result
            st.session_state["agent1_model"] = used
            st.session_state.pop("approved_skills", None)
        except Exception as e:
            st.error("Something went wrong. The real reason is below:")
            st.code(str(e))

result = st.session_state.get("agent1_result")

if result:
    st.subheader("Step 2: Inferred skills")
    st.info(result.get("summary", ""))
    st.write("Human check: untick any skill that looks wrong, then confirm.")

    icons = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
    keep = []
    for idx, s in enumerate(result.get("skills", [])):
        icon = icons.get(s.get("confidence"), "⚪")
        label = f"{icon} **{s.get('skill')}** · {s.get('category')} · {s.get('level')} · {s.get('confidence')} confidence"
        ticked = st.checkbox(label, value=True, key=f"skill_{idx}")
        st.caption("Evidence: " + str(s.get("evidence", "")))
        if ticked:
            keep.append(s)

    if st.button("✅ Confirm approved skills"):
        st.session_state["approved_skills"] = keep

    if "approved_skills" in st.session_state:
        names = [s["skill"] for s in st.session_state["approved_skills"]]
        st.success(f"Confirmed {len(names)} skills: " + ", ".join(names))
        st.caption("These will flow into Agent 2 (Learning Pathway) next.")

    st.caption(f"Answered by model: {st.session_state.get('agent1_model')}")
