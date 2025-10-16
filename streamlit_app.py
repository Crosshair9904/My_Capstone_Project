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
    get_user_session(username)

def main_app(user_email):

    login(user_email) # used to start the session state individually for each user's email

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
    services_pages = [home]

    page_dict = {}
    page_dict["Services"] = services_pages


    if len(page_dict) > 0:
        pg = st.navigation({"Account": account_pages} | page_dict)

    pg.run()
    
@st.dialog("Please Login or Sign Up")
def auth_screen():    
    
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


