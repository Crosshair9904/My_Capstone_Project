import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta, datetime
from openai import OpenAI
import google.generativeai as genai 
import os
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import json
from docx import Document
import io



from services.home import get_user_data

# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)

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

# Setting The User Session
def get_user_data(email):
    # Fetch user data from Supabase or initialize if not found
    response = supabase.table("user_data").select("data").eq("email", email).execute()
    data = response.data

    if not data:
        # User doesn't exist yet, initialize
        default_data = {
            "courses_list": [],
            "courses_colors": [],
            "difficulty_ranking": [],
            "tasks": [],
            "complete_tasks": [],
            "written_notes":[],
            "uploaded_file":[],
            "ai_history":[],

        }

        supabase.table("user_data").insert({
            "email": email,
            "data": default_data
        }).execute()

        return default_data

    # Ensures that the data coming to the app is a string and what goes to the database is json compatible 

    raw_data = data[0]["data"]
    if isinstance(raw_data, str):
        return json.loads(raw_data)
    return raw_data



user_data = get_user_data(st.session_state['username'])

# Initialize chat history in session (only for current app run)
if "current_ai_session" not in st.session_state:
    st.session_state["current_ai_session"] = []




# Function to Update Supabase Database 

def update_user_data(email, new_data):
    """Update user's data field in Supabase."""
    supabase.table("user_data").update({
        "data": new_data
    }).eq("email", email).execute()


def ai(email):
    # Fetch user data
    user_data = get_user_data(email)

    # Get the data from database to edit within application
    courses = user_data.get("courses_list", [])
    colors = user_data.get("courses_colors", [])
    difficulty_ranking = user_data.get("difficulty_ranking", [])
    tasks = user_data.get("tasks", [])
    completed_tasks = user_data.get("complete_tasks", [])
    written_notes = user_data.get("written_notes",[])
    uploaded_file = user_data.get("uploaded_file",[])
    the_ai_history = user_data.get("ai_history", [])
        
    
    
    st.header("AI Tools")


    # Configure the Gemini API with the securely stored key
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Display history
    for entry in st.session_state["current_ai_session"]:
        with st.chat_message(email):
            st.markdown(entry["user_input"])
        with st.chat_message("AI Assistant"):
            st.markdown(entry["ai_response"])

    # Input
    user_input = st.chat_input("Prompt AI Assistant")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Generating Response"):
            response = model.generate_content(user_input)
            ai_response = response.text

        with st.chat_message("assistant"):
            st.markdown(ai_response)

        # Save chat
        new_entry = {
            "user_input": user_input,
            "ai_response": ai_response,
            "course": task['course'],
            "timestamp": datetime.utcnow().isoformat()
        }

        st.session_state["current_ai_session"].append(new_entry)
        the_ai_history.append(new_entry)
        user_data["ai_history"] = the_ai_history
        update_user_data(email, user_data)


ai(st.session_state['username'])

