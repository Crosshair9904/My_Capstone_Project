import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client


#TO RUN APP: RUN THE CODE AND TAKE THE PATH AND USE THE RUN COMMAND IN TERMINAL

def get_user_session(username):
    # Get / initialize session state for a specific user
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

url = st.secrets['connections']['supabase_url']
key = st.secrets['connections']['supabase_key']


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
    get_user_session(username)

def main_app(user_email):

    login(user_email) # used to start the session state individually for each user's email

    with st.sidebar:
        st.title("🎉 Welcome Page")
        st.success(f"Welcome, {user_email}! 👋")
        if st.button("Logout"):
            sign_out()
    
    #all the pages setup
    #logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("services/settings.py", title="Settings", icon=":material/settings:")
    calendar = st.Page("services/calendar.py", title="Calendar", icon=":material/settings:")

    home = st.Page(
    "services/home.py",
    title="Home",
    icon=":material/home:",
    )
    ai = st.Page("services/ai.py", title="Ai Tools", icon=":material/network_intelligence:")

    #defines page groups
    account_pages = [settings]
    services_pages = [home, ai, calendar]

    page_dict = {}
    page_dict["Services"] = services_pages


    if len(page_dict) > 0:
        pg = st.navigation({"Account": account_pages} | page_dict)

    pg.run()

def auth_screen():
    st.title("Please Login or Sign Up If This Is The First Time")
    option = st.selectbox("Choose an action:", ["Login", "Sign Up"])
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


