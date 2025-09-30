import streamlit as st
import random
from streamlit_calendar import calendar
import uuid
import time
from datetime import date, timedelta
from openai import OpenAI
import google.generativeai as genai 
import os


from services.home import get_user_data


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

st.header("AI Tools")
import openai
from openai import OpenAI

# Connect to OpenAI API
client = OpenAI(
    api_key=st.secrets["API_KEY"],
    base_url="https://api.aimlapi.com/"
)

# Create an assistant
my_assistant = client.beta.assistants.create(
    instructions="You are a helpful assistant.",
    name="AI Assistant",
    model="gpt-4o",  # Specify the model
)

assistant_id = my_assistant.id  # Store assistant ID
thread = client.beta.threads.create()  # Create a new thread
thread_id = thread.id  # Store the thread ID

def initial_request():
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hi! Let's chat!",
    )


def send_message(user_message):
    """Send a message to the assistant and receive a full response"""
    if not user_message.strip():
        print("⚠️ Message cannot be empty!")
        return

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # Start a new run and wait for completion
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Keep responses concise and clear."
    )

    # Check if the run was successful
    if run.status == "completed":
        # Retrieve messages from the thread
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        # Find the last assistant message
        for message in reversed(messages.data):
            if message.role == "assistant":
                print()  # Add an empty line for spacing
                print(f"assistant > {message.content[0].text.value}")
                return

    print("⚠️ Error: Failed to get a response from the assistant.")


# Main chat loop
initial_request()
print("🤖 AI Assistant is ready! Type 'exit' to quit.")
while True:
    user_input = input("\nYou > ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Chat session ended. See you next time!")
        break
    send_message(user_input)
