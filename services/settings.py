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
            "selected_course_group": [],
            "course_groups": [],
            


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

# The Actual Settings Page
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
    course_groups = user_data.get("course_groups", [])


    st.header("Courses List")


    # Progress Bar
    progress_text = "Completion of Course Selection"
    course_progress_bar = st.progress(0, text=progress_text)


    course_groups = user_data.get("course_groups", [])

    group_name_to_group = {
        (group.get("name") or f"Group {i + 1}"): group
        for i, group in enumerate(course_groups)
    }

    if not group_name_to_group:
        st.info("Create a course group first.")
        return
    
    if "selected_course_group" not in st.session_state:
        st.session_state.selected_course_group = user_data.get("selected_course_group")
    
    if (
    st.session_state.selected_course_group not in group_name_to_group
):
        st.session_state.selected_course_group = next(iter(group_name_to_group))
    
    if st.button("Create Course Group"):
        @st.dialog("Create Course Group")
        def add_course_group():
            with st.form("Adding Course Group", clear_on_submit=True):
                new_group = {}

                new_group['name'] = st.text_input("Course Group Name:")
                new_group['courses_list'] = []
                new_group['courses_colors'] =[]
                new_group['completed_tasks'] = []
                new_group['tasks'] = []

                if st.form_submit_button("Submit New Group"):
                    if new_group and new_group not in course_groups:
                        course_groups.append(new_group)
                        user_data['course_groups'] = course_groups
                        update_user_data(email, user_data)
                        st.success(f"Added Course Group: {new_group['name']}")
                        st.rerun()
                    elif new_group in course_groups:
                        st.warning("Course Group already exists.")
                    else:
                        st.error("Please enter a Course Group.")
            

        add_course_group()


    course_group_select = st.segmented_control(
    "Select Course Group",
    options=list(group_name_to_group.keys()),
    default=user_data['selected_course_group'],
    key="course_group_segmented_control",
    selection_mode="single",

)
    if (
    course_group_select
    and course_group_select != st.session_state.selected_course_group
):
        st.session_state.selected_course_group = course_group_select
        user_data["selected_course_group"] = course_group_select
        update_user_data(email, user_data) 


    selected_group = group_name_to_group[st.session_state.selected_course_group] 


    


       



    if course_groups:
        st.subheader(selected_group['name'])
        @st.dialog("Add Course")
        def add_course_dialog(selected_group, user_data, email):
            col1, col2 = st.columns(2)

            with col1:
                course_to_add = st.text_input("Type Course Name Here")

            with col2:
                course_color = st.color_picker(
                    "Select Course Color",
                    key=f"color_{st.session_state['username']}"
                )

            if st.button("Add Course", key="confirm_add_course"):
                # Normalize structure
                if not isinstance(selected_group.get("courses_list"), list):
                    selected_group["courses_list"] = []

                if not isinstance(selected_group.get("courses_colors"), list):
                    selected_group["courses_colors"] = []

                selected_group["courses_list"].append(course_to_add)
                selected_group["courses_colors"].append(course_color)

                update_user_data(email, user_data)
                st.success("Course added")
                st.rerun()

        if st.button("Add Course"):
            add_course_dialog(selected_group, user_data, email)

    # Difficulty of courses for AI reference
        if len(selected_group["courses_list"]) >= 3:
            if "difficulty_ranking_list" not in st.session_state:
                st.session_state['difficulty_ranking'] = []
            
            st.session_state['difficulty_ranking'] = st.multiselect(
                "Rank courses in terms of difficulty (from hardest to easiest):",selected_group["courses_list"]
            )
            if st.session_state['difficulty_ranking']:
                user_data['difficulty_ranking'] = st.session_state['difficulty_ranking'] 
            update_user_data(email, user_data)
            
            # Displays of Properties
            col1, col2, = st.columns(2)

            with col1:
                # Display the list of courses
                st.write("Courses List:")
                for i, course in enumerate(selected_group["courses_list"]):
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
                for i, course in enumerate(selected_group["courses_list"]):
                    st.write(f"{i + 1}. {course}")

        # with col2:
        #     # Display the colors list
        #     st.write("Colors List:")
        #     for i, color in enumerate(user_data["courses_colors"]):
        #         st.write(f"{color}")

        # Option to reset courses list

        st.header("Edit Course Groups")

        with st.expander("Edit Course Groups", expanded=False):
            with st.form("Editing Course Groups"):
                tab1, tab2 = st.tabs(["Edit Course Group", "Delete Course Group"])

                # Edit Course Group Tab
                with tab1:
                    group_to_edit = st.selectbox("Select Group to Edit", group_name_to_group.keys())

                    new_group_name = st.text_input("Please Enter The New Name of The Group")
                    submitted_edited_group_list = st.form_submit_button("Submit Replacement Course Group")

                # Delete Course Group Tab
                with tab2:
                    group_to_delete = st.selectbox("Please Select the Course Group to be Deleted", group_name_to_group.keys())
                    st.warning("This will permanently delete the course group including all courses, tasks and completed tasks associated with the course group")
                    submitted_group_to_delete = st.form_submit_button("Submit Course Group to Delete")

        
        # EDIT COURSE GROUP NAME
        if submitted_edited_group_list and new_group_name.strip():

            for group in user_data["course_groups"]:
                if group.get("name") == group_to_edit:
                    group["name"] = new_group_name.strip()
                    break

            # Update selected group name if it was renamed
            if user_data.get("selected_course_group") == group_to_edit:
                user_data["selected_course_group"] = new_group_name.strip()
                st.session_state.selected_course_group = new_group_name.strip()

            update_user_data(email, user_data)
            st.success("Course group renamed successfully")
            st.rerun()


        # DELETE COURSE GROUP
        if submitted_group_to_delete:

            user_data["course_groups"] = [
                g for g in user_data["course_groups"]
                if g.get("name") != group_to_delete
            ]

            # Handle selected group deletion safely
            remaining_groups = user_data["course_groups"]

            if not remaining_groups:
                user_data["selected_course_group"] = None
                st.session_state.selected_course_group = None
            else:
                new_selected = remaining_groups[0]["name"]
                user_data["selected_course_group"] = new_selected
                st.session_state.selected_course_group = new_selected

            update_user_data(email, user_data)
            st.success("Course group deleted successfully")
            st.rerun()




        st.header("Edit Course List")

        with st.expander("Edit Course List", expanded=False):
            with st.form("Editing Courses List"):
                tab1, tab2, tab3 = st.tabs(["Edit List", "Remove Course From List", "Reset List"])

                # Edit Tab
                with tab1:
                    # Select course to edit
                    course_to_edit = st.selectbox("Select a Course to Edit", selected_group["courses_list"])

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
                    course_to_remove = st.selectbox("Select a Course to Remove", selected_group["courses_list"])

                    # Button to remove course
                    st.write(f"Pressing the button below will remove {course_to_remove} from the Courses List")
                    submitted_remove_course_from_list = st.form_submit_button(f"Remove {course_to_remove} from Courses List")

                # Reset Tab
                with tab3:
                    st.write("Pressing the button below will reset the entire course list")
                    submitted_reset_list = st.form_submit_button("Reset Course List")

        # What happens when the buttons are pressed
        if submitted_edited_list:
            index_course_replace = selected_group["courses_list"].index(course_to_edit)  # Get index of course to be replaced
            selected_group["courses_list"][index_course_replace] = replacement_course  # Replace course
            selected_group["courses_colors"][index_course_replace] = replacement_course_color  # Replace color
            user_data["difficulty_ranking"].clear()
            update_user_data(email, user_data)

        if submitted_remove_course_from_list:
            index_course_remove = selected_group["courses_list"].index(course_to_remove)  # Get index of course to be removed
            selected_group["courses_list"].remove(course_to_remove)
            selected_group["courses_colors"].remove(selected_group["courses_colors"][index_course_remove])
            user_data["difficulty_ranking"].clear()
            update_user_data(email, user_data)

        if submitted_reset_list:
            selected_group["courses_list"].clear()
            selected_group["courses_colors"].clear()
            user_data["difficulty_ranking"].clear()
            update_user_data(email, user_data)

        # Controlling Progress Bar
        if len(selected_group["courses_list"]) == 0:
            course_progress_bar.progress(0, text=progress_text)
        elif len(selected_group["courses_list"]) == 1:
            course_progress_bar.progress(12)
        elif len(selected_group["courses_list"]) == 2:
            course_progress_bar.progress(25)
        elif len(selected_group["courses_list"]) == 3:
            course_progress_bar.progress(37)
        elif len(selected_group["courses_list"]) == 4:
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

        # All AI Tool Settings
        st.header("AI Tools")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ai_task_ordering = st.toggle(
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
            ai_priority = st.toggle(
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
            doc_assistant = st.toggle(
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
            ai_toggle_history = st.toggle(
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