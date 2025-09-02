import streamlit as st
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase


#Background
def background():
    page_element="""
    <style>
    [data-testid="stAppViewContainer"]{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    [data-testid="stHeader"]{
    background-color: rgba(0,0,0,0);
    }
    [data-testid="stSidebar"]> div:first-child{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    </style>


    """

    st.markdown(page_element, unsafe_allow_html=True)
background()

import streamlit as st
from supabase import create_client, Client
import json


# Supabase client


SUPABASE_URL = st.secrets["connections"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["connections"]["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Default app data and functions


DEFAULT_DATA = {
    "courses_list": [],
    "courses_colors": [],
    "difficulty_ranking": [],
    "tasks": [],
    "complete_tasks": [],
    "today_tasks": [],
    "this_week_tasks": [],
}

def get_user_data(email):
    resp = supabase.table("user_data").select("data").eq("email", email).limit(1).execute()
    rows = getattr(resp, "data", [])

    if not rows:
        supabase.table("user_data").insert({"email": email, "data": DEFAULT_DATA}).execute()
        return json.loads(json.dumps(DEFAULT_DATA))

    raw = rows[0]["data"]
    if isinstance(raw, str):
        raw = json.loads(raw)
    return {**DEFAULT_DATA, **raw}

def update_user_data(email, new_data):
    supabase.table("user_data").update({"data": new_data}).eq("email", email).execute()

def save_banner(email, user_data, msg="Saved"):
    update_user_data(email, user_data)
    st.toast(msg)


# Settings Page


def settings_page(email):
    user_data = get_user_data(email)
    courses_list = user_data["courses_list"]
    courses_colors = user_data["courses_colors"]
    difficulty_ranking = user_data["difficulty_ranking"]

    st.title("Settings")
    st.header("Courses List")

    with st.expander("Course List", expanded=False):
        progress_text = "Completion of Course Selection"
        course_progress_bar = st.progress(0, text=progress_text)

        col1, col2 = st.columns(2)
        with col2:
            course_color = st.color_picker("Select Course Color", key=f"color_{email}")
        with col1:
            course_to_add = st.text_input("Type Course Here")
            if st.button("Add Course"):
                if course_to_add:
                    courses_list.append(course_to_add)
                    courses_colors.append(course_color)
                    save_banner(email, user_data, "Course added")

        if len(courses_colors) >= 3:
            difficulty_ranking = st.multiselect(
                "Rank courses in terms of difficulty (from hardest to easiest):",
                courses_list,
                default=difficulty_ranking,
            )
            user_data["difficulty_ranking"] = difficulty_ranking
            save_banner(email, user_data, "Ranking updated")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("Courses List:")
                for i, course in enumerate(courses_list):
                    st.write(f"{i + 1}. {course}")
            with col2:
                st.write("Colors List:")
                for color in courses_colors:
                    st.write(color)
            with col3:
                st.write("Difficulty Ranking:")
                for i, course in enumerate(difficulty_ranking):
                    st.write(f"{i + 1}. {course}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Courses List:")
                for i, course in enumerate(courses_list):
                    st.write(f"{i + 1}. {course}")
            with col2:
                st.write("Colors List:")
                for color in courses_colors:
                    st.write(color)

        st.header("Edit Course List")
        with st.expander("Edit Course List", expanded=False):
            with st.form("Editing Courses List"):
                tab1, tab2, tab3 = st.tabs(["Edit List", "Remove Course From List", "Reset List"])

                with tab1:
                    course_to_edit = st.selectbox("Select a Course to Edit", courses_list)
                    col1, col2 = st.columns(2)
                    with col1:
                        replacement_course = st.text_input("Please Input New Course")
                    with col2:
                        replacement_course_color = st.color_picker("Select Replacement Course Color")
                    submitted_edited_list = st.form_submit_button("Submit Replacement Course")

                with tab2:
                    course_to_remove = st.selectbox("Select a Course to Remove", courses_list)
                    st.write(f"Pressing the button below will remove {course_to_remove} from the Courses List")
                    submitted_remove_course = st.form_submit_button(f"Remove {course_to_remove} from Courses List")

                with tab3:
                    st.write("Pressing the button below will reset the entire course list")
                    submitted_reset_list = st.form_submit_button("Reset Course List")

        if submitted_edited_list:
            idx = courses_list.index(course_to_edit)
            courses_list[idx] = replacement_course
            courses_colors[idx] = replacement_course_color
            user_data["difficulty_ranking"] = []
            save_banner(email, user_data, "Course updated")

        if submitted_remove_course:
            idx = courses_list.index(course_to_remove)
            courses_list.pop(idx)
            courses_colors.pop(idx)
            user_data["difficulty_ranking"] = []
            save_banner(email, user_data, "Course removed")

        if submitted_reset_list:
            courses_list.clear()
            courses_colors.clear()
            user_data["difficulty_ranking"] = []
            save_banner(email, user_data, "Course list reset")

        # Progress bar logic
        if len(courses_list) == 0:
            course_progress_bar.progress(0, text=progress_text)
        elif len(courses_list) == 1:
            course_progress_bar.progress(12)
        elif len(courses_list) == 2:
            course_progress_bar.progress(25)
        elif len(courses_list) == 3:
            course_progress_bar.progress(37)
        elif len(courses_list) == 4:
            course_progress_bar.progress(50)

        if len(difficulty_ranking) == 1:
            course_progress_bar.progress(62)
        elif len(difficulty_ranking) == 2:
            course_progress_bar.progress(75)
        elif len(difficulty_ranking) == 3:
            course_progress_bar.progress(87)

        if len(difficulty_ranking) >= 3:
            course_progress_bar.progress(100, text="Course Setup Complete!")


settings_page(st.session_state["username"])
