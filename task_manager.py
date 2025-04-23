# import streamlit as st
# from utils import generate_ai_response, load_json, save_json
# from email_service import send_task_details, send_observation_sheet, send_evaluation_result
# from video_processor import process_video_submission
# from config import TASKS_FILE, SUBMISSIONS_FILE, INVIGILATORS
# from datetime import datetime, timedelta

# def determine_task_deadline(task_details):
#     """Determine appropriate deadline based on task complexity."""
#     # Use AI to analyze task complexity and suggest deadline
#     deadline_prompt = f"""
#     Analyze this task and suggest an appropriate deadline (in days) between 3 and 60 days. Consider:
#     1. Task complexity
#     2. Required research
#     3. Implementation time
#     4. Testing requirements
    
#     Task: {task_details}
    
#     Return only the number of days as a single number.
#     """
#     try:
#         days_str = generate_ai_response(deadline_prompt).strip()
#         days = int(days_str)
#         # Ensure days are within bounds
#         days = max(3, min(60, days))
#         deadline_date = datetime.today() + timedelta(days=days)
#         return deadline_date.strftime("%Y-%m-%d"), days
#     except:
#         # Default to 14 days if there's any error
#         default_date = datetime.today() + timedelta(days=14)
#         return default_date.strftime("%Y-%m-%d"), 14

# def generate_task(skill):
#     """Generate a certification task for the given skill."""
#     prompt = f"""
#     Generate a detailed real-world certification task for {skill}. 
#     The task should:
#     1. Have clear objectives
#     2. Include specific requirements
#     3. List expected deliverables
#     4. Specify evaluation criteria
    
#     Ensure completion and do not leave mid sentence. 
#     The submission format can be a .txt file or a video file as per the task requirements.
#     """
#     task_details = generate_ai_response(prompt)
    
#     # Generate deadline
#     deadline_date, days = determine_task_deadline(task_details)
    
#     # Add deadline to task details
#     task_with_deadline = f"""
#     TASK DEADLINE: {deadline_date} ({days} days)
    
#     {task_details}
    
#     Please ensure to complete and submit this task before the deadline.
#     Late submissions may affect evaluation.
#     """
    
#     obs_prompt = f"Generate an observation sheet to evaluate the following task: {task_details} in max 700 tokens."
#     obs_sheet = generate_ai_response(obs_prompt)
    
#     return task_with_deadline, obs_sheet

# def assign_task(email, task_details, obs_sheet, invigilator):
#     """Assign task to user and notify relevant parties."""
#     pending_tasks = load_json(TASKS_FILE)
    
#     if email not in pending_tasks:
#         pending_tasks[email] = []
    
#     pending_tasks[email].append({
#         "task": task_details,
#         "invigilator": invigilator,
#         "observation_sheet": obs_sheet
#     })
    
#     save_json(TASKS_FILE, pending_tasks)
    
#     # Send notifications
#     send_task_details(email, task_details)
#     send_observation_sheet(INVIGILATORS[invigilator]["email"], obs_sheet)

# def evaluate_submission(submission_text, obs_sheet, is_video=False):
#     """Evaluate task submission using AI."""
#     if submission_text.startswith("Error") or submission_text.startswith("Video processing"):
#         st.error(submission_text)
#         return None, None

#     if is_video:
#         evaluation_prompt = (
#             "This submission is a transcript of the video file provided by the user. "
#             "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
#             "Give 0 only if the user uploaded something of other topic. "
#             "If it is similar and the user has tried then give atleast 5 marks. "
#             f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
#             f"Submission Text:\n{submission_text}"
#         )
#     else:
#         evaluation_prompt = (
#             "This is a .txt file submitted by the user. "
#             "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
#             "Give 0 only if the user uploaded something of other topic. "
#             "If it is similar and the user has tried then give atleast 5 marks. "
#             f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
#             f"Submission Text:\n{submission_text}"
#         )
    
#     evaluation_result = generate_ai_response(evaluation_prompt)
    
#     # Check if submission completely failed
#     import re
#     match = re.search(r"Score: 0/100", evaluation_result)
#     score = 0 if match else 6
    
#     return score, evaluation_result

# def handle_submission(email, uploaded_file, task_info):
#     """Process and evaluate task submission."""
#     try:
#         file_type = uploaded_file.type
#         is_video = False
        
#         if file_type == "text/plain":
#             submission_text = uploaded_file.read().decode()
#         elif file_type.startswith("video/"):
#             is_video = True
#             submission_text = process_video_submission(uploaded_file)
#             # If video processing failed, show error and return
#             if submission_text.startswith(("Error", "Video processing")):
#                 st.error(submission_text)
#                 return False
#         else:
#             st.error("Invalid file type. Only .txt, .mp4, .avi, and .mov files are allowed.")
#             return False
        
#         score, evaluation_result = evaluate_submission(
#             submission_text, 
#             task_info["observation_sheet"],
#             is_video
#         )

#         if score is None:  # Evaluation failed
#             return False
        
#         if 0 <= score <= 5:
#             st.error("poor/wrong submission, try again")
#             return False
        
#         # Save submission
#         submissions = load_json(SUBMISSIONS_FILE)
#         if email not in submissions:
#             submissions[email] = []
        
#         submissions[email].append({
#             "task": task_info["task"],
#             "evaluation": evaluation_result
#         })
#         save_json(SUBMISSIONS_FILE, submissions)
        
#         # Notify invigilator
#         send_evaluation_result(
#             INVIGILATORS[task_info["invigilator"]]["email"],
#             evaluation_result
#         )
        
#         # Remove completed task
#         pending_tasks = load_json(TASKS_FILE)
#         pending_tasks[email].remove(task_info)
#         save_json(TASKS_FILE, pending_tasks)
        
#         return True
        
#     except Exception as e:
#         st.error(f"Error processing submission: {str(e)}")
#         return False

# import streamlit as st
# from datetime import datetime, timedelta
# from utils import generate_ai_response, save_task, save_submission, load_tasks
# from email_service import send_task_details, send_observation_sheet, send_evaluation_result
# from video_processor import process_video_submission
# from database import tasks_collection, submissions_collection, invigilators_collection, users_collection
# import re

# def determine_task_deadline(task_details):
#     """Determine appropriate deadline based on task complexity."""
#     # Use AI to analyze task complexity and suggest deadline
#     deadline_prompt = f"""
#     Analyze this task and suggest an appropriate deadline (in days) between 3 and 60 days. Consider:
#     1. Task complexity
#     2. Required research
#     3. Implementation time
#     4. Testing requirements
#     Task: {task_details}
#     Return only the number of days as a single number.
#     """
    
#     try:
#         days_str = generate_ai_response(deadline_prompt).strip()
#         days = int(days_str)
#         # Ensure days are within bounds
#         days = max(3, min(60, days))
#         deadline_date = datetime.today() + timedelta(days=days)
#         return deadline_date.strftime("%Y-%m-%d"), days
#     except:
#         # Default to 14 days if there's any error
#         default_date = datetime.today() + timedelta(days=14)
#         return default_date.strftime("%Y-%m-%d"), 14

# def generate_task(skill):
#     """Generate a certification task for the given skill."""
#     prompt = f"""
#     Generate a detailed real-world certification task for {skill}.
#     The task should:
#     1. Have clear objectives
#     2. Include specific requirements
#     3. List expected deliverables
#     4. Specify evaluation criteria
#     Ensure completion and do not leave mid sentence.
#     The submission format can be a .txt file or a video file as per the task requirements.
#     """
    
#     task_details = generate_ai_response(prompt)
    
#     # Generate deadline
#     deadline_date, days = determine_task_deadline(task_details)
    
#     # Add deadline to task details
#     task_with_deadline = f"""
#     TASK DEADLINE: {deadline_date} ({days} days)
#     {task_details}
#     Please ensure to complete and submit this task before the deadline.
#     Late submissions may affect evaluation.
#     """
    
#     obs_prompt = f"Generate an observation sheet to evaluate the following task: {task_details} in max 700 tokens."
#     obs_sheet = generate_ai_response(obs_prompt)
    
#     return task_with_deadline, obs_sheet

# def assign_task(email, task_details, obs_sheet, invigilator_email):
#     """Assign task to user and notify relevant parties."""
#     invigilator = invigilators_collection.find_one({"email": invigilator_email})
    
#     if not invigilator:
#         st.error(f"Invigilator with email {invigilator_email} not found.")
#         return
    
#     task_data = {
#         "email": email,
#         "task": task_details,
#         "invigilator_email": invigilator_email,
#         "invigilator_name": invigilator.get("name", "Unknown"),
#         "observation_sheet": obs_sheet,
#         "created_at": datetime.now()
#     }
    
#     tasks_collection.insert_one(task_data)
    
#     # Send notifications
#     send_task_details(email, task_details)
#     send_observation_sheet(invigilator_email, obs_sheet)

# def evaluate_submission(submission_text, obs_sheet, is_video=False):
#     """Evaluate task submission using AI."""
#     if submission_text.startswith("Error") or submission_text.startswith("Video processing"):
#         st.error(submission_text)
#         return None, None
    
#     if is_video:
#         evaluation_prompt = (
#             "This submission is a transcript of the video file provided by the user. "
#             "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
#             "Give 0 only if the user uploaded something of other topic. "
#             "If it is similar and the user has tried then give atleast 5 marks. "
#             f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
#             f"Submission Text:\n{submission_text}"
#         )
#     else:
#         evaluation_prompt = (
#             "This is a .txt file submitted by the user. "
#             "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
#             "Give 0 only if the user uploaded something of other topic. "
#             "If it is similar and the user has tried then give atleast 5 marks. "
#             f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
#             f"Submission Text:\n{submission_text}"
#         )
    
#     evaluation_result = generate_ai_response(evaluation_prompt)
    
#     # Check if submission completely failed
#     match = re.search(r"Score: 0/100", evaluation_result)
#     score = 0 if match else 6
    
#     return score, evaluation_result

# def handle_submission(email, uploaded_file, task_info):
#     """Process and evaluate task submission."""
#     try:
#         file_type = uploaded_file.type
#         is_video = False
        
#         if file_type == "text/plain":
#             submission_text = uploaded_file.read().decode()
#         elif file_type.startswith("video/"):
#             is_video = True
#             submission_text = process_video_submission(uploaded_file)
#             # If video processing failed, show error and return
#             if submission_text.startswith(("Error", "Video processing")):
#                 st.error(submission_text)
#                 return False
#         else:
#             st.error("Invalid file type. Only .txt, .mp4, .avi, and .mov files are allowed.")
#             return False
        
#         score, evaluation_result = evaluate_submission(
#             submission_text,
#             task_info["observation_sheet"],
#             is_video
#         )
        
#         if score is None:  # Evaluation failed
#             return False
        
#         if 0 <= score <= 5:
#             st.error("poor/wrong submission, try again")
#             return False
        
#         # Save submission
#         submission_data = {
#             "email": email,
#             "task": task_info["task"],
#             "evaluation": evaluation_result,
#             "submitted_at": datetime.now()
#         }
        
#         submissions_collection.insert_one(submission_data)
        
#         # Notify invigilator
#         send_evaluation_result(
#             task_info["invigilator_email"],
#             evaluation_result
#         )
        
#         # Remove completed task
#         tasks_collection.delete_one({"_id": task_info["_id"]})
        
#         return True
    
#     except Exception as e:
#         st.error(f"Error processing submission: {str(e)}")
#         return False
import streamlit as st
from datetime import datetime, timedelta
from utils import generate_ai_response, save_task, save_submission, load_tasks
from email_service import send_task_details, send_observation_sheet, send_evaluation_result
from video_processor import process_video_submission
from database import tasks_collection, submissions_collection, invigilators_collection,users_collection
import re

def determine_task_deadline(task_details):
    """Determine appropriate deadline based on task complexity."""
    # Use AI to analyze task complexity and suggest deadline
    deadline_prompt = f"""
    Analyze this task and suggest an appropriate deadline (in days) between 3 and 60 days. Consider:
    1. Task complexity
    2. Required research
    3. Implementation time
    4. Testing requirements
    Task: {task_details}
    Return only the number of days as a single number.
    """
    
    try:
        days_str = generate_ai_response(deadline_prompt).strip()
        days = int(days_str)
        # Ensure days are within bounds
        days = max(3, min(60, days))
        deadline_date = datetime.today() + timedelta(days=days)
        return deadline_date.strftime("%Y-%m-%d"), days
    except:
        # Default to 14 days if there's any error
        default_date = datetime.today() + timedelta(days=14)
        return default_date.strftime("%Y-%m-%d"), 14

def generate_task(skill):
    """Generate a certification task for the given skill."""
    prompt = f"""
    Generate a detailed real-world certification task for {skill}.
    The task should:
    1. Have clear objectives
    2. Include specific requirements
    3. List expected deliverables
    4. Specify evaluation criteria
    Ensure completion and do not leave mid sentence.
    The submission format can be a .txt file or a video file as per the task requirements.
    """
    
    task_details = generate_ai_response(prompt)
    
    # Generate deadline
    deadline_date, days = determine_task_deadline(task_details)
    
    # Add deadline to task details
    task_with_deadline = f"""
    TASK DEADLINE: {deadline_date} ({days} days)
    {task_details}
    Please ensure to complete and submit this task before the deadline.
    Late submissions may affect evaluation.
    """
    
    obs_prompt = f"Generate an observation sheet to evaluate the following task: {task_details} in max 700 tokens."
    obs_sheet = generate_ai_response(obs_prompt)
    
    return task_with_deadline, obs_sheet

def assign_task(email, task_details, obs_sheet, invigilator_email):
    """Assign task to user and notify relevant parties."""
    invigilator = invigilators_collection.find_one({"email": invigilator_email})
    
    if not invigilator:
        st.error(f"Invigilator with email {invigilator_email} not found.")
        return
    
    task_data = {
        "email": email,
        "task": task_details,
        "invigilator_email": invigilator_email,
        "invigilator_name": invigilator.get("name", "Unknown"),
        "observation_sheet": obs_sheet,
        "created_at": datetime.now()
    }
    
    tasks_collection.insert_one(task_data)
    
    # Send notifications
    send_task_details(email, task_details)
    send_observation_sheet(invigilator_email, obs_sheet)

def evaluate_submission(submission_text, obs_sheet, is_video=False):
    """Evaluate task submission using AI."""
    if submission_text.startswith("Error") or submission_text.startswith("Video processing"):
        st.error(submission_text)
        return None, None
    
    if is_video:
        evaluation_prompt = (
            "This submission is a transcript of the video file provided by the user. "
            "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
            "Give 0 only if the user uploaded something of other topic. "
            "If it is similar and the user has tried then give atleast 5 marks. "
            f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
            f"Submission Text:\n{submission_text}"
        )
    else:
        evaluation_prompt = (
            "This is a .txt file submitted by the user. "
            "If the task is completely incorrect begin your evaluation result by saying Score: 0/100. "
            "Give 0 only if the user uploaded something of other topic. "
            "If it is similar and the user has tried then give atleast 5 marks. "
            f"Evaluate this submission based on the observation sheet: {obs_sheet}. "
            f"Submission Text:\n{submission_text}"
        )
    
    evaluation_result = generate_ai_response(evaluation_prompt)
    
    # Check if submission completely failed
    match = re.search(r"Score: 0/100", evaluation_result)
    score = 0 if match else 6
    
    return score, evaluation_result

def handle_submission(email, uploaded_file, task_info):
    """Process and evaluate task submission."""
    try:
        file_type = uploaded_file.type
        is_video = False
        
        if file_type == "text/plain":
            submission_text = uploaded_file.read().decode()
        elif file_type.startswith("video/"):
            is_video = True
            submission_text = process_video_submission(uploaded_file)
            # If video processing failed, show error and return
            if submission_text.startswith(("Error", "Video processing")):
                st.error(submission_text)
                return False
        else:
            st.error("Invalid file type. Only .txt, .mp4, .avi, and .mov files are allowed.")
            return False
        
        score, evaluation_result = evaluate_submission(
            submission_text,
            task_info["observation_sheet"],
            is_video
        )
        
        if score is None:  # Evaluation failed
            return False
        
        if 0 <= score <= 5:
            st.error("poor/wrong submission, try again")
            return False
        
        # Get user's name from the email
        user = users_collection.find_one({"email": email}, {"name": 1})

        # Fallback if user not found
        user_name = user["name"] if user and "name" in user else "Unknown"

        # Now build submission_data
        submission_data = {
            "email": email,
            "name": user_name,  # include the name here
            "task": task_info["task"],
            "evaluation": evaluation_result,
            "submitted_at": datetime.now(),
            "invigilator_email": task_info["invigilator_email"]
        }

        submissions_collection.insert_one(submission_data)
        
        # Notify invigilator
        send_evaluation_result(
            task_info["invigilator_email"],
            evaluation_result
        )
        
        # Remove completed task
        tasks_collection.delete_one({"_id": task_info["_id"]})
        
        return True
    
    except Exception as e:
        st.error(f"Error processing submission: {str(e)}")
        return False
