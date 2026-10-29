import streamlit as st
from google import genai

st.title("Sap-lings: connection test")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"].strip())

MODEL = "gemini-2.5-flash"

if st.button("Test the AI"):
    try:
        reply = client.models.generate_content(
            model=MODEL,
            contents="Say hello to Team Sap-lings in one friendly sentence.",
        )
        st.success(reply.text)
    except Exception as e:
        st.error("The AI call failed. The real reason is below:")
        st.code(str(e))

if st.button("Show models my key can use"):
    try:
        names = [m.name for m in client.models.list()]
        st.write(names)
    except Exception as e:
        st.error("Could not list models. The real reason is below:")
        st.code(str(e))
