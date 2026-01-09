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
import json


# Initialize Supabase Client
url = st.secrets['connections']['SUPABASE_URL']
key = st.secrets['connections']['SUPABASE_KEY']
supabase: Client = create_client(url, key)


def background():
    page_element = """
    <style>

    /*******************************************************
     FULLY TRANSPARENT STREAMLIT HEADER – SAFE VERSION
    *******************************************************/

    /* Outer header container */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0) !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
    }

    /* Inner toolbar block */
    header[data-testid="stHeader"] > div:first-child {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }

    /* Streamlit’s banner subcontainer */
    header[data-testid="stHeader"] div[role="banner"] {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }

    /* All nested elements must not re-apply tint */
    header[data-testid="stHeader"] * {
        background: transparent !important;
    }


    /*******************************************************
     NORMAL BACKGROUND BEHIND ENTIRE APP
    *******************************************************/
    [data-testid="stApp"] {
        background-image: url("https://cdn.wallpapersafari.com/58/75/Ut1h5g.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
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
    background-color: rgba(255, 255, 255, 0.08) !important;
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

/* --- Inputs / Textareas / Selects (EXCEPT Color Picker) --- */
input:not([type="color"]), select, textarea {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 6px;
}

/* --- Restore Color Picker --- */
input[type="color"] {
    background: none !important;
    border: none !important;
    padding: 0 !important;
    height: 2.5rem !important;
    width: 3rem !important;
}

input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 0 !important;
}

input[type="color"]::-webkit-color-swatch {
    border-radius: 8px !important;
    border: 2px solid rgba(255, 255, 255, 0.6) !important;
}

input[type="color"]::-moz-color-swatch {
    border-radius: 8px !important;
    border: 2px solid rgba(255, 255, 255, 0.6) !important;
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

/* Let Color Picker content show properly */
div[data-baseweb="popover"] [data-baseweb="color-picker"] * {
    background: initial !important;
    color: initial !important;
}

/* --- Top Header / Nav Bar --- */
header[data-testid="stHeader"] {
    background-color: rgba(30, 30, 30, 0.4) !important;
    backdrop-filter: blur(10px);
    border-bottom: none !important;
    box-shadow: none !important;
}

/* Keep icons and text visible */
header[data-testid="stHeader"] * {
    color: white !important;
}

/* --- Buttons in the top bar --- */
header[data-testid="stHeader"] button {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    backdrop-filter: blur(6px);
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: bold;
    transition: 0.3s ease-in-out;
}

/* Hover effect for buttons */
header[data-testid="stHeader"] button:hover {
    background-color: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
}

/* Optional: make main content match frosted theme */
.main .block-container {
    background-color: rgba(30, 30, 30, 0.3) !important;
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

/* Transparent container with borders and frosted glass */
.task-container {
    background-color: rgba(0, 0, 0, 0) !important;
    color: white !important;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    padding: 15px;
    margin-top: 5px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
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

div.streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
}

/* Remove Streamlit default shadows */
div[data-testid="stExpander"] {
    box-shadow: none !important;
}

/* --- Custom Frosted Expanders --- */
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
            


input[type="color"] {
    background: white !important;
    border-radius: 10px;
    padding: 2px;
}


.frosted-expander-content.show {
    max-height: 1000px;
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
            "ai_use_task_ordering": False,
            "ai_use_ai_priority": False,
            "ai_document_assistant": False,
            "ai_use_history": False,
            "ai_quiz_length": ["Short"],
            "ai_summary_length": ["Short"],
            "ai_assistant_response_length": ["Medium"],
            


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


def settings_page(email):
    st.title("Settings")

     # Fetch user data
    user_data = get_user_data(email)

    # Get the data from database to edit within application
    courses = user_data.get("courses_list", [])
    colors = user_data.get("courses_colors", [])
    difficulty_ranking = user_data.get("difficulty_ranking", [])
    tasks = user_data.get("tasks", [])
    completed_tasks = user_data.get("complete_tasks", [])


    st.header("Courses List")


    # Progress Bar
    progress_text = "Completion of Course Selection"
    course_progress_bar = st.progress(0, text=progress_text)

    # Button to add the course to the list
    if st.button("Add Course"):
        @st.dialog("Add Course")
        def add_course():
            col1, col2 = st.columns(2)

            with col2:
                # Input to select a color for calendar
                course_color = st.color_picker("Select Course Color", key=f"color_{st.session_state['username']}")

            with col1:
                # Input for new course
                course_to_add = st.text_input("Type Course Here")



            if st.button("Add Course", key="Inside_st.dialog"):  # Check if the input is not empty
                user_data["courses_list"].append(course_to_add)
                user_data["courses_colors"].append(course_color)
                update_user_data(email, user_data)
        add_course()

    # Difficulty of courses for AI reference
    if len(user_data["courses_list"]) >= 3:
        if "difficulty_ranking_list" not in st.session_state:
            st.session_state['difficulty_ranking'] = []
        
        st.session_state['difficulty_ranking'] = st.multiselect(
            "Rank courses in terms of difficulty (from hardest to easiest):",user_data["courses_list"]
        )
        if st.session_state['difficulty_ranking']:
            user_data['difficulty_ranking'] = st.session_state['difficulty_ranking'] 
        update_user_data(email, user_data)
        
        # Displays of Properties
        col1, col2, = st.columns(2)

        with col1:
            # Display the list of courses
            st.write("Courses List:")
            for i, course in enumerate(user_data["courses_list"]):
                st.write(f"{i + 1}. {course}")

        # with col2:
        #     # Display the colors list
        #     st.write("Colors List:")
        #     for i, color in enumerate(user_data["courses_colors"]):
        #         st.write(f"{color}")

        if user_data["difficulty_ranking"] != "[]" :
            with col2:
                # Display the difficulty order
                st.write("Difficulty Ranking:")
                for i, course in enumerate(user_data["difficulty_ranking"]):
                    st.write(f"{i + 1}. {course}")

    else:
        # col1, col2 = st.columns(2)

        # with col1:
            # Display the list of courses
            st.write("Courses List:")
            for i, course in enumerate(user_data["courses_list"]):
                st.write(f"{i + 1}. {course}")

        # with col2:
        #     # Display the colors list
        #     st.write("Colors List:")
        #     for i, color in enumerate(user_data["courses_colors"]):
        #         st.write(f"{color}")

    # Option to reset courses list
    st.header("Edit Course List")

    with st.expander("Edit Course List", expanded=False):
        with st.form("Editing Courses List"):
            tab1, tab2, tab3 = st.tabs(["Edit List", "Remove Course From List", "Reset List"])

            # Edit Tab
            with tab1:
                # Select course to edit
                course_to_edit = st.selectbox("Select a Course to Edit", user_data["courses_list"])

                col1, col2 = st.columns(2)

                with col1:
                    # Input what is to replace it
                    replacement_course = st.text_input("Please Input New Course")
                with col2:
                    replacement_course_color = st.color_picker("Select Replacement Course Color")

                submitted_edited_list = st.form_submit_button("Submit Replacement Course")

            # Remove Tab
            with tab2:
                # Select a Course to remove from list
                course_to_remove = st.selectbox("Select a Course to Remove", user_data["courses_list"])

                # Button to remove course
                st.write(f"Pressing the button below will remove {course_to_remove} from the Courses List")
                submitted_remove_course_from_list = st.form_submit_button(f"Remove {course_to_remove} from Courses List")

            # Reset Tab
            with tab3:
                st.write("Pressing the button below will reset the entire course list")
                submitted_reset_list = st.form_submit_button("Reset Course List")

    # What happens when the buttons are pressed
    if submitted_edited_list:
        index_course_replace = user_data["courses_list"].index(course_to_edit)  # Get index of course to be replaced
        user_data["courses_list"][index_course_replace] = replacement_course  # Replace course
        user_data["courses_colors"][index_course_replace] = replacement_course_color  # Replace color
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    if submitted_remove_course_from_list:
        index_course_remove = user_data["courses_list"].index(course_to_remove)  # Get index of course to be removed
        user_data["courses_list"].remove(course_to_remove)
        user_data["courses_colors"].remove(user_data["courses_colors"][index_course_remove])
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    if submitted_reset_list:
        user_data["courses_list"].clear()
        user_data["courses_colors"].clear()
        user_data["difficulty_ranking"].clear()
        update_user_data(email, user_data)

    # Controlling Progress Bar
    if len(user_data["courses_list"]) == 0:
        course_progress_bar.progress(0, text=progress_text)
    elif len(user_data["courses_list"]) == 1:
        course_progress_bar.progress(12)
    elif len(user_data["courses_list"]) == 2:
        course_progress_bar.progress(25)
    elif len(user_data["courses_list"]) == 3:
        course_progress_bar.progress(37)
    elif len(user_data["courses_list"]) == 4:
        course_progress_bar.progress(50)

    if len(user_data["difficulty_ranking"]) == 1:
        course_progress_bar.progress(62)
    elif len(user_data["difficulty_ranking"]) == 2:
        course_progress_bar.progress(75)
    elif len(user_data["difficulty_ranking"]) == 3:
        course_progress_bar.progress(87)

    if len(user_data["difficulty_ranking"]) >= 3:
        course_progress_bar.progress(100, text="Course Setup Complete!")




    if len(user_data["difficulty_ranking"]) >= 3:


        st.header("AI Tools")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ai_task_ordering = st.checkbox(
            "Enable AI Task Ordering",
            value=user_data.get("ai_use_task_ordering", False)
        )

            if ai_task_ordering != user_data.get("ai_use_task_ordering", False):
                user_data["ai_use_task_ordering"] = ai_task_ordering
                update_user_data(email, user_data)

            st.info("""
                After enabling this option, the AI Assistant will take into consideration your task information and course difficulty settings to provide a list of your tasks in the order of which it recommends you complete them to be as time efficient as possible.       
            """)
        with col2:
            ai_priority = st.checkbox(
            "Enable AI Task Priority",
            value=user_data.get("ai_use_ai_priority", False)
        )
            if ai_priority != user_data.get("ai_use_ai_priority", False):
                user_data["ai_use_ai_priority"] = ai_priority
                update_user_data(email, user_data)
            st.info("""
                After enabling this option, the AI Assistant will take into consideration your task information and course difficulty settings to provide an automatic priority rating for your tasks.   
            """)
            
        with col3:
            doc_assistant = st.checkbox(
                "Enable AI Document Assistant",
                value=user_data.get("ai_document_assistant", False)
            )
            if doc_assistant != user_data.get("ai_document_assistant", False):
                user_data["ai_document_assistant"] = doc_assistant
                update_user_data(email, user_data)
            
            st.info("""
                After enabling this option, the AI Assistant will now have a place in your tasks menu for each task. This will allow you to use it to summarize imported document, ask questions about it, or simply just chat with it.
            """)
        with col4:
            ai_toggle_history = st.checkbox(
                "Enable AI History",
                value = user_data.get("ai_use_history", False)
            )
            if ai_toggle_history != user_data.get("ai_use_history", False):
                user_data["ai_use_history"] = ai_toggle_history
                update_user_data(email, user_data)
            
            st.info("""
                After enabling this option, the AI Assitant will remember all your interactions with it and be able to recall past discussions and use them to help with discussing new topics.
            """)
        
        if doc_assistant == True:
            col1a, col2a, col3a = st.columns(3)

            with col1a:

                ai_quiz_length = st.select_slider(
                "Set AI Quiz Length",
                ["Short", "Medium", "Long", "Complete Review"], 
                value = user_data.get("ai_quiz_length"),
                )
                if ai_quiz_length != user_data.get("ai_quiz_length", "Short"):
                    user_data["ai_quiz_length"] = ai_quiz_length
                    update_user_data(email, user_data)
                
                st.info("""
                    This toggle sets the length of the AI generated quizes:
                        Short: - 1 to 5 questions (Multiple Choice)    
                        Medium: - 1 to 10 questions                
                        Long: - 1 to 20 questions                    
                        (2/3 Multiple Choice, 1/3 Short Answer)    
                        Complete Review: - 1 to 25 questions             
                        (1/2 Multiple Choice, 1/2 Short Answer)
                """)
            
            with col2a:
                ai_summary_length = st.select_slider(
                "Set AI Summary Length",
                ["Short", "Complete Answers", "Comprehensive Answers"], 
                value = user_data.get("ai_summary_length"),
                )
                if ai_summary_length != user_data.get("ai_summary_length", "Short"):
                    user_data["ai_summary_length"] = ai_summary_length
                    update_user_data(email, user_data)
                    
                st.info("""
                    This toggle sets the length of the AI generated summaries. The options are self-explanatory, how long you expect it to be will be how long it is.
                        
                """)

            with col3a:
                ai_assistant_response_length = st.select_slider(
                "Set AI Assistant Response Length",
                ["Concise", "Short", "Medium", "Comprehensive"], 
                value = user_data.get("ai_assistant_response_length"),
                )
                if ai_assistant_response_length != user_data.get("ai_assistant_response_length", "Medium"):
                    user_data["ai_assistant_response_length"] = ai_assistant_response_length
                    update_user_data(email, user_data)
                
                st.info("""
                    This toggle sets the length of the AI Assistant Responses. The options are self-explanatory, how long you expect it to be will be how long it is.
                        
                """)



settings_page(st.session_state['username'])