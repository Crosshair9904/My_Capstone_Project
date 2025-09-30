import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta, datetime
import openai
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import json
from docx import Document
import io


# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)

# Setting the Background
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

# Setting The User Session
def get_user_data(email):
    # Fetch user data from Supabase or initialize if not found
    response = supabase.table("user_data").select("data").eq("email", email).execute()
    data = response.data

    if not data:
        # User doesn't exist yet, initialize
        default_data = {
            "courses_list": [],
            "courses_colors": [],
            "difficulty_ranking": [],
            "tasks": [],
            "complete_tasks": [],
            "written_notes":[],
            "uploaded_file":[],

        }

        supabase.table("user_data").insert({
            "email": email,
            "data": default_data
        }).execute()

        return default_data

    # Ensures that the data coming to the app is a string and what goes to the database is json compatible 

    raw_data = data[0]["data"]
    if isinstance(raw_data, str):
        return json.loads(raw_data)
    return raw_data


# Function to Update Supabase Database 

def update_user_data(email, new_data):
    """Update user's data field in Supabase."""
    supabase.table("user_data").update({
        "data": new_data
    }).eq("email", email).execute()



# Initialize list session state
if "today_tasks" not in st.session_state:
    st.session_state["today_tasks"] = []

if "this_week_tasks" not in st.session_state:
    st.session_state["this_week_tasks"] = []

def get_week_bounds():
    """Return today's date, start of week, and end of week (all as date objects)."""
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.isoweekday() - 1)  # Monday start
    end_of_week = start_of_week + timedelta(days=6)
    return today, start_of_week, end_of_week


user_data = get_user_data(st.session_state['username'])
today, start, end = get_week_bounds()

def parse(d):
        return datetime.fromisoformat(d).date()  # all tasks stored as strings
todays_tasks = [
        task["name"]
        for task in user_data['tasks']
        if parse(task["due_date"]) == today
    ]

this_weeks_tasks = [
    task["name"]
    for task in user_data['tasks']
    if start <= parse(task["due_date"]) <= end and parse(task["due_date"]) != today
]


def home_page(email):


    # Fetch user data
    user_data = get_user_data(email)

    # Get the data from database to edit within application
    courses = user_data.get("courses_list", [])
    colors = user_data.get("courses_colors", [])
    difficulty_ranking = user_data.get("difficulty_ranking", [])
    tasks = user_data.get("tasks", [])
    completed_tasks = user_data.get("complete_tasks", [])
    written_notes = user_data.get("written_notes",[])
    uploaded_file = user_data.get("uploaded_file",[])

    if not courses:
        st.warning("Please Enter Your Courses In The Setting Menu Before Continuing")

    # Display the Tasks
    def display_tasks():
        global username
        # Display and edit tasks
        global today
        for index, task in enumerate(user_data["tasks"]):
            col1, col2 = st.columns([0.55, 3])

            with col1:
                # Color
                color_index = user_data["courses_list"].index(task["course"])
                color = user_data["courses_colors"][color_index]
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
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        task["name"] = st.text_input("Name", value=task["name"], key=f"name_{index}")
                        task["course"] = st.selectbox(
                            "Course",
                            user_data["courses_list"],
                            index=user_data["courses_list"].index(task["course"]),
                            key=f"course_{index}",
                        )
                        task["due_date"] = st.date_input("Due Date", value=task["due_date"], key=f"date_{index}").isoformat()
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

                    
                    
                    # Notes Section
                    st.title("Notes")
                    written_notes = st.text_area("Jot Down Some Notes Here:", key=f"notes_{index}")

                    # File Upload
                    with st.expander("Upload Notes"):
                        uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"], key=f"uploaded_notes_{index}")

                    if uploaded_file is not None:
                        @st.dialog("Uploaded_File")
                        def view_uploaded_files():
                            # Read the uploaded file as bytes
                            docx_bytes = uploaded_file.getvalue()

                            # Create a BytesIO object to pass to python-docx
                            doc_stream = io.BytesIO(docx_bytes)

                            # Load the document using python-docx
                            document = Document(doc_stream)

                            st.subheader("Document Content:")

                            # Go through paragraphs and display their text
                            for paragraph in document.paragraphs:
                                st.write(paragraph.text)

                            # Display tables if present
                            if document.tables:
                                st.subheader("Tables:")
                                for table in document.tables:
                                    for row in table.rows:
                                        row_data = [cell.text for cell in row.cells]
                                        st.write(row_data) 
                        view_uploaded_files()
                    with col3:
                        # Action Buttons
                        if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                            user_data["tasks"][index] = task
                            if uploaded_file is not None:
                                user_data['uploaded_file'].append(uploaded_file)
                            update_user_data(email, user_data)     
                       
                        if st.button(f"Mark As Complete", key=f"mark_complete_button_{index}"):
                            task["status"] = "Complete"
                            update_user_data(email, user_data)
                    
                        if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                            del user_data["tasks"][index]
                            update_user_data(email, user_data)
                            break

                    # Completed Tasks Sorting
                    if task["status"] == "Complete":
                        user_data["complete_tasks"].append(user_data["tasks"][index])
                        del user_data["tasks"][index]
                        update_user_data(email, user_data)
                        break

    # Display the Completed Tasks
    def display_completed_tasks():
        """Display completed tasks."""
        for index, task in enumerate(user_data["complete_tasks"]):
            with st.expander(task["name"], expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    task["name"] = st.text_input("Name", value=task["name"], key=f"completed_name_{index}")
                    task["course"] = st.selectbox(
                        "Course",
                        user_data["courses_list"],
                        index=user_data["courses_list"].index(task["course"]),
                        key=f"completed_course_{index}",
                    )
                with col2:
                    task["due_date"] = st.date_input("Date Completed", value=datetime.today().date(), key=f"completed_date_{index}").isoformat()
                # with col2:
                #     task["status"] = st.select_slider(
                #         "Status",
                #         ["Not Started", "In-Progress", "Near Completion", "Complete"],
                #         value=task["status"],
                #         key=f"completed_status_{index}",
                #     )
                #     task["priority"] = st.select_slider(
                #         "Priority",
                #         ["Low", "Medium", "High"],
                #         value=task["priority"],
                #         key=f"completed_priority_{index}",
                #     )
                #     task["effort"] = st.slider("Effort", min_value=1, max_value=5, value=task["effort"], key=f"completed_effort_{index}")
                
                # Buttons
                    if st.button(f"Move to Active Tasks List", key=f"re_add_{index}"):
                        task["status"] = "In-Progress"
                        user_data["tasks"].append(user_data["complete_tasks"][index])
                        del user_data["complete_tasks"][index]
                        update_user_data(email, user_data)                        
                        break
                if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                    del user_data["complete_tasks"][index]
                    update_user_data(email, user_data)
                    break


    # Add New Tasks
    # Menu Layout
    col1, col2, col3 = st.columns([2.3, 1, 2.3])

    with col1:
        st.markdown("# Home")

    col1, col2 = st.columns([1,4])

    with col1:
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        if st.button("Add New Task"):
            @st.dialog("Add New Task")
            def add_new_task():
                with st.form("Adding Tasks", clear_on_submit=True):
                    tab1, tab2, tab3 = st.tabs(["Task Details", "Additional Details", "Submit"]) 
                    
                    # Task Details
                    with tab1:
                        st.header("Task Details")
                        new_task = {
                            "name": st.text_input("Task Name:"),
                            "course": st.selectbox("Course:", user_data["courses_list"]),
                            "due_date": st.date_input("Due Date:").isoformat()
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
                            if new_task and new_task not in tasks:
                                tasks.append(new_task)
                                user_data["tasks"] = tasks
                                update_user_data(email, user_data)
                                st.success(f"Added task: {new_task['name']}")
                                st.rerun()
                            elif new_task in tasks:
                                st.warning("Task already exists.")
                            else:
                                st.error("Please enter a task.")
            add_new_task()
    with col2:
        st.empty()
        # Display the list of tasks for editing
        st.subheader("Current Tasks")
        if user_data['tasks']:
            
            display_tasks()
        else:
            st.write("No Tasks Available.")



    col1, col2= st.columns([1, 2.5])



    #Indicator of what is due today
    with col1:
        st.subheader("Tasks Due Today:")    #if st.button("Clear List of Today's Tasks"):
            #st.session_state.today_tasks.clear()

        if todays_tasks:
            for task_name in todays_tasks:
                st.markdown(f"- **{task_name}**")
        else:
            st.write("No Tasks Due For Today")

    # Indicator of what is due later in the same week
        st.subheader("Tasks Due Later This Week:")

        if this_weeks_tasks:
            for task_name in this_weeks_tasks:
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
            for index, task in enumerate(user_data['tasks']):
                name = task['name'] 

                # Color
                color_index = user_data['courses_list'].index(task['course'])
                color = user_data['courses_colors'][color_index]

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

    # Area for Complete Tasks
    st.subheader("Completed Tasks")
    if user_data['complete_tasks']:
        
        display_completed_tasks()

    else:
        st.write("You Have Not Completed Any Tasks.")








home_page(st.session_state['username'])
