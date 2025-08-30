import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase




# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)


def get_todos():
    response = supabase.table('todos').select('*').execute()
    return response.data


def add_todo(task):
    supabase.table('todos').insert({'task': task}).execute()


# def clear_todo():
#     supabase.table('todos').delete().eq("id", 0, 1).execute()

st.title("Supabase Todo App")

task = st.text_input("Add a new task:")
if st.button("Add Task"):
    if task:
        add_todo(task)
        st.success("Task added!")
    else:
        st.error("Please enter a task.")
# if st.button("Clear Tasks"):
#     clear_todo()

st.write("### Todo List:")
todos = get_todos()
if todos:
    for todo in todos:
        st.write(f"- {todo['task']}")
else:
    st.write("No tasks available.")