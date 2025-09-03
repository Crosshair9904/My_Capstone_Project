import streamlit as st
from datetime import datetime, timedelta


#Background
def background():
    page_element="""
    <style>
    [data-testid="stAppViewContainer"]{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    [data-testid="stHeader"]{
    background-color: rgba(0,0,0,0);
    }
    [data-testid="stSidebar"]> div:first-child{
    background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
    background-size: cover;
    }
    </style>


    """

    st.markdown(page_element, unsafe_allow_html=True)
background()

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
            # "today_tasks": [],
            # "this_week_tasks": [],
        }

    return st.session_state["user_sessions"][username]


def settings_page():
    st.title("Settings")

    # Get the logged-in user's session state
    user_session = get_user_session(st.session_state["username"])

    st.header("Courses List")

    with st.expander("Course List", expanded=False):
        # Progress Bar
        progress_text = "Completion of Course Selection"
        course_progress_bar = st.progress(0, text=progress_text)

        col1, col2 = st.columns(2)

        with col2:
            # Input to select a color for calendar
            course_color = st.color_picker("Select Course Color", key=f"color_{st.session_state['username']}")

        with col1:
            # Input for new course
            course_to_add = st.text_input("Type Course Here")

            # Button to add the course to the list
            if st.button("Add Course"):
                if course_to_add:  # Check if the input is not empty
                    user_session["courses_list"].append(course_to_add)
                    user_session["courses_colors"].append(course_color)

        # Difficulty of courses for AI reference
        if len(user_session["courses_colors"]) >= 3:
            user_session["difficulty_ranking"] = st.multiselect(
                "Rank courses in terms of difficulty (from hardest to easiest):",
                user_session["courses_list"],
            )

            # Displays of Properties
            col1, col2, col3 = st.columns(3)

            with col1:
                # Display the list of courses
                st.write("Courses List:")
                for i, course in enumerate(user_session["courses_list"]):
                    st.write(f"{i + 1}. {course}")

            with col2:
                # Display the colors list
                st.write("Colors List:")
                for i, color in enumerate(user_session["courses_colors"]):
                    st.write(f"{color}")

            with col3:
                # Display the difficulty order
                st.write("Difficulty Ranking:")
                for i, course in enumerate(user_session["difficulty_ranking"]):
                    st.write(f"{i + 1}. {course}")

        else:
            col1, col2 = st.columns(2)

            with col1:
                # Display the list of courses
                st.write("Courses List:")
                for i, course in enumerate(user_session["courses_list"]):
                    st.write(f"{i + 1}. {course}")

            with col2:
                # Display the colors list
                st.write("Colors List:")
                for i, color in enumerate(user_session["courses_colors"]):
                    st.write(f"{color}")

        # Option to reset courses list
        st.header("Edit Course List")

        with st.expander("Edit Course List", expanded=False):
            with st.form("Editing Courses List"):
                tab1, tab2, tab3 = st.tabs(["Edit List", "Remove Course From List", "Reset List"])

                # Edit Tab
                with tab1:
                    # Select course to edit
                    course_to_edit = st.selectbox("Select a Course to Edit", user_session["courses_list"])

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
                    course_to_remove = st.selectbox("Select a Course to Remove", user_session["courses_list"])

                    # Button to remove course
                    st.write(f"Pressing the button below will remove {course_to_remove} from the Courses List")
                    submitted_remove_course_from_list = st.form_submit_button(f"Remove {course_to_remove} from Courses List")

                # Reset Tab
                with tab3:
                    st.write("Pressing the button below will reset the entire course list")
                    submitted_reset_list = st.form_submit_button("Reset Course List")

        # What happens when the buttons are pressed
        if submitted_edited_list:
            index_course_replace = user_session["courses_list"].index(course_to_edit)  # Get index of course to be replaced
            user_session["courses_list"][index_course_replace] = replacement_course  # Replace course
            user_session["courses_colors"][index_course_replace] = replacement_course_color  # Replace color
            user_session["difficulty_ranking"].clear()

        if submitted_remove_course_from_list:
            index_course_remove = user_session["courses_list"].index(course_to_remove)  # Get index of course to be removed
            user_session["courses_list"].remove(course_to_remove)
            user_session["courses_colors"].remove(user_session["courses_colors"][index_course_remove])
            user_session["difficulty_ranking"].clear()

        if submitted_reset_list:
            user_session["courses_list"].clear()
            user_session["courses_colors"].clear()
            user_session["difficulty_ranking"].clear()

        # Controlling Progress Bar
        if len(user_session["courses_list"]) == 0:
            course_progress_bar.progress(0, text=progress_text)
        elif len(user_session["courses_list"]) == 1:
            course_progress_bar.progress(12)
        elif len(user_session["courses_list"]) == 2:
            course_progress_bar.progress(25)
        elif len(user_session["courses_list"]) == 3:
            course_progress_bar.progress(37)
        elif len(user_session["courses_list"]) == 4:
            course_progress_bar.progress(50)

        if len(user_session["difficulty_ranking"]) == 1:
            course_progress_bar.progress(62)
        elif len(user_session["difficulty_ranking"]) == 2:
            course_progress_bar.progress(75)
        elif len(user_session["difficulty_ranking"]) == 3:
            course_progress_bar.progress(87)

        if len(user_session["difficulty_ranking"]) >= 3:
            course_progress_bar.progress(100, text="Course Setup Complete!")

settings_page()