import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta
from openai import OpenAI
import google.generativeai as genai 
import os


from services.home import get_user_data


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



import google.generativeai as genai

# Configure the Gemini API with the securely stored key
genai.configure(api_key=st.secrets["GEMENI_API_KEY"])

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.5-flash") 

st.title("Gemini-Powered AI App")

user_input = st.text_input("Enter your prompt:")

if st.button("Get Response"):
    if user_input:
        with st.spinner("Generating response..."):
            response = model.generate_content(user_input)
            st.write(response.text)
    else:
        st.warning("Please enter a prompt.")
