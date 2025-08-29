import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta
from openai import OpenAI
import google.generativeai as genai 
import os


#Background
def background():
    page_element="""
    <style>
    [data-testid="stAppViewContainer"]{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    [data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0);
    }
    [data-testid="stSidebar"]> div:first-child{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    </style>


    """

    st.markdown(page_element, unsafe_allow_html=True)
background()

st.header("AI Tools")

st.title("ChatGPT-like clone")

 # Load API key from Streamlit secrets or environment variable for security
if "GEMENI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMENI_API_KEY"])
else:
    st.error("Gemini API Key not found. Please add it to your Streamlit secrets or environment variables.")
    st.stop() # Stop the app if the key is missing

model = genai.GenerativeModel('gemini-pro')

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": "Hello! How can I help you today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

with st.chat_message("model"):
    response = model.generate_content(prompt)
    st.markdown(response.text)
    st.session_state.messages.append({"role": "model", "content": response.text})

