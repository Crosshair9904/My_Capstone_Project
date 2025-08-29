import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
from datetime import datetime, timedelta


#TO RUN APP: RUN THE CODE AND TAKE THE PATH AND USE THE RUN COMMAND IN TERMINAL

# Access user data from secrets
USER_DATA = st.secrets["users"]

# Set session timeout duration (e.g., 30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

def authenticate(username, password):
    """Authenticate user by checking their credentials."""
    if username in USER_DATA and USER_DATA[username] == password:
        return True
    return False

def login(username):
    """Log in the user and set session state."""
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["login_time"] = datetime.now()

def logout():
    """Log out the user and clear session state."""
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["login_time"] = None

def check_session_timeout():
    """Log out the user if the session has expired."""
    if (
        "login_time" in st.session_state
        and datetime.now() - st.session_state["login_time"] > SESSION_TIMEOUT
    ):
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
    """Display the user's dashboard."""
    st.title(f"Welcome, {st.session_state['username']}!")
    st.write("This is your personalized dashboard.")
    if st.button("Logout"):
        logout()
        st.rerun()

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


#all the pages setup
#logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("services/settings.py", title="Settings", icon=":material/settings:")

home = st.Page(
"services/home.py",
title="Home",
icon=":material/home:",
)
ai = st.Page("services/ai.py", title="Ai Tools", icon=":material/network_intelligence:")

#defines page groups
account_pages = [settings]
services_pages = [home, ai]

page_dict = {}
page_dict["Services"] = services_pages


if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)

pg.run()


