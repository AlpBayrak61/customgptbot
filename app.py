import os
from dotenv import load_dotenv
import openai
import requests
import streamlit as st
import time
import logging

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4-1106-preview"  # "gpt-3.5-turbo-16k"

# Streamlit app configuration
st.set_page_config(page_title="Study Buddy - Chat and Learn", page_icon=":books:")

# Custom CSS for brown and yellow theme
st.markdown(
    """
    <style>
        body {
            background-color: #fdf5e6;
        }
        .stApp {
            background-color: #f8f5f1;
        }
        header {
            color: #5c4033;
            font-family: 'Arial Black', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #a0522d;
            color: #fff;
        }
        .stTextInput>div>div>input {
            background-color: #fffacd;
            border: 1px solid #a0522d;
            border-radius: 5px;
        }
        .stButton button {
            background-color: #a0522d;
            color: #fffacd;
            border: 1px solid #8b4513;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            margin: 5px;
        }
        .stButton button:hover {
            background-color: #8b4513;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title
st.title("📚 Study Buddy")
st.write("Learn fast by chatting with your documents!")

# Initialize session state variables
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "assistant_created" not in st.session_state:
    st.session_state.assistant_created = False

if "file_id" not in st.session_state:
    st.session_state.file_id = None

# Helper function to upload a file to OpenAI
def upload_file_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = openai.File.create(file=file, purpose="fine-tune")
    return response["id"]

# Helper function to wait for the assistant's run to complete
def wait_for_run_completion(thread_id, run_id, sleep_interval=5):
    while True:
        try:
            run = openai.Threads.run.retrieve(thread_id=thread_id, run_id=run_id)
            if run["status"] == "completed":
                messages = openai.Threads.messages.list(thread_id=thread_id)
                assistant_message = messages["data"][-1]["content"]
                return assistant_message
        except Exception as e:
            logging.error(f"Error while retrieving run: {e}")
            break
        time.sleep(sleep_interval)

# Sidebar: File upload
st.sidebar.title("🌟 Upload & Setup")
st.sidebar.markdown(
    "Upload a PDF file and let your assistant analyze it. Use brown and yellow to guide your experience!"
)

uploaded_file = st.sidebar.file_uploader("📄 Upload PDF", type=["pdf"])
if st.sidebar.button("📤 Upload File"):
    if uploaded_file:
        filepath = uploaded_file.name
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_id = upload_file_to_openai(filepath)
        st.session_state.file_id = file_id
        st.sidebar.success(f"✅ File uploaded with ID: {file_id}")
    else:
        st.sidebar.error("🚫 Please upload a valid PDF file.")

# Sidebar: Create Assistant
if st.sidebar.button("🤖 Create Assistant"):
    if st.session_state.file_id:
        assistant = openai.Assistants.create(
            name="Study Buddy",
            instructions="""You are a helpful study assistant who knows a lot about understanding research papers.
            Your role is to summarize papers, clarify terminology within context, and extract key figures and data.
            Cross-reference information for additional insights and answer related questions comprehensively.
            """,
            tools=[{"type": "retrieval"}],
            model=model,
            file_ids=[st.session_state.file_id],
        )
        st.session_state.assistant_created = True
        st.sidebar.success("🤝 Assistant created successfully!")
    else:
        st.sidebar.error("📂 Please upload a file first.")

# Main interface: Chat with the assistant
if st.session_state.assistant_created:
    st.subheader("💬 Chat with Study Buddy")

    user_message = st.text_input("Ask your question:", placeholder="Type your question here...")
    if st.button("Send"):
        if user_message.strip():
            # Create thread if not already created
            if not st.session_state.thread_id:
                thread = openai.Threads.create()
                st.session_state.thread_id = thread["id"]

            # Add user's message to the thread
            openai.Threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_message,
            )

            # Run assistant on the thread
            run = openai.Threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=st.session_state.file_id,
            )

            # Wait for assistant's response
            with st.spinner("🤔 Generating response..."):
                response = wait_for_run_completion(
                    thread_id=st.session_state.thread_id,
                    run_id=run["id"],
                )
                st.markdown(
                    f"**Assistant:** {response}",
                    unsafe_allow_html=True,
                )
            # Wait for assistant's response
            with st.spinner("🤔 Generating response..."):
                response = wait_for_run_completion(
                    thread_id=st.session_state.thread_id,
                    run_id=run["id"],
                )
                if response:
                    st.markdown(
                        f"**Assistant:** {response}",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error("⚠️ Failed to get a response from the assistant. Please try again.")

        else:
            st.warning("⚠️ Please enter a valid question.")
    else:
        st.write("Your assistant is ready! Ask anything related to the uploaded document.")

else:
    st.write(
        "👋 Upload a file and create your assistant in the sidebar to get started."
    )
