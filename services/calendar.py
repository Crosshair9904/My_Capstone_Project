import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase







# # Initialize Supabase Client
# url = st.secrets['connections']['SUPABASE_URL']
# key = st.secrets['connections']['SUPABASE_KEY']
# supabase: Client = create_client(url, key)

# def get_user_data(email):
#     """Fetch user data from Supabase or initialize if not found."""
#     response = supabase.table("user_data").select("data").eq("email", email).execute()
#     data = response.data

#     if not data:
#         # User doesn't exist yet, initialize
#         default_data = {
#             "courses_list": [],
#             "courses_colors": [],
#             "difficulty_ranking": [],
#             "tasks": [],
#             "complete_tasks": []
#         }

#         supabase.table("user_data").insert({
#             "email": email,
#             "data": default_data
#         }).execute()

#         return default_data

#     raw_data = data[0]["data"]
#     if isinstance(raw_data, str):
#         return json.loads(raw_data)
#     return raw_data


# def update_user_data(email, new_data):
#     """Update user's data field in Supabase."""
#     supabase.table("user_data").update({
#         "data": new_data
#     }).eq("email", email).execute()


# def course_manager(email):
#     st.title("📚 Course Manager")

#     # Fetch user data
#     user_data = get_user_data(email)

#     # Local editing state
#     courses = user_data.get("courses_list", [])

#     st.subheader("Your Courses")
#     if not courses:
#         st.info("No courses yet. Add one below.")
#     else:
#         for i, course in enumerate(courses):
#             col1, col2 = st.columns([6, 1])
#             col1.markdown(f"- **{course}**")
#             if col2.button("❌", key=f"del_{i}"):
#                 courses.pop(i)
#                 user_data["courses_list"] = courses
#                 update_user_data(email, user_data)
#                 st.rerun()

#     # Add a new course
#     st.subheader("Add a New Course")
#     new_course = st.text_input("Course Name", key="new_course")

#     if st.button("➕ Add Course"):
#         if new_course and new_course not in courses:
#             courses.append(new_course)
#             user_data["courses_list"] = courses
#             update_user_data(email, user_data)
#             st.success(f"Added course: {new_course}")
#             st.rerun()
#         elif new_course in courses:
#             st.warning("Course already exists.")
#         else:
#             st.error("Please enter a course name.")

# course_manager(st.session_state['username'])