import streamlit as st
from datetime import datetime, timedelta
import hashlib

from config import SKILLS
from auth import (
    authenticate_user,
    authenticate_invigilator,
    is_user_authenticated,
    is_invigilator_authenticated,
    get_current_user
)
from test_manager import (
    generate_test,
    evaluate_test_answers,
    save_test_result,
    handle_test_completion,
    display_test_results
)
from task_manager import (
    generate_task,
    assign_task,
    handle_submission
)
from utils import load_json, generate_ai_response
from config import TASKS_FILE, INVIGILATORS
from email_service import send_email

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# Create a Flask server to receive test results from React
flask_app = Flask(__name__)
CORS(flask_app)

@flask_app.route('/save_test_result', methods=['POST'])
def save_test_result_endpoint():
    data = request.json
    email = data.get('email')
    skill = data.get('skill')
    score = data.get('score')
    feedback = data.get('feedback')
    
    # Use your existing function to save results
    save_test_result(email, skill, score, feedback)
    
    # Handle certification if passed
    if score >= 5:
        handle_test_completion(email, skill, score)
    
    return jsonify({"success": True})

# Run Flask in a separate thread
def run_flask():
    flask_app.run(port=5002)

# Start Flask server in background
threading.Thread(target=run_flask, daemon=True).start()

# Page setup
st.set_page_config(page_title="Certification Platform", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["User Dashboard", "Invigilator Dashboard", "Pending Tasks", "Test Results"])

if page == "User Dashboard":
    st.header("User Dashboard")
    
    # User Authentication
    if not is_user_authenticated():
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password", type="password")
        
        if st.button("Login as User"):
            if authenticate_user(email, password):
                st.success("User logged in!")
            else:
                st.error("Invalid credentials")
    
    # Main Dashboard Content
    if is_user_authenticated():
        email = get_current_user()
        
        # Skill Selection and Guidelines
        st.subheader("Select Skill and View Guidelines")
        skill = st.text_input("Enter a Skill:")
        
        if skill:
            # Generate Guidelines
            guidelines_prompt = f"""
            Generate comprehensive guidelines for certification in {skill}. Include:
            1. Prerequisites and requirements
            2. Learning objectives
            3. Evaluation criteria
            4. Recommended preparation
            5. Important topics to focus on
            """
            guidelines = generate_ai_response(guidelines_prompt)
            
            with st.expander("View Skill Guidelines", expanded=True):
                st.write(guidelines)
        
        # Test Generation Section
        if skill:
            st.subheader("Generate Test")
            # Add date picker for preferred test date
            min_date = datetime.today() + timedelta(days=1)
            max_date = datetime.today() + timedelta(days=30)
            preferred_date = st.date_input(
                "Select your preferred test date:",
                min_value=min_date,
                max_value=max_date,
                value=min_date
            )
            preferred_time = st.time_input("Select your preferred test time:", datetime.now().time())

                            
        if st.button("Generate Test"):
                    with st.spinner("Scheduling your test..."):
                        # Format date as ISO string for URL
                        formatted_date = preferred_date.strftime("%Y-%m-%d")
                        formatted_time = preferred_time.strftime("%H:%M")
                       
                        # Construct the React app URL with skill, email, and date
                        react_url = f"http://proctoringfrontend.netlify.app/test?skill={skill}&email={email}&testDate={formatted_date}&testTime={formatted_time}"
                        
                        # Format the date for the email
                        formatted_date1 = preferred_date.strftime("%A, %B %d, %Y")
                        
                        # Send email with test link and instructions
                        email_subject = f"Your Scheduled {skill} Test"
                        email_body = f"""
                        Dear {email},
                        
                        Your test for {skill} has been scheduled for {formatted_date1} at {formatted_time}.
                        
                        Please click on the following link to start your test on the scheduled date:
                        {react_url}
                        
                        Important instructions:
                        - The test will be proctored
                        - Ensure you have a working webcam
                        - Find a quiet place without distractions
                        - The test will last approximately 30 minutes
                        
                        Good luck!
                        """
                        
                        # Send the email
                        send_email(email, email_subject, email_body)
                        
                        st.success(f"Test scheduled for {formatted_date1} at {formatted_time}. Check your email for the test link and instructions.")



       
        
        # Task Generation Section
        if skill:
            st.subheader("Generate Task")
            invigilator = st.selectbox("Select Invigilator:", list(INVIGILATORS.keys()))
            if st.button("Generate Task"):
                with st.spinner("Generating Task & Guidelines..."):
                    task_details, obs_sheet = generate_task(skill)
                    assign_task(email, task_details, obs_sheet, invigilator)
                    
                    # Extract deadline from task details to show in success message
                    deadline_line = task_details.split("\n")[1].strip()
                    st.success(f"Task assigned and emails sent! {deadline_line}")

elif page == "Invigilator Dashboard":
    st.header("Invigilator Dashboard")
    
    # Invigilator Authentication
    if not is_invigilator_authenticated():
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password", type="password")
        
        if st.button("Login as Invigilator"):
            if authenticate_invigilator(email, password):
                st.success("Invigilator logged in!")
            else:
                st.error("Invalid invigilator credentials")
    
    # Invigilator Dashboard Content
    if is_invigilator_authenticated():
        current_invigilator_email = st.session_state["invigilator"]
        
        # Show Pending Tasks
        st.subheader("Pending Tasks")
        pending_tasks = load_json(TASKS_FILE)
        has_pending = False
        
        for user_email, tasks in pending_tasks.items():
            for task in tasks:
                if task["invigilator"] in INVIGILATORS and INVIGILATORS[task["invigilator"]]["email"] == current_invigilator_email:
                    has_pending = True
                    with st.expander(f"Pending - User: {user_email}, Task: {task['task'][:50]}..."):
                        st.write(f"Task: {task['task']}")
                        st.write(f"Observation Sheet: {task['observation_sheet']}")
        
        if not has_pending:
            st.info("No pending tasks assigned to you.")
        
        # Show Submitted Tasks
        st.subheader("Submitted Tasks")
        submissions = load_json("submissions.json")
        
        for user_email, tasks in submissions.items():
            for idx, task_info in enumerate(tasks):
                task_hash = hashlib.md5(task_info['task'].encode()).hexdigest()[:8]
                button_key = f"certify_{user_email}_{task_hash}_{idx}"
                
                with st.expander(f"Completed - User: {user_email}, Task: {task_info['task'][:50]}..."):
                    st.write(f"Task: {task_info['task']}")
                    st.write(f"Evaluation Result: {task_info['evaluation']}")
                    
                    if st.button("Generate Certificate", key=button_key):
                        cert_prompt = f"Generate a professional certification document for {user_email} for completing the task: {task_info['task']}."
                        certificate = generate_ai_response(cert_prompt)
                        send_email(user_email, "Certification Achieved!", certificate)
                        st.success("Certificate sent to user!")

elif page == "Pending Tasks":
    st.header("Pending Tasks")
    
    # User Authentication
    if not is_user_authenticated():
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password", type="password")
        
        if st.button("Login as User"):
            if authenticate_user(email, password):
                st.success("User logged in!")
            else:
                st.error("Invalid credentials")
    
    # Show Pending Tasks
    if is_user_authenticated():
        email = get_current_user()
        st.subheader(f"Pending Tasks for {email}")
        
        pending_tasks = load_json(TASKS_FILE)
        if email in pending_tasks and pending_tasks[email]:
            for task_info in pending_tasks[email]:
                with st.expander(f"Task: {task_info['task'][:50]}..."):
                    st.write(task_info["task"])
                    
                    # Check if task has a deadline
                    if "TASK DEADLINE:" in task_info["task"]:
                        deadline_line = task_info["task"].split("\n")[1].strip()
                        st.warning(deadline_line)
                    
                    uploaded_file = st.file_uploader(
                        "Upload Code/Video Submission",
                        type=["txt", "mp4", "avi", "mov"],
                        key=f"submission_{task_info['task']}"
                    )
                    
                    if uploaded_file:
                        with st.spinner("Processing submission..."):
                            if handle_submission(email, uploaded_file, task_info):
                                st.success("Task evaluated!")
        else:
            st.info("No pending tasks found.")

elif page == "Test Results":
    st.header("Test Results")
    
    # User Authentication
    if not is_user_authenticated():
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password", type="password")
        
        if st.button("Login as User"):
            if authenticate_user(email, password):
                st.success("User logged in!")
            else:
                st.error("Invalid credentials")
    
    # Display Test Results
    if is_user_authenticated():
        email = get_current_user()
        st.subheader(f"Test Results for {email}")
        display_test_results(email)