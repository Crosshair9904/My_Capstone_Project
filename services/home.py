import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta, datetime
import openai
import google.generativeai as genai 
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import supabase
import json
from docx import Document
import io
import os
import base64
from pathlib import Path


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
            "written_notes":[ ],
            "uploaded_file":[],
            "ai_history":[],

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



# Initialize sectioned task list session state
if "today_tasks" not in st.session_state:
    st.session_state["today_tasks"] = []

if "this_week_tasks" not in st.session_state:
    st.session_state["this_week_tasks"] = []

if "ai_to_do_list_database" not in st.session_state:
    st.session_state["ai_to_do_list_database"] = []

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


# Function to Update Supabase Database 

def update_user_data(email, new_data):
    """Update user's data field in Supabase."""
    supabase.table("user_data").update({
        "data": new_data
    }).eq("email", email).execute()


def home_page(email):


    # Fetch user data
    user_data = get_user_data(email)

    # Get the data from database to edit within application
    courses = user_data.get("courses_list", [])
    colors = user_data.get("courses_colors", [])
    difficulty_ranking = user_data.get("difficulty_ranking", [])
    tasks = user_data.get("tasks", [])
    completed_tasks = user_data.get("complete_tasks", [])
    written_notes = user_data.get("written_notes", [])
    uploaded_file = user_data.get("uploaded_file", [])
    the_ai_history = user_data.get("ai_history", [])

    def ai_to_do_list():
        # Set default session variables
        if "ai_data_stale" not in st.session_state:
            st.session_state["ai_data_stale"] = True

        if "ai_to_do_list_database" not in st.session_state:
            st.session_state["ai_to_do_list_database"] = []

        # Configure the Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=genai.GenerationConfig(temperature=0.15)
        )

        prompt = f"""
        Your task is to output a list of which of the users tasks in the logical order that they should be done.

        Take the courses list and course difficulty as well as the tasks and their details in the database and create a list of which order to do the tasks in that is personalized to each users details.
        Take the names into consideration as well to determine the gravity of the task when determining the order.

        INPUTS
        difficulty: {difficulty_ranking}
        courses: {courses}
        tasks: {tasks}

        Formating requirements:
        Make it into a list that can be displayed in streamlit application
        YOU ARE ONLY OUTPUTING A LIST OF THE USER'S TASKS IN THE ORDER OF WHICH THEY SHOULD BE DONE BASED ON THE INPUTS
        DO NOT OUTPUT CODE OF ANY KIND, JUST THE LIST OF THE NAMES OF THE TASKS!!!!
        Do Not add extra unecessary characters like brackets in response, but ensure it remains a list, make it as easy as possible to incorporate response into a list

        What You Need To Output:
        - OUTPUT A POINT LIST THAT LISTS THE ORDER OF THE TASKS
        - Put them in a "To Do Today" category "To Do Afterwards" category and add a bit of space in between the two categories for easy legibility
        - If no other tasks after "To Do Today" category, do NOT include the "To Do Afterwards" category
        - If No tasks at all, just output "No Tasks To Order"
        """

        # If data was updated and AI list is stale, regenerate
        if st.session_state["ai_data_stale"]:
            with st.spinner("Generating Optimal Task Completion Order ..."):
                response = model.generate_content(prompt)
                ai_output = response.text
                st.session_state["ai_to_do_list_database"] = [ai_output]
                st.session_state["ai_data_stale"] = False  # Mark as up-to-date
                st.success("AI To-Do List Updated!")
        
        # Show current AI-generated list
        if st.session_state["ai_to_do_list_database"]:
            st.markdown(st.session_state["ai_to_do_list_database"][0])

        # Manual update option
        if st.button("Regenerate AI Task Order"):
            st.session_state["ai_data_stale"] = True

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

                    # ✅ Notes Section
                    st.title("Notes")
                    # Initialize notes if missing
                    if "written_notes" not in task:
                        task["written_notes"] = ""

                    task['written_notes'] = st.text_area(
                        "Jot Down Some Notes Here:", 
                        value=task["written_notes"], 
                        key=f"notes_{index}"
                    )

                    # ✅ File Upload
                    with st.expander("Upload Notes"):
                        uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"], key=f"uploaded_notes_{index}")

                                            
                        UPLOAD_DIR = Path("uploaded_docs")
                        UPLOAD_DIR.mkdir(exist_ok=True)

                        if uploaded_file is not None:
                            # Generate unique file name
                            file_extension = uploaded_file.name.split('.')[-1]
                            safe_task_name = task["name"].replace(" ", "_").lower()
                            file_name = f"{safe_task_name}_{index}.{file_extension}"
                            file_path = UPLOAD_DIR / file_name

                            # Save file to disk
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            # ✅ Save file metadata or path to task
                            task["uploaded_file_path"] = str(file_path)
                            task["uploaded_file_name"] = uploaded_file.name

                            # Show dialog with file content (optional)
                            @st.dialog("Uploaded File")
                            def view_uploaded_files():
                                docx_bytes = uploaded_file.getvalue()
                                doc_stream = io.BytesIO(docx_bytes)
                                document = Document(doc_stream)

                                st.subheader("Document Content:")
                                for paragraph in document.paragraphs:
                                    st.write(paragraph.text)

                                if document.tables:
                                    st.subheader("Tables:")
                                    for table in document.tables:
                                        for row in table.rows:
                                            row_data = [cell.text for cell in row.cells]
                                            st.write(row_data)

                            view_uploaded_files()
                            # Show previously uploaded file
                            if task.get("uploaded_file_path") and os.path.exists(task["uploaded_file_path"]):
                                st.info(f"Previously uploaded: {task['uploaded_file_name']}")
                                if st.button(f"Preview {task['uploaded_file_name']}", key=f"preview_{index}"):
                                    with open(task["uploaded_file_path"], "rb") as f:
                                        doc_stream = io.BytesIO(f.read())
                                        document = Document(doc_stream)
                                        st.subheader("Previously Uploaded Document:")
                                        for paragraph in document.paragraphs:
                                            st.write(paragraph.text)


                    with col3:
                        # Update Task Button
                        if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                            user_data["tasks"][index] = task
                            if uploaded_file is not None:
                                if "uploaded_file" not in user_data:
                                    user_data["uploaded_file"] = []
                                user_data['uploaded_file'].append(uploaded_file)
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True

                        # Mark Complete
                        if st.button(f"Mark As Complete", key=f"mark_complete_button_{index}"):
                            task["status"] = "Complete"
                            user_data["tasks"][index] = task
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True

                        # Delete Task
                        if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                            if "uploaded_file_path" in task and os.path.exists(task["uploaded_file_path"]):
                                os.remove(task["uploaded_file_path"])
                            del user_data["tasks"][index]
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True
                            break

                    # Move completed tasks to a separate list
                    if task["status"] == "Complete":
                        user_data.setdefault("complete_tasks", []).append(user_data["tasks"][index])
                        del user_data["tasks"][index]
                        update_user_data(email, user_data)
                        st.session_state["ai_data_stale"] = True
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
                        st.session_state["ai_data_stale"] = True                      
                        break
                if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                    del user_data["complete_tasks"][index]
                    update_user_data(email, user_data)
                    st.session_state["ai_data_stale"] = True
                    break


    # Add New Tasks
    # Menu Layout
    col1, col2, col3 = st.columns([2.3, 1, 2.3])

    with col2:
        st.markdown("# Home")


    with col2:
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
                                st.session_state["ai_data_stale"] = True
                                st.success(f"Added task: {new_task['name']}")
                                st.rerun()
                            elif new_task in tasks:
                                st.warning("Task already exists.")
                            else:
                                st.error("Please enter a task.")
            add_new_task()
    
    col1, col2 = st.columns([3,1.2])

    with col1:
        # Display the list of tasks for editing
        st.subheader("Current Tasks")
        if user_data['tasks']:
            
            display_tasks()
        else:
            st.write("No Tasks Available.")

    with col2:
        # Display The AI Ordered Task Completion List
        st.subheader("Advised Task Order Completion")
        ai_to_do_list()



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

        # Area for Complete Tasks
        st.subheader("Completed Tasks")
        if user_data['complete_tasks']:
            
            display_completed_tasks()

        else:
            st.write("You Have Not Completed Any Tasks.")

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









home_page(st.session_state['username'])
