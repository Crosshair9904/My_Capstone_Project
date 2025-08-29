import streamlit as st
import streamlit_authenticator as stauth  
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection


#TO RUN APP: RUN THE CODE AND TAKE THE PATH AND USE THE RUN COMMAND IN TERMINAL

# Access user data from secrets
USER_DATA = st.secrets["users"]

# Set session timeout duration 
SESSION_TIMEOUT = timedelta(minutes=30)

def authenticate(username, password):
    # Authenticate user by checking their credentials
    if username in USER_DATA and USER_DATA[username] == password:
        return True
    return False


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


def login(username):
    # Log in the user and set session state
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["login_time"] = datetime.now()  # Set login time
    # Initialize user-specific session state
    get_user_session(username)

def logout():
    # Log out the user
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["login_time"] = None

def check_session_timeout():
    # Log out the user if the session has expired 
    login_time = st.session_state.get("login_time", None)  # Get login time or None
    if login_time is None:
        return  # Skip timeout check if login_time is not set

    if datetime.now() - login_time > SESSION_TIMEOUT:
        st.warning("Session expired. Please log in again.")
        logout()
        st.rerun()

def login_page():
    # Display the login page
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            login(username)
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

def user_dashboard():
    # Display the user's dashboard 
    
    with st.sidebar:
        st.title(f"Welcome, {st.session_state['username']}!")
        st.write("This is your personalized dashboard.")
        if st.button("Logout"):
            logout()
            st.rerun()


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

def main():
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["login_time"] = None

    # Check session timeout
    if st.session_state["logged_in"]:
        check_session_timeout()

    # Display login page or user dashboard
    if st.session_state["logged_in"]:
        user_dashboard()
    else:
        login_page()

if __name__ == "__main__": 
    main()




