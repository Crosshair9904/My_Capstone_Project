import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta
import openai
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import json

# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)


# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)

# Setting the Background
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
            "complete_tasks": []
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


# Function to Update Supabase Database 

def update_user_data(email, new_data):
    """Update user's data field in Supabase."""
    supabase.table("user_data").update({
        "data": new_data
    }).eq("email", email).execute()


def settings_page(email):
    st.title("Settings")

     # Fetch user data
    user_data = get_user_data(email)

    # Get the data from database to edit within application
    courses = user_data.get("courses_list", [])
    colors = user_data.get("courses_colors", [])
    difficulty_ranking = user_data.get("difficulty_ranking", [])
    tasks = user_data.get("tasks", [])
    completed_tasks = user_data.get("complete_tasks", [])


    st.header("Courses List")

    with st.expander("Course List", expanded=False):
        # Progress Bar
        progress_text = "Completion of Course Selection"
        course_progress_bar = st.progress(0, text=progress_text)

        col1, col2 = st.columns(2)

        with col2:
            # Input to select a color for calendar
            course_color = st.color_picker("Select Course Color", key=f"color_{st.session_state['username']}")

        with col1:
            # Input for new course
            course_to_add = st.text_input("Type Course Here")

            # Button to add the course to the list
            if st.button("Add Course"):
                if course_to_add:  # Check if the input is not empty
                    user_data["courses_list"].append(course_to_add)
                    user_data["courses_colors"].append(course_color)
                    update_user_data(email, user_data)

        # Difficulty of courses for AI reference
        if len(user_data["courses_colors"]) >= 3:
            course_difficulty_list = st.multiselect(
                "Rank courses in terms of difficulty (from hardest to easiest):",
                user_data["courses_list"],
            )
            user_data["difficulty_ranking"].clear()
            user_data["difficulty_ranking"].append(course_difficulty_list)
            update_user_data(email, user_data)
            
            # Displays of Properties
            col1, col2, col3 = st.columns(3)

            with col1:
                # Display the list of courses
                st.write("Courses List:")
                for i, course in enumerate(user_data["courses_list"]):
                    st.write(f"{i + 1}. {course}")

            with col2:
                # Display the colors list
                st.write("Colors List:")
                for i, color in enumerate(user_data["courses_colors"]):
                    st.write(f"{color}")
            if user_data["difficulty_ranking"] != "[]" :
                with col3:
                    # Display the difficulty order
                    st.write("Difficulty Ranking:")
                    for i, course in enumerate(user_data["difficulty_ranking"]):
                        st.write(f"{i + 1}. {course}")

        else:
            col1, col2 = st.columns(2)

            with col1:
                # Display the list of courses
                st.write("Courses List:")
                for i, course in enumerate(user_data["courses_list"]):
                    st.write(f"{i + 1}. {course}")

            with col2:
                # Display the colors list
                st.write("Colors List:")
                for i, color in enumerate(user_data["courses_colors"]):
                    st.write(f"{color}")

        # Option to reset courses list
        st.header("Edit Course List")

        with st.expander("Edit Course List", expanded=False):
            with st.form("Editing Courses List"):
                tab1, tab2, tab3 = st.tabs(["Edit List", "Remove Course From List", "Reset List"])

                # Edit Tab
                with tab1:
                    # Select course to edit
                    course_to_edit = st.selectbox("Select a Course to Edit", user_data["courses_list"])

                    col1, col2 = st.columns(2)

                    with col1:
                        # Input what is to replace it
                        replacement_course = st.text_input("Please Input New Course")
                    with col2:
                        replacement_course_color = st.color_picker("Select Replacement Course Color")

                    submitted_edited_list = st.form_submit_button("Submit Replacement Course")

                # Remove Tab
                with tab2:
                    # Select a Course to remove from list
                    course_to_remove = st.selectbox("Select a Course to Remove", user_data["courses_list"])

                    # Button to remove course
                    st.write(f"Pressing the button below will remove {course_to_remove} from the Courses List")
                    submitted_remove_course_from_list = st.form_submit_button(f"Remove {course_to_remove} from Courses List")

                # Reset Tab
                with tab3:
                    st.write("Pressing the button below will reset the entire course list")
                    submitted_reset_list = st.form_submit_button("Reset Course List")

    # What happens when the buttons are pressed
    if submitted_edited_list:
        index_course_replace = user_data["courses_list"].index(course_to_edit)  # Get index of course to be replaced
        user_data["courses_list"][index_course_replace] = replacement_course  # Replace course
        user_data["courses_colors"][index_course_replace] = replacement_course_color  # Replace color
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    if submitted_remove_course_from_list:
        index_course_remove = user_data["courses_list"].index(course_to_remove)  # Get index of course to be removed
        user_data["courses_list"].remove(course_to_remove)
        user_data["courses_colors"].remove(user_data["courses_colors"][index_course_remove])
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    if submitted_reset_list:
        user_data["courses_list"].clear()
        user_data["courses_colors"].clear()
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    # Controlling Progress Bar
    if len(user_data["courses_list"]) == 0:
        course_progress_bar.progress(0, text=progress_text)
    elif len(user_data["courses_list"]) == 1:
        course_progress_bar.progress(12)
    elif len(user_data["courses_list"]) == 2:
        course_progress_bar.progress(25)
    elif len(user_data["courses_list"]) == 3:
        course_progress_bar.progress(37)
    elif len(user_data["courses_list"]) == 4:
        course_progress_bar.progress(50)

    if len(user_data["difficulty_ranking"]) == 1:
        course_progress_bar.progress(62)
    elif len(user_data["difficulty_ranking"]) == 2:
        course_progress_bar.progress(75)
    elif len(user_data["difficulty_ranking"]) == 3:
        course_progress_bar.progress(87)

    if len(user_data["difficulty_ranking"]) >= 3:
        course_progress_bar.progress(100, text="Course Setup Complete!")

settings_page(st.session_state['username'])