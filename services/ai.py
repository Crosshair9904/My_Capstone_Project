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


def get_week_bounds():
    """Return today's date, start of week, and end of week (all as date objects)."""
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.isoweekday() - 1)  # Monday start
    end_of_week = start_of_week + timedelta(days=6)
    return today, start_of_week, end_of_week


user_data = get_user_data(st.session_state['username'])
today, start, end = get_week_bounds()

def parse(d):
        return datetime.fromisoformat(d).date()  # all tasks stored as strings
todays_tasks = [
        task["name"]
        for task in user_data['tasks']
        if parse(task["due_date"]) == today
    ]

this_weeks_tasks = [
    task["name"]
    for task in user_data['tasks']
    if start <= parse(task["due_date"]) <= end and parse(task["due_date"]) != today
]




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

    col1, col2= st.columns([1, 2.5])



    #Indicator of what is due today
    with col1:
        st.subheader("Tasks Due Today:")   

        if todays_tasks:
            for task_name in todays_tasks:
                st.markdown(f"- **{task_name}**")
        else:
            st.write("No Tasks Due For Today")

    # Indicator of what is due later in the same week
        st.subheader("Tasks Due Later This Week:")

        if this_weeks_tasks:
            for task_name in this_weeks_tasks:
                st.markdown(f"- **{task_name}**")
        else:
            st.write("No Tasks Due This Week")

    # Configure the Gemini API with the securely stored key
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-2.5-flash")
    user_input = st.text_input("Enter your prompt:")

    if st.button("Get Response"):
        if user_input:
            with st.spinner("Generating response..."):
                response = model.generate_content(user_input)
                st.write(response.text)
        else:
            st.warning("Please enter a prompt.")


                    


                


    

        







ai(st.session_state['username'])

# Things that need to happen:
# - Ai history is stored in database so it can callback anything previously done
# - Give AI access to course difficulty list and all task data so that it can give a logical to-do-list in a logical order      DONE!!!!
# - Add an area in notes section so that it can summarize documents and give additional info on it
# - Possibly make an interface to allow for quiz creation to aid in studying