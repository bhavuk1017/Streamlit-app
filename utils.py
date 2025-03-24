import json
import os
import requests
from config import GROQ_API

# def load_json(file):
#     """Load data from a JSON file."""
#     if os.path.exists(file):
#         with open(file, "r") as f:
#             return json.load(f)
#     return {}

# def save_json(file, data):
#     """Save data to a JSON file."""
#     with open(file, "w") as f:
#         json.dump(data, f, indent=4)

from database import tasks_collection, submissions_collection, test_results_collection

def generate_ai_response(prompt, max_tokens=700):
    """Generate AI response using GROQ API."""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            },
            headers={
                "Authorization": f"Bearer {GROQ_API}",
                "Content-Type": "application/json"
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Error generating AI response: {str(e)}")



def load_tasks(email):
    """Load tasks for a user from MongoDB."""
    tasks = tasks_collection.find({"email": email})
    return list(tasks)

def load_submissions(email):
    """Load submissions for a user from MongoDB."""
    submissions = submissions_collection.find({"email": email})
    return list(submissions)

def load_test_results(email):
    """Load test results for a user from MongoDB."""
    results = test_results_collection.find({"email": email})
    return list(results)

def save_task(email, task_data):
    """Save a task to MongoDB."""
    task_data["email"] = email
    tasks_collection.insert_one(task_data)

def save_submission(email, submission_data):
    """Save a submission to MongoDB."""
    submission_data["email"] = email
    submissions_collection.insert_one(submission_data)

def save_test_result(email, result_data):
    """Save a test result to MongoDB."""
    result_data["email"] = email
    test_results_collection.insert_one(result_data)

def get_all_invigilators():
    """Get all invigilators from MongoDB."""
    from database import invigilators_collection
    return list(invigilators_collection.find({}, {"_id": 0, "name": 1, "email": 1}))
