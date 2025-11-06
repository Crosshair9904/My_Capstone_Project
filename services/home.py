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

# Frosted Glass Theme CSS
st.markdown("""
<style>
/* --- Buttons --- */
button[kind="secondary"], button[kind="primary"], div.stButton > button {
    background-color: rgba(255, 255, 255, 0.08) !important; /* semi-transparent */
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(6px);
    transition: 0.3s ease-in-out;
    border-radius: 8px;
}

/* Button hover */
div.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}

/* --- Dialogs / Modals --- */
.stDialog, .stModal, div[data-testid="stModal"], div[data-testid="stDialog"] {
    background-color: rgba(30, 30, 30, 0.4) !important;
    color: white !important;
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.25);
}

/* Inner containers in dialogs */
.stDialog div, .stModal div {
    background-color: transparent !important;
}

/* --- Inputs / Textareas / Selects --- */
input, select, textarea {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 6px;
}

/* --- Popovers (expanded content) --- */
div[data-baseweb="popover"] {
    background-color: rgba(30, 30, 30, 0.4) !important; 
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    box-shadow: none !important;
    backdrop-filter: blur(10px) !important;
}

         

/* Popover inner elements */
div[data-baseweb="popover"] * {
    background-color: transparent !important;
    color: white !important;
}

/* Optional: Adjust popover arrow to match background */
div[data-baseweb="popover"]::after {
    background-color: rgba(30, 30, 30, 0.4) !important;
}
            


/* Button hover effect */
div.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
    border: 2px solid rgba(255, 255, 255, 0.7) !important;
}

/* Transparent container with borders and frosted glass */
.task-container {
    background-color: rgba(0, 0, 0, 0) !important; /* fully transparent */
    color: white !important;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.5); /* visible border */
    padding: 15px;
    margin-top: 5px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px); /* frosted effect */
}

/* --- Frosted Expanders --- */
div.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 10px !important;
    color: white !important;
    transition: all 0.3s ease-in-out !important;
}


/* Hover / active glow for expander header */
div.streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
}

/* Remove Streamlit default shadows */
div[data-testid="stExpander"] {
    box-shadow: none !important;
}
            
/* --- Frosted Expanders --- */
.frosted-expander-header {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 10px;
    color: white;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease-in-out;
}
.frosted-expander-header:hover {
    background: rgba(255, 255, 255, 0.18);
    border-color: rgba(255, 255, 255, 0.4);
}

.frosted-expander-content {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 0 15px;
    color: white;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease, padding 0.3s ease;
}
.frosted-expander-content.show {
    max-height: 1000px; /* Large enough to show full content */
    padding: 15px;
}
</style>

<script>
function toggleExpander(index) {
    const all = document.querySelectorAll('.frosted-expander-content');
    all.forEach(div => {
        if (div.id === `expander-${index}`) {
            div.classList.toggle('show');
        } else {
            div.classList.remove('show');
        }
    });
}
</script>
""", unsafe_allow_html=True)


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
            "ai_use_task_ordering":[],
            "ai_use_ai_priority":[],
            "ai_document_assistant":[],
            "ai_use_history":[],

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


    if "ai_quiz" not in st.session_state:
            st.session_state["ai_quiz"]  = []
    if "ai_data_stale" not in st.session_state:
            st.session_state["ai_data_stale"] = True
    if "ai_data_stale_priority" not in st.session_state:
            st.session_state["ai_data_stale_priority"] = True
    if "ai_priority" not in st.session_state:
        st.session_state['ai_priority'] = "To Be Determined"


    
    def ai_to_do_list():
        if user_data['ai_use_task_ordering'] == True:
            # Set default session variables
            # if "ai_data_stale" not in st.session_state:
            #     st.session_state["ai_data_stale"] = True

            if "ai_to_do_list_database" not in st.session_state:
                st.session_state["ai_to_do_list_database"] = []
            
            if "current_ai_session" not in st.session_state:
                st.session_state["current_ai_session"] = []


            # Configure the Gemini API
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=genai.GenerationConfig(temperature=0.0)
            )

            prompt = f"""
            Your task is to output a list of which of the users tasks in the logical order that they should be done in the most time efficient manor.

            Take the courses list and course difficulty as well as the tasks and their details in the database and create a list of which order to do the tasks in that is personalized to each users details.
            Take the names as well as the status of the tasks into consideration as well to determine the gravity of the task when determining the order.

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
            - If No current tasks at all in the database, just output "No Tasks To Order"
            - ONLY If tasks have the exact same name, stick the name of their respective course in brackets when listing them in the completion order
            - OUTPUT AS QUICKLY AS POSSIBLE WHILE STILL BEING AS ACCURATE AS POSSIBLE
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
            if st.button("Regenerate AI Task Order", key = "generate_ai_task_order_button"):
                st.session_state["ai_data_stale"] = True

        if not courses:
            st.warning("Please Enter Your Courses In The Setting Menu Before Continuing")


    def display_tasks():
        global username
        global today

        # Sort tasks: overdue first, then upcoming in chronological order
        sorted_tasks = sorted(
            user_data["tasks"],
            key=lambda t: (
                datetime.fromisoformat(t["due_date"]).date() >= today,
                datetime.fromisoformat(t["due_date"]).date()
            )
        )

        for index, task in enumerate(sorted_tasks):
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

               # Unique key for each task
                expander_key = f"task_open_{index}"

                # Toggle button
                if expander_key not in st.session_state:
                    st.session_state[expander_key] = False

                if st.button(task["name"], key=f"toggle_{index}", use_container_width=True):
                    st.session_state[expander_key] = not st.session_state[expander_key]

                # Container for task content
                if st.session_state[expander_key]:
                    st.markdown('<div class="task-container">', unsafe_allow_html=True)

                    # ---- Task details go inside here ----
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
                        task["effort"] = st.slider("Effort", min_value=1, max_value=5, value=task["effort"], key=f"effort_{index}")


                    

                    # --- AI or Manual Priority System (All Recalculate, Each Displays Its Own) ---

                    priority_prefix = "ai_priority_"
                    stale_key = "ai_data_stale_priority_all"

                    # --- Handle AI-based Priority Mode ---
                    if user_data.get("ai_use_ai_priority", False):

                        # Button (shown per task) — triggers all regeneration
                        if st.button("Regenerate Task Priority", key=f"regenerate_priority_btn_{index}"):
                            st.session_state[stale_key] = True

                        # Initialize state defaults
                        if stale_key not in st.session_state:
                            st.session_state[stale_key] = True

                        # --- Recalculate All Task Priorities if Needed ---
                        if st.session_state[stale_key]:
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            model = genai.GenerativeModel(
                                model_name="gemini-2.5-flash",
                                generation_config=genai.GenerationConfig(temperature=0.0)
                            )

                            # Summarize all tasks for context
                            task_descriptions = []
                            for i, t in enumerate(user_data["tasks"]):
                                desc = f"{i+1}. {t['name']} (Course: {t['course']}, Difficulty: {t.get('difficulty', 'N/A')}, Due: {t['due_date']})"
                                task_descriptions.append(desc)
                            all_tasks_text = "\n".join(task_descriptions)

                            # AI prompt (batch mode)
                            prompt = f"""
                            You are an academic task prioritization assistant.

                            Your job is to assign a single-word **priority rating** ("High", "Medium", or "Low") to each of the following tasks.

                            You must ONLY output one word per task, separated by line breaks — in the same order the tasks are listed below.
                            Example Output:
                            High
                            Medium
                            Low
                            Medium

                            Rules:
                            1. **Due Date**
                            - Tasks due soon (today or within 3 days) → more likely "High"
                            - Tasks due in 4–7 days → usually "Medium"
                            - Tasks due in more than 7 days → likely "Low"

                            2. **Course Difficulty**
                            - Harder courses increase the likelihood of "High" or "Medium".
                            - Easier courses lower the likelihood of "High".

                            3. **Task Name**
                            - If the name includes words like "exam", "test", "quiz", "project", or "assignment", raise the priority.
                            - If the name includes words like "notes", "practice", "reading", or "review", lower the priority.

                            4. **Distribution Rule**
                            - On average, only 2 out of every 4 tasks (≈ 50%) should be rated "High".
                            - The rest must be "Medium" or "Low" according to importance.

                            Today's Date: {today}

                            Tasks:
                            {all_tasks_text}

                            Output one line per task (High / Medium / Low only):
                            """

                            with st.spinner("Regenerating priorities for all tasks..."):
                                try:
                                    response = model.generate_content(prompt)
                                    ai_output_lines = [
                                        line.strip() for line in response.text.splitlines()
                                        if line.strip() in ["High", "Medium", "Low"]
                                    ]

                                    for i, t in enumerate(user_data["tasks"]):
                                        # Assign the generated priority
                                        if i < len(ai_output_lines):
                                            t["priority"] = ai_output_lines[i]
                                        else:
                                            t["priority"] = "Medium"
                                        st.session_state[f"{priority_prefix}{i}"] = t["priority"]

                                except Exception as e:
                                    st.warning(f"AI failed to determine priorities: {e}")
                                    for i, t in enumerate(user_data["tasks"]):
                                        t["priority"] = "Medium"
                                        st.session_state[f"{priority_prefix}{i}"] = "Medium"

                            # Mark as no longer stale
                            st.session_state[stale_key] = False

                        # --- Display ONLY This Task’s Priority ---
                        task["priority"] = st.session_state.get(
                            f"{priority_prefix}{index}",
                            task.get("priority", "Medium")
                        )

                        color_priority = {
                            "Low": "green",
                            "Medium": "orange",
                            "High": "red",
                        }.get(task["priority"], "blue")

                        st.markdown(
                            f"""
                            <span style="
                                background-color: {color_priority};
                                color: white;
                                padding: 5px 10px;
                                border-radius: 5px;
                                font-weight: bold;
                            ">
                                {task['priority']}
                            </span>
                            """,
                            unsafe_allow_html=True,
                        )

                    else:
                        # --- Manual Mode (Independent per task) ---
                        task["priority"] = st.select_slider(
                            "Priority",
                            ["Low", "Medium", "High"],
                            value=task.get("priority", "Medium"),
                            key=f"priority_slider_{index}",
                        )

                        color_priority = {
                            "Low": "green",
                            "Medium": "orange",
                            "High": "red",
                        }.get(task["priority"], "blue")

                        st.markdown(
                            f"""
                            <span style="
                                background-color: {color_priority};
                                color: white;
                                padding: 5px 10px;
                                border-radius: 5px;
                                font-weight: bold;
                            ">
                                {task['priority']}
                            </span>
                            """,
                            unsafe_allow_html=True,
                        )

                    # Notes section
                    task["written_notes"] = st.text_area(
                        "Notes",
                        value=task.get("written_notes", ""),
                        key=f"notes_{index}",
                    )

                    
                    
                    # File Upload
                
                    # Define the quiz dialog
                    def show_quiz_dialog(ai_output, task_name):
                        @st.dialog(f"{task_name} Quiz", width="large")
                        def view_quiz():
                            st.write(ai_output)
                        view_quiz()

                    def show_ai_summary(ai_output_summary):
                        @st.dialog(f"{task['uploaded_file_name']} Summary", width="large")
                        def view_ai_summary():
                            task["uploaded_file_name"] = uploaded_file.name
                            st.write(ai_output_summary)
                        view_ai_summary()


                    # Define the uploaded file preview dialog
                    def show_uploaded_file_dialog(uploaded_file):
                        @st.dialog("Uploaded File Preview", width="large")
                        def view_uploaded_file():
                            docx_bytes = uploaded_file.getvalue()
                            doc_stream = io.BytesIO(docx_bytes)
                            document = Document(doc_stream)

                            task["uploaded_file_name"] = uploaded_file.name

                            st.subheader("Document Content:")
                            for paragraph in document.paragraphs:
                                st.write(paragraph.text)

                            if document.tables:
                                st.subheader("Tables:")
                                for table in document.tables:
                                    for row in table.rows:
                                        row_data = [cell.text for cell in row.cells]
                                        st.write(row_data)


                        view_uploaded_file()

                                            

                    
                    with st.expander("Upload Notes"):
                        col9, col10 = st.columns(2)
                        with col9:
                            uploaded_file = st.file_uploader("Upload your file", type=["docx", "txt", "pdf"], key=f"uploaded_notes_{index}")


                            # Extract text content from the file
                            def extract_text(file):
                                if file.name.endswith(".docx"):
                                    doc = Document(file)
                                    return "\n".join([p.text for p in doc.paragraphs])
                                elif file.name.endswith(".txt"):
                                    return file.read().decode("utf-8")
                                elif file.name.endswith(".pdf"):
                                    # Optional: Add PDF extraction support using PyMuPDF or pdfminer
                                    return "PDF summarization not yet implemented."
                                else:
                                    return "Unsupported file type."

                            # Handle file upload
                            if uploaded_file:
                                content = extract_text(uploaded_file)

                        
                        if uploaded_file:

                        

                            with col10:
                                task['uploaded_file_name'] = uploaded_file.name
                                st.info(f"Uploaded: {task['uploaded_file_name']}")

                                if st.button(f"Preview {task['uploaded_file_name']}", key=f"preview_{index}"):
                                    show_uploaded_file_dialog(uploaded_file)

                                if user_data['ai_document_assistant']:
                                    st.header("AI Tools")
                                
                                    def generate_quiz_button():
                                        if st.button("Generate Quiz", key=f"generate_quiz_button_{index}"):

                                            # Configure Gemini
                                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                            model = genai.GenerativeModel(
                                                model_name="gemini-2.5-flash",
                                                generation_config=genai.GenerationConfig(temperature=1.2)
                                            )

                                            prompt = f"""
                                            Your task is to output a quiz for the user based off of the notes they submit

                                            Take the name of the task, the course, the users difficulty ranking of the course and the rest of the task data into consideration.
                                            You will take all that info as well as the file uploaded as notes and generate a quiz relevant to what is in the notes, as well as some questions from other internet souces relevant to the topic


                                            INPUTS
                                            difficulty: {difficulty_ranking}
                                            courses: {courses}
                                            tasks: {tasks}
                                            file: {content}

                                            Formating requirements:
                                            Generate a 20 or so question quiz on the uploaded notes (uploaded file) and other KNOWN AND CREDIBLE SOURCES
                                            If relevant, create mulitple choice questions where the options are easily seen in the question and word questions for relevant topics
                                            Order them in easiest to hardest as the quiz goes along

                                            ONLY PROVIDE QUETSIONS THAT HAVE ACTUAL, REAL ANSWERS
                                            """

                                            with st.spinner("Generating Quiz ..."):
                                                response = model.generate_content(prompt)
                                                ai_output = response.text
                                                st.session_state["ai_quiz"] = [ai_output]
                                                st.success("Quiz Successfully Generated")

                                                # Trigger the quiz dialog
                                                show_quiz_dialog(ai_output, task["name"])

                                
                                    def summary_button():
                                        if st.button("Summarize", key=f"summarize_button_{index}"):
                                            # Configure Gemini
                                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                            model = genai.GenerativeModel(
                                                model_name="gemini-2.5-flash",
                                                generation_config=genai.GenerationConfig(temperature=1.0)
                                            )

                                            prompt = f"""

                                            You are an AI assistant designed to read and summarize documents submitted by users. Your goal is to generate a clear, concise, and informative summary of the uploaded file. Keep the summary brief, but do not omit important details or critical context.
                                            
                                            Instructions:
                                            - Read and analyze the document thoroughly.
                                            - Extract the main topics, arguments, conclusions, and any key data points or examples.
                                            - Prioritize clarity and brevity while maintaining accuracy and completeness.
                                            - Do not copy large chunks of text from the document.
                                            - Do not add external information not found in the file.
                                            
                                            Output Format:
                                            - Title (if available)
                                            - Brief overview (1-5 sentences)
                                            - Bullet-point summary of key points (5-12 items max)
                                            - Include sections/quotation of the document where the summary points were taken from
                                            - [Optional] Definitions or explanations of complex terms, if needed for clarity

                                            Example Output (for a class note or report):
                                            Title: Introduction to Quantum Mechanics
                                            Overview: This document provides a basic introduction to the fundamental concepts of quantum mechanics.
                                            Key Points:
                                            Quantum mechanics describes the behavior of particles at atomic and subatomic scales.
                                            Wave-particle duality means particles can behave like waves and vice versa.
                                            The Schrödinger equation is used to predict how quantum systems evolve.
                                            Measurement affects the system being observed (observer effect).
                                            Applications include quantum computing, cryptography, and semiconductors.
                                            
                                            Inputs:
                                            difficulty: {difficulty_ranking}
                                            courses: {courses}
                                            tasks: {tasks}
                                            file: {content}
                                            Begin your summary below:
                                            

                                            """
                                            with st.spinner("Generating Summary ..."):
                                                response = model.generate_content(prompt)
                                                ai_output_summary = response.text
                                                st.session_state["ai_summary"] = [ai_output_summary]
                                                st.success("Summary Successfully Generated")

                                                # Trigger the quiz dialog
                                                show_ai_summary(ai_output_summary)

                                    if st.session_state["current_ai_session"]:
                                        col6, col7, col8= st.columns(3)

                                        with col6:
                                            generate_quiz_button()

                                        with col7:
                                            summary_button()

                                        with col8:
                                            if st.button("Clear Chat Session"):
                                                st.session_state["current_ai_session"] = []
                                    else:
                                        col6, col7,= st.columns(2)

                                        with col6:
                                            generate_quiz_button()

                                        with col7:
                                            summary_button()



                            if user_data['ai_document_assistant']:        
                                # Configure Gemini API
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

                                # Initialize Gemini Model 
                                model = genai.GenerativeModel(
                                    model_name="gemini-2.5-flash",
                                    generation_config=genai.GenerationConfig(temperature=1.1)
                                )

                                # Load AI History Only If Enabled
                                if user_data.get("ai_use_history", False):
                                    for entry in st.session_state.get("current_ai_session", []):
                                        with st.chat_message("user"):
                                            st.markdown(entry["user_input"])
                                        with st.chat_message("assistant"):
                                            st.markdown(entry["ai_response"])

                                # AI Chat Input 
                                user_input = st.chat_input("Prompt AI Assistant")

                                # Conditionally include AI history in the prompt 
                                the_ai_history = (
                                    user_data.get("ai_history", []) if user_data.get("ai_use_history", False) else []
                                )

                                # Ai Prompt
                                prompt = f"""
                                You are a friendly, supportive, and knowledgeable AI study assistant helping students learn effectively.

                                Speak in an approachable, encouraging tone — like a helpful tutor or study buddy. Be patient, clear, and non-judgmental.

                                Your main goals:
                                - Explain complex topics in simple, easy-to-understand language
                                - Provide summaries, examples, and memory aids (like mnemonics)
                                - Ask clarifying questions when a student's request is unclear
                                - Help students build study skills, time management, and focus
                                - Support motivation and celebrate effort, not just correct answers
                                - Use analogies, real-world examples, or relatable explanations to engage students

                                Avoid overly formal or robotic language. Always prioritize learning, understanding, and encouragement.

                                Use the AI chat history for context (if applicable), as well as the course list and difficulty settings to adapt explanations.
                                You can also answer questions about the attached document.
                                And of course, respond helpfully to the user prompt.

                                Inputs:
                                difficulty: {difficulty_ranking}
                                courses: {courses}
                                tasks: {tasks}
                                ai chat history: {the_ai_history}
                                attached document: {content}
                                user input prompt: {user_input}
                                """

                                # Process User Input 
                                if user_input:
                                    with st.chat_message("user"):
                                        st.markdown(user_input)

                                    with st.spinner("Generating Response"):
                                        response = model.generate_content(prompt)
                                        ai_response = response.text

                                    with st.chat_message("assistant"):
                                        st.markdown(ai_response)

                                    # Save AI History Only If Enabled 
                                    if user_data.get("ai_use_history", False):
                                        new_entry = {
                                            "user_input": user_input,
                                            "ai_response": ai_response,
                                            "course": task['course'] if 'task' in locals() else None,
                                            "timestamp": datetime.utcnow().isoformat()
                                        }

                                        st.session_state.setdefault("current_ai_session", []).append(new_entry)
                                        user_data.setdefault("ai_history", []).append(new_entry)
                                        update_user_data(email, user_data)

                        # Warn if Document Missing and Needed 
                        elif not uploaded_file and user_data.get("ai_document_assistant", False):
                            with col9:
                                st.warning("Please Upload a File to Use AI Features")

                            

                        

                        


                    # --- Save Updates ---
                    with col3:
                        # Update Task Button
                        if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                            st.session_state[f"ai_priority_stale_{index}"] = True
                            user_data["tasks"][index] = task
                            if uploaded_file is not None:
                                if "uploaded_file" not in user_data:
                                    user_data["uploaded_file"] = []
                                user_data['uploaded_file'].append(uploaded_file)
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True
                            st.session_state["ai_data_stale_priority"] = True

                        # Mark Complete
                        if st.button(f"Mark As Complete", key=f"mark_complete_button_{index}"):
                            task["status"] = "Complete"
                            user_data["tasks"][index] = task
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True
                            st.session_state["ai_data_stale_priority"] = True


                        # Delete Task
                        if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                            if "uploaded_file_path" in task and os.path.exists(task["uploaded_file_path"]):
                                os.remove(task["uploaded_file_path"])
                            del user_data["tasks"][index]
                            update_user_data(email, user_data)
                            st.session_state["ai_data_stale"] = True
                            st.session_state["ai_data_stale_priority"] = True
                            break

                    # Move completed tasks to a separate list
                    if task["status"] == "Complete":
                        user_data.setdefault("complete_tasks", []).append(user_data["tasks"][index])
                        del user_data["tasks"][index]
                        update_user_data(email, user_data)
                        st.session_state["ai_data_stale"] = True
                        st.session_state["ai_data_stale_priority"] = True
                        break
                    
                    # Close content div
                    st.markdown("</div>", unsafe_allow_html=True)

     



    # Display the Completed Tasks
    def display_completed_tasks():
        with st.container(border=True):
            """Display completed tasks."""

            if user_data['ai_use_task_ordering'] == False:

                if len(user_data['complete_tasks']) <=17:
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
                                task["due_date"] = st.date_input("Date Completed", value=task['due_date'], key=f"completed_date_{index}").isoformat()
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
                                    st.session_state["ai_data_stale_priority"] = True                     
                                    break
                            if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                                del user_data["complete_tasks"][index]
                                update_user_data(email, user_data)
                                st.session_state["ai_data_stale"] = True
                                st.session_state["ai_data_stale_priority"] = True
                                break
                else: 
                    with st.expander("View Complete Tasks", expanded=False):
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
                                        st.session_state["ai_data_stale_priority"] = True                     
                                        break
                                if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                                    del user_data["complete_tasks"][index]
                                    update_user_data(email, user_data)
                                    st.session_state["ai_data_stale"] = True
                                    st.session_state["ai_data_stale_priority"] = True
                                    break
            else:
                if len(user_data['complete_tasks']) < 8:
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
                                task["due_date"] = st.date_input("Date Completed", value=task['due_date'], key=f"completed_date_{index}").isoformat()
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
                                    st.session_state["ai_data_stale_priority"] = True                     
                                    break
                            if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                                del user_data["complete_tasks"][index]
                                update_user_data(email, user_data)
                                st.session_state["ai_data_stale"] = True
                                st.session_state["ai_data_stale_priority"] = True
                                break
                else: 
                    with st.expander("View Complete Tasks", expanded=False):
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
                                        st.session_state["ai_data_stale_priority"] = True                     
                                        break
                                if st.button(f"Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                                    del user_data["complete_tasks"][index]
                                    update_user_data(email, user_data)
                                    st.session_state["ai_data_stale"] = True
                                    st.session_state["ai_data_stale_priority"] = True
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
            def add_new_task_dialog():
                with st.form("Adding Tasks", clear_on_submit=True):
                    new_task = {}

                    tab1, tab2, tab3 = st.tabs(["Task Details", "Additional Details", "Submit"])

                    with tab1:
                        st.header("Task Details")
                        new_task["name"] = st.text_input("Task Name:")
                        new_task["course"] = st.selectbox("Course:", user_data["courses_list"])
                        new_task["due_date"] = st.date_input("Due Date:").isoformat()

                    with tab2:
                        st.header("Additional Details")
                        new_task["status"] = st.select_slider("Status:", ["Not Started", "In-Progress", "Near Completion", "Complete"])
                        
                        # SAFELY check for AI priority setting
                        if not user_data.get("ai_use_ai_priority", False):
                            new_task["priority"] = st.select_slider("Priority:", ["Low", "Medium", "High"])

                        new_task["effort"] = st.slider("Effort Required:", min_value=1, max_value=5)



                    with tab3:
                        if st.form_submit_button("Submit"):
                            if new_task and new_task not in tasks:
                                tasks.append(new_task)
                                user_data["tasks"] = tasks
                                update_user_data(email, user_data)
                                st.session_state["ai_data_stale"] = True
                                st.session_state["ai_data_stale_priority"] = True
                                st.success(f"Added task: {new_task['name']}")
                                st.session_state.show_add_task_dialog = False
                                st.rerun()
                            elif new_task in tasks:
                                st.warning("Task already exists.")
                            else:
                                st.error("Please enter a task.")

            add_new_task_dialog()
    
    


    # Show the current tasks with AI to do list next to it if enabled
    if user_data['ai_use_task_ordering'] == True:
        
        col1, col2 = st.columns([3,1.1])

        with col1:
            # Display the list of tasks for editing
            st.subheader("Current Tasks")
            if user_data['tasks']:
                
                display_tasks()
            else:
                st.write("No Tasks Available.")

        with col2:
            with st.container(border=True):
                # Display The AI Ordered Task Completion List
                st.subheader("AI Workflow Optimizer")
                ai_to_do_list()



    # If AI to do list not enabled
    else:
        col1, col2 = st.columns([3, 0.75])
        
        with col1:
            # Display the list of tasks for editing
                st.subheader("Current Tasks")
                if user_data['tasks']:
                    
                    display_tasks()
                else:
                    st.write("No Tasks Available.")


        
        with col2: 
            with st.container(border=True):
                #Indicator of what is due today
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




    # AI to do list enabled
    if user_data['ai_use_task_ordering'] == True:
        col1, col2= st.columns([1, 2.5])



        #Indicator of what is due today
        with col1:
            with st.container(border=True):
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
                "eventClick": {
                    "callback": """
                        function(info) {
                            window.parent.postMessage({
                                isStreamlitMessage: true,
                                type: 'eventClick',
                                data: {
                                    id: info.event.id,
                                    title: info.event.title,
                                    start: info.event.startStr
                                }
                            }, '*');
                        }
                    """
                }
            }



            # Initialize events list
            events = []




            def add_events_to_calendar():
                for index, task in enumerate(user_data['tasks']):
                    color_index = user_data['courses_list'].index(task['course'])
                    color = user_data['courses_colors'][color_index]
                    due_date = str(task['due_date'])

                    events.append(
                        {
                            "id": index,  # link back to the task
                            "title": task["name"],
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
                /* === Frosted Glass Calendar Theme (Preserves Event Colors) === */

                /* Whole calendar container */
                .fc {
                    background-color: rgba(30, 30, 30, 0.25) !important;
                    backdrop-filter: blur(12px) !important;
                    border-radius: 16px !important;
                    border: 1px solid rgba(255, 255, 255, 0.25) !important;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    color: #fff !important;
                }

                /* Calendar toolbar */
                .fc-toolbar.fc-header-toolbar {
                    background-color: rgba(255, 255, 255, 0.05) !important;
                    backdrop-filter: blur(10px);
                    border-radius: 10px;
                    padding: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    
                }

                /* Title & buttons */
                .fc-toolbar-title {
                    color: #fff !important;
                    font-weight: 600;
                    font-size: 1.6rem !important;
                }
                .fc-button {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    color: white !important;
                    backdrop-filter: blur(8px);
                    border-radius: 8px !important;
                    transition: 0.3s ease-in-out;
                }
                .fc-button:hover {
                    background-color: rgba(255, 255, 255, 0.25) !important;
                }

                /* Day headers and grid */
                .fc-col-header-cell-cushion {
                    color: rgba(255, 255, 255, 0.9) !important;
                    font-weight: 500;
                }
                .fc-daygrid-day {
                    background-color: rgba(255, 255, 255, 0.03) !important;
                    border-color: rgba(255, 255, 255, 0.08) !important;
                }
                .fc-daygrid-day-number {
                    color: rgba(255, 255, 255, 0.8) !important;
                    font-weight: 400;
                }
                .fc-day-today {
                    background-color: rgba(255, 255, 255, 0.07) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    border-radius: 8px !important;
                }

                /* Events: preserve color, add blur via pseudo element */
                .fc-event {
                    position: relative;
                    border: none !important;
                    border-radius: 8px !important;
                    color: #fff !important;
                    font-weight: 500;
                    overflow: hidden;
                    transition: 0.2s ease-in-out;
                }
                .fc-event::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    backdrop-filter: blur(6px);
                    opacity: 0.3; /* controls the glassiness over color */
                    z-index: 0;
                }
                .fc-event > * {
                    position: relative;
                    z-index: 1;
                }
                .fc-event:hover {
                    transform: scale(1.02);
                    opacity: 0.9;
                }

                /* Past events */
                .fc-event-past {
                    opacity: 0.6 !important;
                }

                /* Event text */
                .fc-event-title {
                    font-weight: 600;
                }
                .fc-event-time {
                    font-style: italic;
                }

                /* Popover for events */
                .fc-popover {
                    background-color: rgba(30, 30, 30, 0.4) !important;
                    backdrop-filter: blur(10px);
                    color: #fff !important;
                    border-radius: 10px !important;
                    border: 1px solid rgba(255, 255, 255, 0.25) !important;
                }

                /* Scrollbar styling */
                ::-webkit-scrollbar {
                    width: 6px;
                }
                ::-webkit-scrollbar-thumb {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                }
                """,
                key='calendar_ai_to_do_on',
            )
            
            

            import socket
            try:
                print(socket.gethostbyname('<your-supabase-ref>.supabase.co'))
            except Exception as e:
                print(f"DNS resolution failed: {e}")
    


    # AI Task ordering off
    else:
        col1, col2= st.columns([1, 2.5])
        
        with col1:
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
                "eventClick": {
                    "callback": """
                        function(info) {
                            window.parent.postMessage({
                                isStreamlitMessage: true,
                                type: 'eventClick',
                                data: {
                                    id: info.event.id,
                                    title: info.event.title,
                                    start: info.event.startStr
                                }
                            }, '*');
                        }
                    """
                }
            }



            # Initialize events list
            events = []




            def add_events_to_calendar():
                for index, task in enumerate(user_data['tasks']):
                    color_index = user_data['courses_list'].index(task['course'])
                    color = user_data['courses_colors'][color_index]
                    due_date = str(task['due_date'])

                    events.append(
                        {
                            "id": index,  # link back to the task
                            "title": task["name"],
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
                /* === Frosted Glass Calendar Theme (Preserves Event Colors) === */

                /* Whole calendar container */
                .fc {
                    background-color: rgba(30, 30, 30, 0.25) !important;
                    backdrop-filter: blur(12px) !important;
                    border-radius: 16px !important;
                    border: 1px solid rgba(255, 255, 255, 0.25) !important;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    color: #fff !important;
                }

                /* Calendar toolbar */
                .fc-toolbar.fc-header-toolbar {
                    background-color: rgba(255, 255, 255, 0.05) !important;
                    backdrop-filter: blur(10px);
                    border-radius: 10px;
                    padding: 8px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    
                }

                /* Title & buttons */
                .fc-toolbar-title {
                    color: #fff !important;
                    font-weight: 600;
                    font-size: 1.6rem !important;
                }
                .fc-button {
                    background-color: rgba(255, 255, 255, 0.08) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    color: white !important;
                    backdrop-filter: blur(8px);
                    border-radius: 8px !important;
                    transition: 0.3s ease-in-out;
                }
                .fc-button:hover {
                    background-color: rgba(255, 255, 255, 0.25) !important;
                }

                /* Day headers and grid */
                .fc-col-header-cell-cushion {
                    color: rgba(255, 255, 255, 0.9) !important;
                    font-weight: 500;
                }
                .fc-daygrid-day {
                    background-color: rgba(255, 255, 255, 0.03) !important;
                    border-color: rgba(255, 255, 255, 0.08) !important;
                }
                .fc-daygrid-day-number {
                    color: rgba(255, 255, 255, 0.8) !important;
                    font-weight: 400;
                }
                .fc-day-today {
                    background-color: rgba(255, 255, 255, 0.07) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    border-radius: 8px !important;
                }

                /* Events: preserve color, add blur via pseudo element */
                .fc-event {
                    position: relative;
                    border: none !important;
                    border-radius: 8px !important;
                    color: #fff !important;
                    font-weight: 500;
                    overflow: hidden;
                    transition: 0.2s ease-in-out;
                }
                .fc-event::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    backdrop-filter: blur(6px);
                    opacity: 0.3; /* controls the glassiness over color */
                    z-index: 0;
                }
                .fc-event > * {
                    position: relative;
                    z-index: 1;
                }
                .fc-event:hover {
                    transform: scale(1.02);
                    opacity: 0.9;
                }

                /* Past events */
                .fc-event-past {
                    opacity: 0.6 !important;
                }

                /* Event text */
                .fc-event-title {
                    font-weight: 600;
                }
                .fc-event-time {
                    font-style: italic;
                }

                /* Popover for events */
                .fc-popover {
                    background-color: rgba(30, 30, 30, 0.4) !important;
                    backdrop-filter: blur(10px);
                    color: #fff !important;
                    border-radius: 10px !important;
                    border: 1px solid rgba(255, 255, 255, 0.25) !important;
                }

                /* Scrollbar styling */
                ::-webkit-scrollbar {
                    width: 6px;
                }
                ::-webkit-scrollbar-thumb {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 3px;
                }
                """,
                key='calendar_ai_to_do_off',
            )
            
            

            import socket
            try:
                print(socket.gethostbyname('<your-supabase-ref>.supabase.co'))
            except Exception as e:
                print(f"DNS resolution failed: {e}")









home_page(st.session_state['username'])
