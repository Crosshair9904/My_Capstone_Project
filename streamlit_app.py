import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta, datetime
import openai
import google.generativeai as genai 
import supabase
import json
from docx import Document
import io
import os
import base64
from pathlib import Path

from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client




def background():
    page_element = """
    <style>

    /*******************************************************
     FULLY TRANSPARENT STREAMLIT HEADER – SAFE VERSION
    *******************************************************/

    /* Outer header container */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0) !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
    }

    /* Inner toolbar block */
    header[data-testid="stHeader"] > div:first-child {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }

    /* Streamlit’s banner subcontainer */
    header[data-testid="stHeader"] div[role="banner"] {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }

    /* All nested elements must not re-apply tint */
    header[data-testid="stHeader"] * {
        background: transparent !important;
    }


    /*******************************************************
     NORMAL BACKGROUND BEHIND ENTIRE APP
    *******************************************************/
    [data-testid="stApp"] {
        background-image: url("https://cdn.wallpapersafari.com/58/75/Ut1h5g.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    </style>
    """

    st.markdown(page_element, unsafe_allow_html=True)
background()


# Frosted Glass Theme CSS
st.markdown("""
<style>
/* --- Buttons --- */
button[kind="secondary"], button[kind="primary"], div.stButton > button {
    background-color: rgba(255, 255, 255, 0.08) !important; /* semi-transparent */
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(6px);
    transition: 0.3s ease-in-out;
    border-radius: 8px;
}

/* Button hover */
div.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}

/* --- Dialogs / Modals --- */
.stDialog, .stModal, div[data-testid="stModal"], div[data-testid="stDialog"] {
    background-color: rgba(30, 30, 30, 0.4) !important;
    color: white !important;
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Inner containers in dialogs */
.stDialog div, .stModal div {
    background-color: transparent !important;
}

/* --- Inputs / Textareas / Selects --- */
input, select, textarea {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 6px;
}

/* --- Popovers (expanded content) --- */
div[data-baseweb="popover"] {
    background-color: rgba(30, 30, 30, 0.4) !important; 
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    box-shadow: none !important;
    backdrop-filter: blur(10px) !important;
}

/* Popover inner elements */
div[data-baseweb="popover"] * {
    background-color: transparent !important;
    color: white !important;
}

/* Optional: Adjust popover arrow to match background */
div[data-baseweb="popover"]::after {
    background-color: rgba(30, 30, 30, 0.4) !important;
}

/* --- Frosted Expanders --- */
div.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 10px !important;
    color: white !important;
    transition: all 0.3s ease-in-out !important;
}

/* Expanded expander body */
div.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(12px) !important;
    border-radius: 0 0 10px 10px !important;
    border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: white !important;
}

/* Hover / active glow for expander header */
div.streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
}

/* Remove Streamlit default shadows */
div[data-testid="stExpander"] {
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


#TO RUN APP: RUN THE CODE AND TAKE THE PATH AND USE THE RUN COMMAND IN TERMINAL
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
            "written_notes":[ ],
            "uploaded_file":[],
            "ai_history":[],
            "ai_use_task_ordering":[],
            "ai_use_ai_priority":[],
            "ai_document_assistant":[],
            "ai_use_history":[],
            "ai_quiz_length": ["Short"],
            "ai_summary_length": ["Short"],
            "ai_assistant_response_length": ["Medium"],

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

url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']


# supabase = init_connection()

# # Initialize the Supabase connection
# conn = st.connection("supabase", type=SupabaseConnection)
supabase: Client = create_client(url, key)




def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")


def login(username):
    # Log in the user and set session state
    st.session_state["logged_in"] = True
    st.session_state["username"] = st.session_state.user_email
    st.session_state["login_time"] = datetime.now()  # Set login time
    # Initialize user-specific session state
    get_user_data(username)

def main_app(user_email):

    login(user_email) # used to start the session state individually for each user's email

    user_data = get_user_data(st.session_state['username'])



    with st.sidebar:

        if st.button("How To Use the Application", width="content"):
            @st.dialog("How To Use the App", width="large")
            def how_to_use():
                st.write("""
                    First things first, thank you for using the app, I greatly appreciate it.

                    How to use the app:

                    1.
                        The first thing you want to do is to enter your course info. Look to the top left corner and select the “Settings” page. You will see 	where you will enter your course information. To start, enter the name of one of your courses, select a colour for the course. This colour will be used to differentiate your different courses, so select different ones for different courses. After selecting the colour, click “Add Course”. After entering a few courses, you may notice the progress bar filling up, this means you are nearly done entering your course info. If you have added at least 3 courses, you will see a new option pop up, this is where you select your courses and place them in order of most difficult to the easiest, this will be used for some features to work more properly in the app.

                        If you entered a course incorrectly or wish to change your list, navigate to the “Edit Course List” option and select it. From there, you can chose to edit a course in the list, remove a course from the list, or reset the list altogether. 

                    2. 
                        After setting up your courses, you will can navigate to the “AI Tools” section in the settings menu and select which AI features you would like to use, if any. They are all disabled by default and won’t work until you have enabled them. 

                        Warning: Do NOT give any personal information to the AI Assistant, as it is based on Google Gemini and sends the data to Google in order to process its response. Also, if you are using the ai features, notice how the rest of the app gets greyed out a little, this is the AI processing. Anything you do in the app while the AI is doing this will NOT be saved, so wait until it is done doing its thing and continue afterwards.

                    A few final things to note:

                    - I am not paying for the premium subscription for the database I am using, so unfortunately, you will have login every time the app reloads. Sorry :)
                    - Sometimes the server for the app takes a while to load, so if the app doesn’t load immediately, give it a few minutes and it should get up and going again.
                    - This is a web app, not an actual application, if you want to make it more like an app, you can turn it into a web application for your phone or computer, just look up how to do it for your specific web browser and it should work just fine.


                                    """)
            how_to_use()

        st.markdown(
            f"""
            <span style="
                background-color: green;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            ">
                Version 1.1.0
            </span>
            """,
            unsafe_allow_html=True,
        )
        def show_changelog():
            with st.expander("Changelog"):
                st.write(f"""
Version 1.1.0 includes the following improvements:
- Added Completion Date Tracking for Completed Tasks
- Added User-Selectable AI Response Criteria
- Added AI Tab in Sidebar for Future Use
- Fixed Some Issues

Date Updated: 2025/11/27        
                            
                            """)
        show_changelog()



        st.title("Login Sucessful!")
        st.success(f"Welcome, {user_email}!")
        if st.button("Logout"):
            sign_out()
    
    #all the pages setup
    #logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("services/settings.py", title="Settings", icon=":material/settings:")
    calendar = st.Page("services/calendar.py", title="Supabase Testing", icon=":material/warning:")

    home = st.Page(
    "services/home.py",
    title="Home",
    icon=":material/home:",
    default=True,
    )

    ai = st.Page("services/ai.py", title="Ai Tools", icon=":material/network_intelligence:")

    #defines page groups
    account_pages = [settings]
    if user_data['ai_document_assistant']:
        services_pages = [home]
    else:
        services_pages = [home]

    page_dict = {}
    page_dict["Services"] = services_pages


    if len(page_dict) > 0:
        pg = st.navigation({"Account": account_pages} | page_dict)

    pg.run()
    
@st.dialog("Please Login or Sign Up")
def auth_screen():    


    
    with st.expander("How To Use The App", width="stretch"):
        def how_to_use():
            st.write("""
                First things first, thank you for using the app, I greatly appreciate it.

                How to use the app:

                1.
                    The first thing you want to do is to enter your course info. Look to the top left corner and select the “Settings” page. You will see 	where you will enter your course information. To start, enter the name of one of your courses, select a colour for the course. This colour will be used to differentiate your different courses, so select different ones for different courses. After selecting the colour, click “Add Course”. After entering a few courses, you may notice the progress bar filling up, this means you are nearly done entering your course info. If you have added at least 3 courses, you will see a new option pop up, this is where you select your courses and place them in order of most difficult to the easiest, this will be used for some features to work more properly in the app.

                    If you entered a course incorrectly or wish to change your list, navigate to the “Edit Course List” option and select it. From there, you can chose to edit a course in the list, remove a course from the list, or reset the list altogether. 

                2. 
                    After setting up your courses, you will can navigate to the “AI Tools” section in the settings menu and select which AI features you would like to use, if any. They are all disabled by default and won’t work until you have enabled them. 

                    Warning: Do NOT give any personal information to the AI Assistant, as it is based on Google Gemini and sends the data to Google in order to process its response. Also, if you are using the ai features, notice how the rest of the app gets greyed out a little, this is the AI processing. Anything you do in the app while the AI is doing this will NOT be saved, so wait until it is done doing its thing and continue afterwards.

                A few final things to note:

                - I am not paying for the premium subscription for the database I am using, so unfortunately, you will have login every time the app reloads. Sorry :)
                - Sometimes the server for the app takes a while to load, so if the app doesn’t load immediately, give it a few minutes and it should get up and going again.
                - This is a web app, not an actual application, if you want to make it more like an app, you can turn it into a web application for your phone or computer, just look up how to do it for your specific web browser and it should work just fine.


                                """)
        how_to_use()
    
    options = ["Login", "Sign Up"]
    option = st.segmented_control(
    "", options, selection_mode="single", width="stretch", default="Login")

    if option == "Sign Up":
        st.error(f"""
            Please note that only your email will be used exclusively to keep your app usage only accessable by you, protected by your password.
             
            When first signing up, you will enter your information and then try to sign in, it will NOT work immediately, you will recieve an email with a link to confirm your account by the provider Supabase, click the link and try to login again.             
             
             """)
    if option == "Login":
        st.error(f"""
            Please note that only your email will be used exclusively to keep your app usage only accessable by you, protected by your password.
            
            Do not give the AI Assistant any personal information, as it sends requests to Google to process it's responses.
             
             
             """)
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    

    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password)
        if user and user.user:
            st.success("Registration successful. Please log in.")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user and user.user:
            st.session_state.user_email = user.user.email
            st.success(f"Welcome back, {email}!")
            st.rerun()
    
   

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
else:
    auth_screen()


