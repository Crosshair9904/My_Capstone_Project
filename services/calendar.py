import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase


def get_user_session(username):
    """Get or initialize session state for a specific user."""
    if "user_sessions" not in st.session_state:
        st.session_state["user_sessions"] = {}

    if username not in st.session_state["user_sessions"]:
        # Initialize user-specific session state
        st.session_state["user_sessions"][username] = {
            "courses_list": [],
            "courses_colors": [],
            "difficulty_ranking": [],
            "tasks": [],
            "complete_tasks": [],
            # "today_tasks": [],
            # "this_week_tasks": [],
        }



    return st.session_state["user_sessions"][username]

# Get the logged-in user's session state
user_session = get_user_session(st.session_state["username"])

# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)

# Fetch all tasks
def get_tasks():
    """Fetch all tasks from the database."""
    response = supabase.table("user_data").select({"data": {"tasks": []}}).eq("email", st.session_state["username"]).execute()

    return response.data



st.title("Supabase Todo App")

if st.button("Update Information"):
    if st.session_state["user_sessions"][st.session_state['username']]:
        # Delete the current data so that it can be overwritten with new data
        response = supabase.table("user_data").select("*").eq("email", st.session_state["username"]).execute()

        if response.data:
            response = supabase.table("user_data").update({"data": {"tasks": st.session_state["user_sessions"][st.session_state["username"]]}}).eq("email", st.session_state['username']).execute()
            
            # #Add new/updated data
            # response = supabase.table("user_data").insert({
            #     "data": {"tasks": st.session_state["user_sessions"][st.session_state["username"]]}
            # }).execute()
    
        # else: 
        #     #Add new/updated data
        #     response = supabase.table("user_data").insert({
        #         "email": st.session_state["username"],
        #         "data": {"tasks": st.session_state["user_sessions"][st.session_state["username"]]}
        #     }).execute()
# Show the table

st.write("### Todo List:")
todos = get_tasks()
if todos:
    for todo in todos:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(todos)
else:
    st.write("No tasks available.")

# MAKE AN IF SO THAT IF A USER IS ALREADY THERE, SAY SO OR DO NOTHING

# TO USE IN CODE:
    # HAVE IT SO THAT IN THE UPDATE_TODAYS_TASKS FUNCTION, CREATE A TABLE FOR THE USER, THEN EVERYTIME THE TASKS LIST IS UPDATED, CLEAR THE ROW AND RE-ADD IT WITH THE NEW STUFF!!


# response = supabase.table("user_data").select("*").eq("email", st.session_state["username"]).execute()
# if response.data:
#     st.write(f"User found:", response.data)
# else:
#     st.write("No user found with that email.")

# # Add a new task
# def add_todo(task_name):
#     """Add a new task to the database."""
#     response = supabase.table("user_data").insert({"task": task_name}).execute()
#     if response.status_code != 200:
#         st.error("Failed to add task. Please try again.")

# # Fetch all tasks
# def get_todos():
#     """Fetch all tasks from the database."""
#     response = supabase.table("user_data").select("task").execute()
#     if response.status_code == 200:
#         return response.data
#     else:
#         st.error("Failed to fetch tasks. Please try again.")
#         return []

# # Delete a specific task
# def delete_todo(task_name):
#     """Delete a specific task from the database."""
#     response = supabase.table("user_data").delete().eq("task", task_name).execute()
#     if response.status_code == 200:
#         st.success(f"Task '{task_name}' deleted!")
#     else:
#         st.error("Failed to delete task. Please try again.")

# # Clear all tasks
# def clear_todo():
#     """Clear all tasks from the database."""
#     response = supabase.table("user_data").delete().execute()
#     if response.status_code == 200:
#         st.success("All tasks cleared!")
#     else:
#         st.error("Failed to clear tasks. Please try again.")

# # Streamlit app
# task = st.text_input("Add a new task:")
# if st.button("Add Task"):
#     if task:
#         add_todo(task)
#         st.success("Task added!")
#     else:
#         st.error("Please enter a task.")

# # Button to clear all tasks
# if st.button("Clear Tasks"):
#     clear_todo()

# st.write("### Todo List:")
# todos = get_todos()
# if todos:
#     for todo in todos:
#         col1, col2 = st.columns([3, 1])
#         with col1:
#             st.write(f"- {todo['task']}")
#         with col2:
#             if st.button(f"Delete", key=f"delete_{todo['task']}"):
#                 delete_todo(todo['task'])
# else:
#     st.write("No tasks available.")


# if st.session_state["user_sessions"][st.session_state["username"]]:
#     if supabase.table("user_data").select("*").eq("email", st.session_state["username"]).execute():
#         # Delete the current data so that it can be overwritten with new data
#         response = supabase.table("user_data").delete().eq("data", st.session_state["user_sessions"][st.session_state["username"]]).execute()
#         user_add = supabase.table("user_data").delete().eq("email", st.session_state["username"]).execute()

#         # Add new/updated data
#         response = supabase.table("user_data").insert({
#             "email": st.session_state["username"],
#             "data": {"tasks": st.session_state["user_sessions"][st.session_state["username"]]}
#         }).execute()
    
#     else: 
#         response = supabase.table("user_data").insert({
#             "email": st.session_state["username"],
#             "data": {"tasks": st.session_state["user_sessions"][st.session_state["username"]]}
#         }).execute()