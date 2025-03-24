# import re
# import streamlit as st
# from datetime import datetime, timedelta
# import matplotlib.pyplot as plt
# import hashlib
# from utils import generate_ai_response, load_json, save_json
# from email_service import send_email, send_certificate
# from config import TEST_RESULTS_FILE

# def determine_test_deadline(skill):
#     """Determine appropriate deadline for the test based on skill complexity."""
#     deadline_prompt = f"""
#     Analyze this skill and suggest an appropriate test completion deadline (in days) between 1 and 30 days.
#     Consider:
#     1. Skill complexity
#     2. Required preparation
#     3. Study time needed
#     4. Practice requirements
    
#     Skill: {skill}
    
#     Return only the number of days as a single number.
#     """
#     try:
#         days_str = generate_ai_response(deadline_prompt).strip()
#         days = int(days_str)
#         # Ensure days are within bounds
#         days = max(1, min(30, days))
#         deadline_date = datetime.today() + timedelta(days=days)
#         return deadline_date.strftime("%Y-%m-%d"), days
#     except:
#         # Default to 7 days if there's any error
#         default_date = datetime.today() + timedelta(days=7)
#         return default_date.strftime("%Y-%m-%d"), 7

# def generate_test(skill):
#     """Generate a test for the given skill."""
#     test_prompt = f"""
#     Generate a 10-question test for {skill}. 
#     The test should:
#     1. Cover fundamental concepts
#     2. Include advanced topics
#     3. Test practical understanding
#     4. Assess problem-solving ability
    
#     Output the questions in a numbered list format.
#     """
#     raw_questions = generate_ai_response(test_prompt)
    
#     # Parse questions into a list
#     questions = [q.strip() for q in raw_questions.split("\n") if q.strip() and q[0].isdigit()]
    
#     if len(questions) == 10:
#         deadline_date, days = determine_test_deadline(skill)
#         return questions, deadline_date, days
#     return None, None, None

# def evaluate_test_answers(questions, answers):
#     """Evaluate test answers and provide feedback."""
#     answers_prompt = (
#         "Evaluate the following answers based on the given test questions. "
#         "Provide a score out of 10, and return the result in this format strictly:\n\n"
#         "Score: X/10\n\n"
#         "Feedback: (Detailed feedback on each answer)\n\n"
#     )
    
#     for i in range(10):
#         answers_prompt += f"**Q{i+1}**: {questions[i]}\n"
#         answers_prompt += f"**A{i+1}**: {answers[i]}\n\n"

#     evaluation_result = generate_ai_response(answers_prompt)
    
#     # Extract score
#     match = re.search(r"Score:\s*(\d+)/10", evaluation_result)
#     score = int(match.group(1)) if match else 0
    
#     return score, evaluation_result

# def save_test_result(email, skill, score, feedback):
#     """Save test result to file."""
#     test_results = load_json(TEST_RESULTS_FILE)
    
#     if email not in test_results:
#         test_results[email] = []
    
#     test_results[email].append({
#         "skill": skill,
#         "date": datetime.today().strftime("%Y-%m-%d"),
#         "score": score,
#         "feedback": feedback
#     })
    
#     save_json(TEST_RESULTS_FILE, test_results)

# def handle_test_completion(email, skill, score):
#     """Handle test completion and certification if passed."""
#     if score >= 5:
#         cert_prompt = f"Generate a professional certification document for {email} for passing the test with a score of {score}/10."
#         certificate = generate_ai_response(cert_prompt)
#         send_certificate(email, f"Test Certification - {skill}", certificate)
#         return True
#     return False

# def display_test_results(email):
#     """Display test results and score trend graph."""
#     test_results = load_json(TEST_RESULTS_FILE)
    
#     if email not in test_results or not test_results[email]:
#         st.info("No test results found.")
#         return

#     scores = []
#     dates = []

#     for test in test_results[email]:
#         test_hash = hashlib.md5(f"{test['skill']}_{test['date']}".encode()).hexdigest()[:8]
        
#         st.write(f"**Skill:** {test['skill']}")
#         st.write(f"**Date:** {test['date']}")
#         st.write(f"**Score:** {test['score']}/10")
#         st.write("**Feedback:**")
#         st.text_area("", test["feedback"], height=150, disabled=True, key=f"feedback_{test_hash}")
        
#         scores.append(test["score"])
#         dates.append(test["date"])

#     # Show Score Trend Graph
#     if scores:
#         fig, ax = plt.subplots()
#         ax.plot(dates, scores, marker="o", linestyle="-", color="blue")
#         ax.set_xlabel("Date")
#         ax.set_ylabel("Score")
#         ax.set_title("Test Score Trend")
#         st.pyplot(fig)



import re
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import hashlib
from utils import generate_ai_response
from email_service import send_email, send_certificate
from database import test_results_collection

def determine_test_deadline(skill):
    """Determine appropriate deadline for the test based on skill complexity."""
    deadline_prompt = f"""
    Analyze this skill and suggest an appropriate test completion deadline (in days) between 1 and 30 days.
    Consider:
    1. Skill complexity
    2. Required preparation
    3. Study time needed
    4. Practice requirements
    Skill: {skill}
    Return only the number of days as a single number.
    """
    
    try:
        days_str = generate_ai_response(deadline_prompt).strip()
        days = int(days_str)
        # Ensure days are within bounds
        days = max(1, min(30, days))
        deadline_date = datetime.today() + timedelta(days=days)
        return deadline_date.strftime("%Y-%m-%d"), days
    except:
        # Default to 7 days if there's any error
        default_date = datetime.today() + timedelta(days=7)
        return default_date.strftime("%Y-%m-%d"), 7

def generate_test(skill):
    """Generate a test for the given skill."""
    test_prompt = f"""
    Generate a 10-question test for {skill}.
    The test should:
    1. Cover fundamental concepts
    2. Include advanced topics
    3. Test practical understanding
    4. Assess problem-solving ability
    Output the questions in a numbered list format.
    """
    
    raw_questions = generate_ai_response(test_prompt)
    
    # Parse questions into a list
    questions = [q.strip() for q in raw_questions.split("\n") if q.strip() and q[0].isdigit()]
    
    if len(questions) == 10:
        deadline_date, days = determine_test_deadline(skill)
        return questions, deadline_date, days
    
    return None, None, None

def evaluate_test_answers(questions, answers):
    """Evaluate test answers and provide feedback."""
    answers_prompt = (
        "Evaluate the following answers based on the given test questions. "
        "Provide a score out of 10, and return the result in this format strictly:\n\n"
        "Score: X/10\n\n"
        "Feedback: (Detailed feedback on each answer)\n\n"
    )
    
    for i in range(10):
        answers_prompt += f"**Q{i+1}**: {questions[i]}\n"
        answers_prompt += f"**A{i+1}**: {answers[i]}\n\n"
    
    evaluation_result = generate_ai_response(answers_prompt)
    
    # Extract score
    match = re.search(r"Score:\s*(\d+)/10", evaluation_result)
    score = int(match.group(1)) if match else 0
    
    return score, evaluation_result

def save_test_result(email, skill, score, feedback):
    """Save test result to MongoDB."""
    test_result = {
        "email": email,
        "skill": skill,
        "date": datetime.today().strftime("%Y-%m-%d"),
        "score": score,
        "feedback": feedback
    }
    
    test_results_collection.insert_one(test_result)

def handle_test_completion(email, skill, score):
    """Handle test completion and certification if passed."""
    if score >= 5:
        cert_prompt = f"Generate a professional certification document for {email} for passing the test with a score of {score}/10."
        certificate = generate_ai_response(cert_prompt)
        send_certificate(email, f"Test Certification - {skill}", certificate)
        return True
    return False

def display_test_results(email):
    """Display test results and score trend graph."""
    test_results = list(test_results_collection.find({"email": email}))
    
    if not test_results:
        st.info("No test results found.")
        return
    
    scores = []
    dates = []
    
    for test in test_results:
        test_hash = hashlib.md5(f"{test['skill']}_{test['date']}".encode()).hexdigest()[:8]
        st.write(f"**Skill:** {test['skill']}")
        st.write(f"**Date:** {test['date']}")
        st.write(f"**Score:** {test['score']}/10")
        st.write("**Feedback:**")
        st.text_area("", test["feedback"], height=150, disabled=True, key=f"feedback_{test_hash}")
        
        scores.append(test["score"])
        dates.append(test["date"])
    
    # Show Score Trend Graph
    if scores:
        fig, ax = plt.subplots()
        ax.plot(dates, scores, marker="o", linestyle="-", color="blue")
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.set_title("Test Score Trend")
        st.pyplot(fig)
