import streamlit as st


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

st.title("Settings")


st.header("Courses List")
# Initialize the session state for courses_list if it doesn't exist
if 'courses_list' not in st.session_state:
    st.session_state.courses_list = []

if 'courses_colors' not in st.session_state:
    st.session_state.courses_colors = []

if 'difficulty_ranking' not in st.session_state:
    st.session_state.difficulty_ranking = []

with st.expander("Course List", expanded=False):

    # Progress Bar
    progress_text = "Completition of Course Selection"
    course_progress_bar = st.progress(0, text=progress_text)


    col1, col2 = st.columns(2)

    with col2:
        # Input to select a color for calendar
        course_color = st.color_picker("Select Course Color")
    
    with col1:
        # Input for new course
        course_to_add = st.text_input("Type Course Here")

        # Button to add the course to the list
        if st.button("Add Course"):
            if course_to_add:  # Check if the input is not empty
                st.session_state.courses_list.append(course_to_add)
                st.session_state.courses_colors.append(course_color)

    # Difficulty of courses for Ai reference
    if len(st.session_state.courses_colors) >= 3:
        st.session_state.difficulty_ranking = st.multiselect(
        "Rank courses in terms of difficulty (from hardest to easiest):",
        st.session_state.courses_list,
        )

        # Diplays of Properties

        col1, col2, col3 = st.columns(3)

        with col1:
            # Display the list of courses
            st.write("Courses List:")
            for i, course in enumerate(st.session_state.courses_list):
                st.write(f"{i + 1}. {course}")

        with col2:
            # Display the colors list
            st.write("Colors List:")
            for i, color in enumerate(st.session_state.courses_colors):
                st.write(f"{color}")

        with col3:
            # Display the difficulty order
            st.write("Difficulty Ranking:")
            for i, course in enumerate(st.session_state.difficulty_ranking):
                st.write(f"{i + 1}. {course}")
    
    else:

        col1, col2 = st.columns(2)

        with col1:
            # Display the list of courses
            st.write("Courses List:")
            for i, course in enumerate(st.session_state.courses_list):
                st.write(f"{i + 1}. {course}")

        with col2:
            # Display the colors list
            st.write("Colors List:")
            for i, color in enumerate(st.session_state.courses_colors):
                st.write(f"{color}")

    # option to reset courses list
    st.header("Edit Course List")

    with st.expander("Edit Course List", expanded=False):
        with st.form("Editing Courses List"):
            tab1, tab2, tab3,= st.tabs(["Edit List", "Remove Course From List", "Reset List"]) 

            # Edit Tab
            with tab1:
                # select course to edit
                course_to_edit = st.selectbox("Select a Course to Edit",st.session_state.courses_list)
                
                col1, col2 = st.columns(2)

                with col1:
                    # input what is to replace it
                    replacement_course = st.text_input("Please Input New Course")
                with col2:
                    replacement_course_color = st.color_picker("Select Replacement Course Color")


                submitted_edited_list = st.form_submit_button("Submit Replacement Course")
            
            # Remove Tab
            with tab2:
                # Select a Course to remove from list
                course_to_remove =st.selectbox("Select a Course to Remove", st.session_state.courses_list)

                # Button to remove course
                st.write(f"Pressing the button below will remove", str(course_to_remove), "from the Courses List")
                submitted_remove_course_from_list = st.form_submit_button("Remove  " + str(course_to_remove) + "  from Courses List")


            # Reset Tab
            with tab3:
                st.write("Pressing the button below will reset the entire course list")
                submitted_reset_list = st.form_submit_button("Reset Course List")
        
    # What happens when the buttons are pressed

    #edit list
    if submitted_edited_list:
        index_course_replace = st.session_state.courses_list.index(course_to_edit) #get index of course to be replaced
        st.session_state.courses_list[index_course_replace] = replacement_course #places replacement course in position of the one to be replaced
        st.session_state.courses_colors[index_course_replace] = replacement_course_color #places replacement color in position of the one to be replaced
        st.session_state.difficulty_ranking.clear()

    if submitted_remove_course_from_list:
        index_course_remove = st.session_state.courses_list.index(course_to_remove) #get index of course to be removed
        st.session_state.courses_list.remove(course_to_remove)
        st.session_state.courses_colors.remove(st.session_state.courses_colors[index_course_remove])
        st.session_state.difficulty_ranking.clear()

    #reset list
    if submitted_reset_list:
        st.session_state.courses_list.clear()
        st.session_state.courses_colors.clear()
        st.session_state.difficulty_ranking.clear()

# Controlling Progress Bar
if len(st.session_state.courses_list) == 0:
    course_progress_bar.progress(0, text=progress_text)
if len(st.session_state.courses_list) == 1:
    course_progress_bar.progress(12)
if len(st.session_state.courses_list) == 2:
    course_progress_bar.progress(25)
if len(st.session_state.courses_list) == 3:
    course_progress_bar.progress(37)
if len(st.session_state.courses_list) == 4:
    course_progress_bar.progress(50)

if len(st.session_state.difficulty_ranking) == 1:
    course_progress_bar.progress(62)
if len(st.session_state.difficulty_ranking) == 2:
    course_progress_bar.progress(75)
if len(st.session_state.difficulty_ranking) == 3:
    course_progress_bar.progress(87)

if course_progress_bar.progress == 100:
    progress_text = "Course Setup Complete!"

if len(st.session_state.difficulty_ranking) >= 3:
    course_progress_bar.progress(100, text="Course Setup Complete!")
