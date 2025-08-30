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

#Background
#Background
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


# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)


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


# Tell The User to Add Courses to The List If Not Done Already
if not user_session["courses_list"]:
    st.warning("Please Enter Courses In Settings")

# Initialize session state to hold tasks if it doesn't exist
if "tasks" not in user_session:
    user_session["tasks"] = []

# Initialize session state to hold complete tasks if it doesn't exist
if "complete_tasks" not in user_session:
    user_session["complete_tasks"] = []

if "today_tasks" not in user_session:
    user_session["today_tasks"] = []

if "this_week_tasks" not in user_session:
    user_session["this_week_tasks"] = []


def get_user_data(email):
    """
    Retrieve user data from the database.
    
    :param email: The user's email address.
    :return: A dictionary containing the user's lists or None if no data is found.
    """
    response = supabase.table("user_data").select("*").eq("email", email).execute()
    if response.data:
        return response.data[0]["data"]  # Return the 'data' field
    else:
        return None
    

def store_user_data(email, user_data):
    """
    Store or update user data in the database.
    
    :param email: The user's email address.
    :param user_data: A dictionary containing the user's lists.
    """
    # Check if the user already exists in the database
    existing_user = supabase.table("user_data").select("*").eq("email", email).execute()
    
    if existing_user.data:
        # Update the existing user's data
        response = supabase.table("user_data").update({"data": user_data}).eq("email", email).execute()
    else:
        # Insert new user data
        response = supabase.table("user_data").insert({"email": email, "data": user_data}).execute()
    
    return response



today = date.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)

def update_today_tasks():
    # Update today's and this week's tasks
    global today
    user_session["today_tasks"] = [
        task["name"]
        for task in user_session["tasks"]
        if task["due_date"] == today
    ]
    user_session["this_week_tasks"] = [
        task["name"]
        for task in user_session["tasks"]
        if start < task["due_date"] < end and task["due_date"] != today
    ]

    # Store the User Data in Supabase
    store_user_data(st.write(st.session_state.username), st.session_state["user_sessions"][username])

def display_tasks():
    global username
    """Display and edit tasks."""
    global today
    for index, task in enumerate(user_session["tasks"]):
        col1, col2 = st.columns([1.25, 3])

        with col1:
            # Color
            color_index = user_session["courses_list"].index(task["course"])
            color = user_session["courses_colors"][color_index]

            st.markdown(
                f"""
                <span style="
                    background-color: {color};
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                ">
                    {task['course']}
                </span>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            with st.expander(task["name"], expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    task["name"] = st.text_input("Name", value=task["name"], key=f"name_{index}")
                    task["course"] = st.selectbox(
                        "Course",
                        user_session["courses_list"],
                        index=user_session["courses_list"].index(task["course"]),
                        key=f"course_{index}",
                    )
                    task["due_date"] = st.date_input("Due Date", value=task["due_date"], key=f"date_{index}")
                with col2:
                    task["status"] = st.select_slider(
                        "Status",
                        ["Not Started", "In-Progress", "Near Completion", "Complete"],
                        value=task["status"],
                        key=f"status_{index}",
                    )
                    task["priority"] = st.select_slider(
                        "Priority",
                        ["Low", "Medium", "High"],
                        value=task["priority"],
                        key=f"priority_{index}",
                    )
                    task["effort"] = st.slider("Effort", min_value=1, max_value=5, value=task["effort"], key=f"effort_{index}")

                # Action Buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                        user_session["tasks"][index] = task
                        update_today_tasks()
                    if st.button(f"Mark As Complete", key=f"mark_complete_button_{index}"):
                        task["status"] = "Complete"
                        update_today_tasks()

                with col2:
                    if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                        del user_session["tasks"][index]
                        update_today_tasks()
                        break

                # Notes Section
                st.title("Notes")
                written_notes = st.text_area("Jot Down Some Notes Here:", key=f"notes_{index}")

                # File Upload
                with st.expander("Upload Notes"):
                    uploaded_files = st.file_uploader(
                        "Import Your Notes Here:", accept_multiple_files=True, key=f"uploaded_files_{index}"
                    )
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            st.subheader(f"File: {uploaded_file.name}")
                            if "text" in uploaded_file.type:
                                string_data = uploaded_file.getvalue().decode("utf-8")
                                st.text_area("Content:", value=string_data, height=200)
                            elif "image" in uploaded_file.type:
                                st.image(uploaded_file, caption=f"Image: {uploaded_file.name}")

                # Completed Tasks Sorting
                if task["status"] == "Complete":
                    user_session["complete_tasks"].append(user_session["tasks"][index])
                    del user_session["tasks"][index]
                    update_today_tasks()
                    break

def display_completed_tasks():
    """Display completed tasks."""
    for index, task in enumerate(user_session["complete_tasks"]):
        with st.expander(task["name"], expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                task["name"] = st.text_input("Name", value=task["name"], key=f"completed_name_{index}")
                task["course"] = st.selectbox(
                    "Course",
                    user_session["courses_list"],
                    index=user_session["courses_list"].index(task["course"]),
                    key=f"completed_course_{index}",
                )
                task["due_date"] = st.date_input("Date Completed", value=task["due_date"], key=f"completed_date_{index}")
            with col2:
                task["status"] = st.select_slider(
                    "Status",
                    ["Not Started", "In-Progress", "Near Completion", "Complete"],
                    value=task["status"],
                    key=f"completed_status_{index}",
                )
                task["priority"] = st.select_slider(
                    "Priority",
                    ["Low", "Medium", "High"],
                    value=task["priority"],
                    key=f"completed_priority_{index}",
                )
                task["effort"] = st.slider("Effort", min_value=1, max_value=5, value=task["effort"], key=f"completed_effort_{index}")

            # Buttons
            if st.button(f"Move to Active Tasks List", key=f"re_add_{index}"):
                task["status"] = "In-Progress"
                user_session["tasks"].append(user_session["complete_tasks"][index])
                del user_session["complete_tasks"][index]
                update_today_tasks()
                break
            if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                del user_session["complete_tasks"][index]
                update_today_tasks()
                break

# Menu Layout
col1, col2, col3 = st.columns([2.5, 3, 1])

with col2:
    st.markdown("# Home")


col1, col2, col3= st.columns([1, 1.75, 1])

with col2:

    # Collapsible form for adding new tasks with tabs
    with st.expander("Add New Task", expanded=False):
        with st.form("Adding Tasks", clear_on_submit=True):
            tab1, tab2, tab3 = st.tabs(["Task Details", "Additional Details", "Submit"]) 
            
            # Task Details
            with tab1:
                st.header("Task Details")
                new_task = {
                    "name": st.text_input("Task Name:"),
                    "course": st.selectbox("Course:", user_session["courses_list"]),
                    #"due_date": st.date_input("Due Date:")
                }
            
            # Additional Details
            with tab2:
                st.header("Additional Details")
                new_task["status"] = st.select_slider("Status:", ["Not Started", "In-Progress", "Near Completion", "Complete"])
                new_task["priority"] = st.select_slider("Priority:", ["Low", "Medium", "High"])
                new_task["effort"] = st.slider("Effort Required:", min_value=1, max_value=5)

            # Submit
            with tab3:
                if st.form_submit_button("Submit"):
                    #user_session["tasks"].append(new_task)
                    supabase.table('user_data').insert({'data': new_task}).execute()
                    update_today_tasks()
                    st.success("Task added!")


col1, col2 =st.columns([2, 1])

with col1:
    # Display the list of tasks for editing
    st.subheader("Current Tasks")
    if user_session['tasks']:
        
        display_tasks()
    else:
        st.write("No Tasks Available.")

with col2:
    # Area for Complete Tasks
    st.subheader("Completed Tasks")
    if user_session['complete_tasks']:
        
        display_completed_tasks()

    else:
        st.write("You Have Not Completed Any Tasks.")


col1, col2= st.columns([1, 2.5])



#Indicator of what is due today
with col1:
    st.subheader("Tasks Due Today:")    #if st.button("Clear List of Today's Tasks"):
        #st.session_state.today_tasks.clear()

    if user_session["today_tasks"]:
        for task_name in user_session['today_tasks']:
            # Use markdown for a cleaner display
            st.markdown(f"- **{task_name}**")
    else:
        st.write("No Tasks Due For Today")

# Indicator of what is due later in the same week
    st.subheader("Tasks Due Later This Week:")

    if user_session['this_week_tasks']:
        for task_name in user_session['this_week_tasks']:
            st.markdown(f"- **{task_name}**")
    else:
        st.write("No Tasks Due This Week")



# The calendar
with col2:

    # The Calendar

    st.subheader("Calendar")

    


    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridDay,dayGridWeek,dayGridMonth",
        },
        "initialView": "dayGridMonth",
        "editable": True,
        "selectable": True,
        "selectMirror": True,
    }



    # Initialize events list
    events = []




    # Function to add events to the calendar
    def add_events_to_calendar():
        for index, task in enumerate(user_session['tasks']):
            name = task['name'] 

            # Color
            color_index = user_session['courses_list'].index(task['course'])
            color = user_session['courses_colors'][color_index]

            due_date = str(task['due_date'])

            events.append(
                {
                    "title": name,
                    "color": color,
                    "start": due_date,
                }
            )

    # Call the function to add events
    add_events_to_calendar()

    # Render the calendar with the updated events
    state = calendar(
        events=events,
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity:0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 600;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        
        """,
        key='calendar',
    )

    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

import socket
try:
    print(socket.gethostbyname('<your-supabase-ref>.supabase.co'))
except Exception as e:
    print(f"DNS resolution failed: {e}")
