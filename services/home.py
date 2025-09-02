import streamlit as st
import random
from streamlit_calendar import calendar
from datetime import date, timedelta
from supabase import create_client, Client
import json


# Visual background

def background():
    page_element = """
    <style>
    [data-testid="stAppViewContainer"]{
      background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
      background-size: cover;
    }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0); }
    [data-testid="stSidebar"]> div:first-child{
      background-image: url("https://wallpapers.com/images/featured/dark-mountain-gd3o1mx0wxezbewk.jpg");
      background-size: cover;
    }
    </style>
    """
    st.markdown(page_element, unsafe_allow_html=True)

background()


# Supabase client

SUPABASE_URL = st.secrets["connections"]["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["connections"]["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Storage functions (Database to the session)


DEFAULT_DATA = {
    "courses_list": [],
    "courses_colors": [],
    "difficulty_ranking": [],
    "tasks": [],
    "complete_tasks": [],
    "today_tasks": [],
    "this_week_tasks": [],
}

def _init_user_sessions_bucket():
    if "user_sessions" not in st.session_state:
        st.session_state["user_sessions"] = {}


def load_user_session(email: str) -> dict:
    """Fetch user's blob from Supabase (or create one) and mirror into session_state."""
    _init_user_sessions_bucket()

    if email in st.session_state["user_sessions"]:
        return st.session_state["user_sessions"][email]

    # Fetch from Database
    resp = (
        supabase
        .table("user_data")
        .select("data")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    rows = getattr(resp, "data", [])

    if not rows:
        # Create a fresh record
        supabase.table("user_data").insert({
            "email": email,
            "data": DEFAULT_DATA,
        }).execute()
        st.session_state["user_sessions"][email] = json.loads(json.dumps(DEFAULT_DATA))
        return st.session_state["user_sessions"][email]

    raw = rows[0]["data"]
    if isinstance(raw, str):
        raw = json.loads(raw)

    # Ensure all expected keys exist (forward compatible)
    merged = {**DEFAULT_DATA, **raw}
    st.session_state["user_sessions"][email] = merged
    return merged


def sync_user_session_to_db(email: str) -> None:
    """Push current in-memory user blob to Supabase."""
    _init_user_sessions_bucket()
    payload = st.session_state["user_sessions"].get(email)
    if not payload:
        return
    supabase.table("user_data").update({"data": payload}).eq("email", email).execute()


def save_banner(email: str, msg: str = "Saved"):
    sync_user_session_to_db(email)
    st.toast(msg)



# Identity


username = st.session_state.get("username")
if not username:
    st.error("User not logged in.")
    st.stop()

user_session = load_user_session(username)

# ──────────────────────────────────────────────────────────────────────────────
# Dates and computed lists
# ──────────────────────────────────────────────────────────────────────────────

today = date.today()
better_today = today.strftime("%Y-%m-%d")
start = today - timedelta(days=today.weekday())
better_start = start.strftime("%Y-%m-%d")
end = start + timedelta(days=6)
better_end = end.strftime("%Y-%m-%d")

def update_today_tasks(email: str):
    us = st.session_state["user_sessions"][email]
    us["today_tasks"] = [t["name"] for t in us["tasks"] if t.get("due_date") == better_today]
    us["this_week_tasks"] = [
        t["name"]
        for t in us["tasks"]
        if t.get("due_date") and (better_start < t["due_date"] < better_end) and t["due_date"] != better_today
    ]
    save_banner(email, "Synced")

# ──────────────────────────────────────────────────────────────────────────────
# UI helpers
# ──────────────────────────────────────────────────────────────────────────────

def display_tasks(email: str):
    us = st.session_state["user_sessions"][email]
    for index, task in enumerate(list(us["tasks"])):  # list() because we may mutate
        col1, col2 = st.columns([1.25, 3])

        with col1:
            # Color based on course
            color = "#666"
            if task.get("course") in us["courses_list"]:
                color_index = us["courses_list"].index(task["course"])
                if 0 <= color_index < len(us["courses_colors"]):
                    color = us["courses_colors"][color_index]
            st.markdown(
                f"""
                <span style="background-color:{color}; color:white; padding:5px 10px; border-radius:5px; font-weight:bold;">
                {task.get('course','(No course)')}
                </span>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            with st.expander(task.get("name", f"Task {index+1}"), expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    task["name"] = st.text_input("Name", value=task.get("name", ""), key=f"name_{index}")
                    if us["courses_list"]:
                        task["course"] = st.selectbox(
                            "Course",
                            us["courses_list"],
                            index=(us["courses_list"].index(task["course"]) if task.get("course") in us["courses_list"] else 0),
                            key=f"course_{index}",
                        )
                    else:
                        st.info("Add courses in Settings.")
                        task["course"] = task.get("course", "")
                    # always store as ISO str
                    due_val = task.get("due_date") or better_today
                    task["due_date"] = st.date_input("Due Date", value=date.fromisoformat(due_val)).isoformat()
                with c2:
                    task["status"] = st.select_slider(
                        "Status",
                        ["Not Started", "In-Progress", "Near Completion", "Complete"],
                        value=task.get("status", "Not Started"),
                        key=f"status_{index}",
                    )
                    task["priority"] = st.select_slider(
                        "Priority",
                        ["Low", "Medium", "High"],
                        value=task.get("priority", "Medium"),
                        key=f"priority_{index}",
                    )
                    task["effort"] = st.slider("Effort", 1, 5, value=int(task.get("effort", 3)), key=f"effort_{index}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Update Task {index + 1}", key=f"update_button_{index}"):
                        us["tasks"][index] = task
                        update_today_tasks(email)
                    if st.button("Mark As Complete", key=f"mark_complete_button_{index}"):
                        task["status"] = "Complete"
                        # move below in completion sorter
                with c2:
                    if st.button(f"Delete Task {index + 1}", key=f"delete_{index}"):
                        del us["tasks"][index]
                        update_today_tasks(email)
                        st.experimental_rerun()

                # Completion sorter
                if task.get("status") == "Complete":
                    us["complete_tasks"].append(task)
                    del us["tasks"][index]
                    update_today_tasks(email)
                    st.experimental_rerun()


def display_completed_tasks(email: str):
    us = st.session_state["user_sessions"][email]
    for index, task in enumerate(list(us["complete_tasks"])):
        with st.expander(task.get("name", f"Completed {index+1}"), expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                task["name"] = st.text_input("Name", value=task.get("name", ""), key=f"completed_name_{index}")
                if us["courses_list"]:
                    task["course"] = st.selectbox(
                        "Course",
                        us["courses_list"],
                        index=(us["courses_list"].index(task["course"]) if task.get("course") in us["courses_list"] else 0),
                        key=f"completed_course_{index}",
                    )
                else:
                    task["course"] = task.get("course", "")
                due_val = task.get("due_date") or better_today
                task["due_date"] = st.date_input("Date Completed", value=date.fromisoformat(due_val)).isoformat()
            with c2:
                task["status"] = st.select_slider(
                    "Status",
                    ["Not Started", "In-Progress", "Near Completion", "Complete"],
                    value=task.get("status", "Complete"),
                    key=f"completed_status_{index}",
                )
                task["priority"] = st.select_slider(
                    "Priority",
                    ["Low", "Medium", "High"],
                    value=task.get("priority", "Medium"),
                    key=f"completed_priority_{index}",
                )
                task["effort"] = st.slider("Effort", 1, 5, value=int(task.get("effort", 3)), key=f"completed_effort_{index}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Move to Active Tasks List", key=f"re_add_{index}"):
                    task["status"] = "In-Progress"
                    us["tasks"].append(task)
                    del us["complete_tasks"][index]
                    update_today_tasks(email)
                    st.experimental_rerun()
            with c2:
                if st.button("Delete From Completed Tasks List", key=f"remove_from_completed_list_{index}"):
                    del us["complete_tasks"][index]
                    update_today_tasks(email)
                    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────────────────────
# PAGE LAYOUT
# ──────────────────────────────────────────────────────────────────────────────

col1, col2, col3 = st.columns([2.5, 3, 1])
with col2:
    st.markdown("# Home")

col1, col2, col3 = st.columns([1, 1.75, 1])
with col2:
    with st.expander("Add New Task", expanded=False):
        with st.form("Adding Tasks", clear_on_submit=True):
            tab1, tab2, tab3 = st.tabs(["Task Details", "Additional Details", "Submit"])
            new_task = {}
            with tab1:
                st.header("Task Details")
                new_task["name"] = st.text_input("Task Name:")
                if user_session["courses_list"]:
                    new_task["course"] = st.selectbox("Course:", user_session["courses_list"])
                else:
                    st.info("Please add courses in Settings first.")
                    new_task["course"] = ""
                new_task["due_date"] = st.date_input("Due Date:").isoformat()
            with tab2:
                st.header("Additional Details")
                new_task["status"] = st.select_slider("Status:", ["Not Started", "In-Progress", "Near Completion", "Complete"])  # noqa
                new_task["priority"] = st.select_slider("Priority:", ["Low", "Medium", "High"])  # noqa
                new_task["effort"] = st.slider("Effort Required:", 1, 5)
            with tab3:
                if st.form_submit_button("Submit"):
                    if not new_task.get("name"):
                        st.warning("Please provide a task name.")
                    else:
                        st.session_state["user_sessions"][username]["tasks"].append(new_task)
                        update_today_tasks(username)
                        st.success("Task added!")
                        st.experimental_rerun()

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Current Tasks")
    if user_session["tasks"]:
        display_tasks(username)
    else:
        st.write("No Tasks Available.")
with col2:
    st.subheader("Completed Tasks")
    if user_session["complete_tasks"]:
        display_completed_tasks(username)
    else:
        st.write("You Have Not Completed Any Tasks.")

col1, col2 = st.columns([1, 2.5])
with col1:
    st.subheader("Tasks Due Today:")
    if user_session["today_tasks"]:
        for task_name in user_session["today_tasks"]:
            st.markdown(f"- **{task_name}**")
    else:
        st.write("No Tasks Due For Today")

    st.subheader("Tasks Due Later This Week:")
    if user_session["this_week_tasks"]:
        for task_name in user_session["this_week_tasks"]:
            st.markdown(f"- **{task_name}**")
    else:
        st.write("No Tasks Due This Week")

with col2:
    st.subheader("Calendar")

    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridDay,dayGridWeek,dayGridMonth"},
        "initialView": "dayGridMonth",
        "editable": True,
        "selectable": True,
        "selectMirror": True,
    }

    # Build events from tasks
    events = []
    for task in st.session_state["user_sessions"][username]["tasks"]:
        name = task.get("name", "(Untitled)")
        course = task.get("course", "")
        color = "#666"
        if course in user_session["courses_list"]:
            idx = user_session["courses_list"].index(course)
            if 0 <= idx < len(user_session["courses_colors"]):
                color = user_session["courses_colors"][idx]
        due_date = str(task.get("due_date", better_today))
        events.append({"title": name, "color": color, "start": due_date})

    state = calendar(
        events=events,
        options=calendar_options,
        custom_css="""
        .fc-event-past { opacity:0.8; }
        .fc-event-time { font-style: italic; }
        .fc-event-title { font-weight: 600; }
        .fc-toolbar-title { font-size: 2rem; }
        """,
        key="calendar",
    )

    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

# Manual Save button (optional safety)
with st.sidebar:
    st.subheader("Data")
    if st.button("Save to Supabase now"):
        save_banner(username, "Saved to Supabase")


