import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta
import pandas as pd
from io import StringIO
import openai

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

#REMEMBER TO ADD WHAT IS NEEDED FOR COPYWRITE ON GOOGLE LOGIN









# Tell The User to Add Courses to The List If Not Done Already
if 'courses_list' not in st.session_state:
    st.warning("Please Enter Courses In Settings")


# Initialize session state to hold tasks if it doesn't exist
if 'tasks' not in st.session_state:
    st.session_state.tasks = []


# Initialize session state to hold complete task if it doesn't exist
if 'complete_tasks' not in st.session_state:
    st.session_state.complete_tasks = []

if 'today_tasks' not in st.session_state:
    st.session_state.today_tasks = []

if 'this_week_tasks' not in st.session_state:
    st.session_state.this_week_tasks = []

today = date.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)

def update_today_tasks():
    global today
    # Update the list with tasks due today
    st.session_state.today_tasks = [
        task['name']
        for task in st.session_state.tasks
        if task['due_date'] == today
    ]
    # Update the list with tasks due later in the same week
    st.session_state.this_week_tasks = [
        task['name']
        for task in st.session_state.tasks
        if task['due_date'] > start and task['due_date'] < end and task['due_date'] != today
    ]


# Function to display and edit tasks
def display_tasks():
    global today
    for index, task in enumerate(st.session_state.tasks):
    # uses enumerate to iterate through all the data while keeping track of the indexs to sort the data
    # uses index to allow for multiple of the same variable to exist and have different stored data at the same time
        col1, col2 = st.columns([0.76, 3])

        with col1:
            # Color
            color_index = st.session_state.courses_list.index(task['course'])
            color = st.session_state.courses_colors[color_index]
            

            # Define your RGB color
            rgb_color = color # Example: Tomato red

            st.markdown(
                f"""
                <span style="
                    background-color: {rgb_color};
                    color: white; /* Text color for contrast */
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                ">
                    {task['course']}
                
                """,
                unsafe_allow_html=True
)


        with col2:
            with st.expander(task['name'], expanded=False,): #adds the name of each task on it's respective tab
                col1, col2 = st.columns(2)  # create two columns for compact layout
                with col1: # first column
                    task['name'] = st.text_input("Name", value=task['name'], key=f"name_{index}")
                    task['course'] = st.selectbox("Course", st.session_state.courses_list, index=st.session_state.courses_list.index(task['course']), key=f"course_{index}")
                    task['due_date'] = st.date_input("Due Date", value=task['due_date'], key=f"date_{index}")
                with col2: # second column
                    task['status'] = st.select_slider("Status", ["Not Started", "In-Progress", "Near Completion", "Complete"], value=task['status'], key=f"status_{index}")
                    task['priority'] = st.select_slider("Priority", ["Low", "Medium", "High"], value=task['priority'], key=f"priority_{index}")
                    task['effort'] = st.slider("Effort", min_value=1, max_value=5, value=task['effort'], key=f"effort_{index}")
                
                #Action Buttons
                col1, col2 = st.columns(2)
                with col1:
                    col1a, col2a = st.columns(2)
                    with col1a:
                        if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                            st.session_state.tasks[index] = task
                            update_today_tasks()  
                    with col2a:
                        if st.button(f"Mark As Complete", key=f"mark_complete_button_{index}"):
                            task['status'] = "Complete"
                            update_today_tasks()  
                        
                    with col2:    
                        # Delete button
                        with st.expander("Delete Task"):
                            if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                                del st.session_state.tasks[index] #deletes the task information from the place of which it is stored
                                update_today_tasks()
                                break  # exit the loop to refresh the display
                with col2:
                    # Notes Section
                    st.title("Notes")

                    # section to jot down a few notes (not uploaded file)
                    written_notes = st.text_area("Jot Down Some Notes Here:", key=f"notes_{index}")
        
                    # Area for a to-do list (button to access)
                    
                    # section to upload a file
                    with st.expander("Upload Notes"):
                        uploaded_files = st.file_uploader(
                        "Import Your Notes Here:", accept_multiple_files=True, key=f"uploaded_files_{index}",
                        )
                        

                    # expander to show the file
                    with st.expander("Display File"):
                        if uploaded_files: # Check if the list is not empty
                            for uploaded_file in uploaded_files:
                                st.subheader(f"File: {uploaded_file.name}")
                                st.write(f"Type: {uploaded_file.type}")
                                st.write(f"Size: {uploaded_file.size} bytes")

                                if "text" in uploaded_file.type:
                                    string_data = uploaded_file.getvalue().decode("utf-8")
                                    st.text_area("Content:", value=string_data, height=200)
                                elif "image" in uploaded_file.type:
                                    st.image(uploaded_file, caption=f"Image: {uploaded_file.name}")
                



            with col1:
                # AI Section

                st.title("AI")

                # Create quizzes or study questions from notes ()
            #- Answer questions from the notes, summarize them, do additional research
            #- Create a task manager to divide work into easier chunks that the user can tick off
            #- Record a lecture or brainstorm session and summarize content into notes or a vision board
            #- Find additional resources to help with comprehension and studying








            #Completed Tasks Sorting
            if task['status'] == "Complete":
                st.session_state.complete_tasks.append(st.session_state.tasks[index])
                del st.session_state.tasks[index]
                update_today_tasks()
                break

            



# Display to view completed tasks
def display_completed_tasks():
    for index, task in enumerate(st.session_state.complete_tasks):
         with st.expander(task['name'], expanded=False,):
            col1, col2 = st.columns(2)  # create two columns for compact layout
            with col1: # first column
                task['name'] = st.text_input("Name", value=task['name'], key=f"completed_name_{index},")
                task['course'] = st.selectbox("Course", st.session_state.courses_list, index=st.session_state.courses_list.index(task['course']), key=f"completed_course_{index}")
                task['due_date'] = st.date_input("Date Completed", value=task['due_date'], key=f"completed_date_{index}")
            with col2: # second column
                task['status'] = st.select_slider("Status", ["Not Started", "In-Progress", "Near Completion", "Complete"], value=task['status'], key=f"completed_status_{index}")
                task['priority'] = st.select_slider("Priority", ["Low", "Medium", "High"], value=task['priority'], key=f"completed_priority_{index}")
                task['effort'] = st.slider("Effort", min_value=1, max_value=5, value=task['effort'], key=f"completed_effort_{index}")


            col1, col2 = st.columns(2)
            # Button To Add A Task Back To Tasks List
            with col1:
                if st.button(f"Move to Active Tasks List", key=f"re_add_{index},"):
                    task['status'] = 'In-Progress'
                    st.session_state.tasks.append(st.session_state.complete_tasks[index])
                    del st.session_state.complete_tasks[index]
                    update_today_tasks()
                    break


            # Button to remove task from completed list
            with col2:
                if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index},"):
                    del st.session_state.complete_tasks[index]
                    update_today_tasks()
                    break



# Menu Layout
col1, col2, col3 = st.columns([2.5, 3, 1])

with col2:
    st.markdown("# Home")


col1, col2, col3= st.columns([0.7, 1.75, 1])

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
                    "course": st.selectbox("Course:", st.session_state.courses_list),
                    "due_date": st.date_input("Due Date:")
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
                    st.session_state.tasks.append(new_task)
                    update_today_tasks()
                    st.success("Task added!")


col1, col2, col3= st.columns([1, 1.75, 1])

with col1:
    # Display the list of tasks for editing
    st.subheader("Current Tasks")
    if st.session_state.tasks:
        
        display_tasks()
    else:
        st.write("No Tasks Available.")

with col3:
    # Area for Complete Tasks
    st.subheader("Completed Tasks")
    if st.session_state.complete_tasks:
        
        display_completed_tasks()

    else:
        st.write("You Have Not Completed Any Tasks.")

col1, col2= st.columns([1, 2.5])



#Indicator of what is due today
with col1:
    st.subheader("Tasks Due Today:")    #if st.button("Clear List of Today's Tasks"):
        #st.session_state.today_tasks.clear()

    if st.session_state.today_tasks:
        for task_name in st.session_state.today_tasks:
            # Use markdown for a cleaner display
            st.markdown(f"- **{task_name}**")
    else:
        st.write("No Tasks Due For Today")

# Indicator of what is due later in the same week
    st.subheader("Tasks Due Later This Week:")

    if st.session_state.this_week_tasks:
        for task_name in st.session_state.this_week_tasks:
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
        for index, task in enumerate(st.session_state.tasks):
            name = task['name'] 

            # Color
            color_index = st.session_state.courses_list.index(task['course'])
            color = st.session_state.courses_colors[color_index]

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
