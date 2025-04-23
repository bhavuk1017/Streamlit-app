import streamlit as st
from datetime import datetime, timedelta
import pytz
import hashlib
timezone = pytz.timezone('Asia/Kolkata')
from database import tasks_collection,submissions_collection

from auth import (
    authenticate_user,
    authenticate_invigilator,
    is_user_authenticated,
    is_invigilator_authenticated,
    get_current_user,
    get_current_invigilator,
    logout_user,
    register_user,
    get_all_invigilators)
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
from utils import generate_ai_response
from email_service import send_email, send_certificate
from certificate_generator import CertificateGenerator

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import threading

# # Create a Flask server to receive test results from React
# flask_app = Flask(__name__)
# CORS(flask_app)

# @flask_app.route('/save_test_result', methods=['POST'])
# def save_test_result_endpoint():
#     data = request.json
#     email = data.get('email')
#     skill = data.get('skill')
#     score = data.get('score')
#     feedback = data.get('feedback')
    
#     # Use your existing function to save results
#     save_test_result(email, skill, score, feedback)
    
#     # Handle certification if passed
#     if score >= 5:
#         handle_test_completion(email, skill, score)
    
#     return jsonify({"success": True})
  

# Run Flask in a separate thread
# port = 6000
# def run_flask():
#     flask_app.run(host='0.0.0.0', port=port)

# # Start Flask server in background
# threading.Thread(target=run_flask, daemon=True).start()

# Page setup
st.set_page_config(page_title="Certification Platform", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["User Dashboard", "Invigilator Dashboard", "Pending Tasks", "Test Results"])

if page == "User Dashboard":
    st.header("User Dashboard")
    
    # User Authentication
    if not is_user_authenticated():
        auth_option = st.radio("Choose an option", ["Login", "Register"])
        if auth_option=="Login":
            email = st.text_input("Enter your email")
            password = st.text_input("Enter your password", type="password")
            
            if st.button("Login as User"):
                if authenticate_user(email, password):
                    st.success("User logged in!")
                else:
                    st.error("Invalid credentials")
        else:
            # User input fields
            email = st.text_input("Enter your email")
            password = st.text_input("Enter your password", type="password")
            name = st.text_input("Enter your name")

            # Button to trigger registration
            if st.button("Register"):
                # Call the register_user function and capture its response
                response = register_user(email, password, name)
                
                # Check the response and display appropriate messages
                if response["success"]:
                    st.success(response["message"])
                else:
                    st.error(response["error"])
    if is_user_authenticated():
        email = get_current_user()
        if st.button("Logout"):
            logout_user()
            st.success("Logged out successfully!")
            st.rerun()
        # Skill Selection and Guidelines
        st.subheader("Select Skill and View Guidelines")
        skill = st.text_input("Enter a Skill:")
        if st.button("Generate Guidelines"):
            if skill:
                # Generate Guidelines
                guidelines_prompt = f"""
                Generate comprehensive guidelines for certification in {skill}. Include:
                1. Prerequisites and requirements
                2. Learning objectives
                3. Evaluation criteria
                4. Recommended preparation
                make sure to not end the response mid-sentence. Complete the response within 700 tokens.
                """
                guidelines = generate_ai_response(guidelines_prompt)
                
                with st.expander("View Skill Guidelines", expanded=True):
                    st.write(guidelines)
            
        # Test Generation Section
        if skill:
            st.subheader("Generate Test")
            # Add date picker for preferred test date
            min_date = datetime.today()
            max_date = datetime.today() + timedelta(days=30)
            preferred_date = st.date_input(
                "Select your preferred test date:",
                min_value=min_date,
                max_value=max_date,
                value=min_date
            )
        
            # Get the current time
            current_time = datetime.now(timezone).time()

            # Display the time input widget with the current time as the default value
            preferred_time = st.time_input("Select your preferred test time:")
            timecorrect=False
            # Validate if the selected time is greater than or equal to the current time
            if preferred_time < current_time:
                st.error(f"Please select a time after {current_time.strftime('%H:%M')}.")

            else:
                st.success(f"Your selected time is valid: {preferred_time.strftime('%H:%M')}")
                timecorrect=True


                            
            if st.button("Generate Test"):
                        if timecorrect:
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

                        else:
                            st.error("Please select a valid time for the test.")

       
        
        # Task Generation Section
        if skill:
            st.subheader("Generate Task")
            invigilators = get_all_invigilators()
            if invigilators:
                # Create a list of options with name and email
                invigilator_options = [f"{inv.get('name', 'Unknown')} ({inv['email']})" for inv in invigilators]
                
                # Add a dropdown to select invigilator
                selected_invigilator = st.selectbox(
                    "Select an Invigilator:",
                    options=invigilator_options
                )
        
        # Extract email from the selected option
                if selected_invigilator:
                    invigilator_email = selected_invigilator.split('(')[1].split(')')[0]
                if st.button("Generate Task"):
                    with st.spinner("Generating Task & Guidelines..."):
                        task_details, obs_sheet = generate_task(skill)
                        
                        task_data = {
                            "email": email,
                            "task": task_details,
                            "invigilator_email": invigilator_email,
                            "observation_sheet": obs_sheet,
                            "created_at": datetime.now()
                        }
                        
                        tasks_collection.insert_one(task_data)  # Save task to MongoDB
                        send_email(email, "Your Certification Task", task_details)  # Send task details to user
                        send_email(invigilator_email, "Observation Sheet", obs_sheet)  # Send observation sheet to invigilator
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
        current_invigilator_email = get_current_invigilator()
        
        # Show Pending Tasks
        st.subheader("Pending Tasks")
        pending_tasks_cursor = tasks_collection.find({"invigilator_email": current_invigilator_email})
        
        has_pending_tasks = False
        
        for task in pending_tasks_cursor:
            has_pending_tasks = True
            with st.expander(f"Pending Task: {task['task'][:50]}..."):
                st.write(f"Task: {task['task']}")
                st.write(f"Observation Sheet: {task['observation_sheet']}")
        
        if not has_pending_tasks:
            st.info("No pending tasks assigned to you.")
        
        # Show Submitted Tasks
        st.subheader("Submitted Tasks")
        submitted_tasks_cursor = submissions_collection.find({"invigilator_email": current_invigilator_email})
        
        for submission in submitted_tasks_cursor:
            task_hash = hashlib.md5(submission['task'].encode()).hexdigest()[:8]
            button_key = f"certify_{submission['email']}_{task_hash}"
            
            with st.expander(f"Completed - User: {submission['email']}, Task: {submission['task'][:50]}..."):
                st.write(f"Task: {submission['task']}")
                st.write(f"Evaluation Result: {submission['evaluation']}")
                
                if st.button("Generate Certificate", key=button_key):
                    cert_prompt = f"Generate a professional certification document for {submission['email']} for completing the task: {submission['task']}."
                    
                    # Generate certificate PDF
                    certificate_gen = CertificateGenerator()
                    certificate_path = certificate_gen.generate_certificate(
                        submission['email'],
                        submission['task'],  # Use the full task description instead of extracting skill
                        "This certification acknowledges the successful demonstration of skills and competency in the specified domain."
                    )
                    
                    # Send certificate via email
                    send_certificate(submission["email"], submission['task'], certificate_path)
                    st.success("Certificate generated and sent to user!")

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
        
        pending_tasks_cursor = tasks_collection.find({"email": email})
    
        for task in pending_tasks_cursor:
            with st.expander(f"Task: {task['task'][:50]}..."):
                st.write(task['task'])
                deadline_line = task["task"].split("\n")[1].strip()
                uploaded_file = st.file_uploader(
                    "Upload Code/Video Submission",
                    type=["txt", "mp4", "avi", "mov"],
                    key=f"submission_{task['_id']}"
                )   
            
                    
                if uploaded_file:
                    with st.spinner("Processing submission..."):
                        if handle_submission(email, uploaded_file, task):
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