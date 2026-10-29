import streamlit as st
from google import genai

st.title("Sap-lings: connection test")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if st.button("Test the AI"):
    reply = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello to Team Sap-lings in one friendly sentence.",
    )
    st.success(reply.text)
