import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client

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
            "today_tasks": [],
            "this_week_tasks": [],
        }

    return st.session_state["user_sessions"][username]

# Get the logged-in user's session state
user_session = get_user_session(st.session_state["username"])

# Initialize connection.
# Uses st.cache_resource to only run once.

def init_connection():
    url = st.secrets['connections']['supabase']['SUPABASE_URL']
    key = st.secrets['connections']['supabase']['SUPABASE_KEY']
    return create_client(url, key)

supabase = init_connection()

# Initialize the Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Perform a query to retrieve data from a table
# Replace "your_table_name" with the actual name of your table
# You can also specify specific columns instead of "*"
response = conn.table("AcingTask User Data").select().execute()

if response and response.data:
    st.write("## Contents of your_table_name:")
    for row in response.data:
        st.write(row)





#


