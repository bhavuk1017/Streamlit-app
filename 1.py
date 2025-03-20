import base64
import streamlit as st
import json
import os
import requests
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import hashlib

# Load environment variables
GROQ_API = "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"

# Sample Credentials
USERS = {"bhavukprasad2004@gmail.com": "password123", "user2@example.com": "password456"}
INVIGILATORS = {
    "John Doe": {"email": "bhavukprasad2004@gmail.com", "password": "invigilator123"},
    "Jane Smith": {"email": "jane.smith@example.com", "password": "invigilator456"}
}

# Skills
skills = ["Python Programming", "Data Analysis", "Machine Learning", "Web Development", "Essay Writing", "Poem Writing", "Article Writing", "Story Writing"]

# JSON File Storage
TASKS_FILE = "tasks.json"
SUBMISSIONS_FILE = "submissions.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def send_email(to_email, subject, body):
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.send"])
    service = build("gmail", "v1", credentials=creds)
    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

pending_tasks = load_json(TASKS_FILE)
submissions = load_json(SUBMISSIONS_FILE)

# Streamlit UI
st.set_page_config(page_title="Certification Platform", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["User Dashboard", "Invigilator Dashboard", "Pending Tasks", "Test Results"])


if page == "User Dashboard":
    st.header("User Dashboard")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    
    if st.button("Login as User"):
        if email in USERS and USERS[email] == password:
            st.session_state["user"] = email
            st.success("User logged in!")
        else:
            st.error("Invalid credentials")
    
    if "user" in st.session_state:
        skill = st.text_input("Enter a Skill:")
        date = st.date_input("Select Submission Date:", min_value=datetime.today())
        invigilator = st.selectbox("Select Invigilator:", list(INVIGILATORS.keys()))
        if st.button("Generate Test"):
            with st.spinner("Generating Test..."):
                test_prompt = f"Generate a 10-question test for {skill}. Provide questions that test fundamental and advanced concepts in this skill. Output the questions in a numbered list format."
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": test_prompt}],
                    "max_tokens": 700
                }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})

                raw_questions = response.json()["choices"][0]["message"]["content"]
                
                # Parse questions into a list (assuming numbered format like "1. Question ...")
                questions = [q.strip() for q in raw_questions.split("\n") if q.strip() and q[0].isdigit()]

                if len(questions) == 10:
                    st.session_state["test_questions"] = questions
                    st.session_state["taking_test"] = True
                    st.session_state["user_answers"] = [""] * 10  # Empty answer fields
                    st.success("Test generated! Starting test...")
                else:
                    st.error("Failed to parse questions properly. Please try again.")

        if st.session_state.get("taking_test"):
            st.header("Test Screen")

            # List to store user answers
            for i, question in enumerate(st.session_state["test_questions"], 1):
                st.write(f"**{i}. {question}**")
                st.session_state["user_answers"][i-1] = st.text_input(f"Your answer:", key=f"answer_{i}")
            TEST_RESULTS_FILE = "test_results.json"
            test_results = load_json(TEST_RESULTS_FILE)
            if st.button("Submit Test"):
                with st.spinner("Evaluating your answers..."):
                    answers_prompt = (
                        "Evaluate the following answers based on the given test questions. "
                        "Provide a score out of 10, and return the result in this format strictly:\n\n"
                        "Score: X/10\n\n"
                        "Feedback: (Detailed feedback on each answer)\n\n"
                    )
                    
                    for i in range(10):
                        answers_prompt += f"**Q{i+1}**: {st.session_state['test_questions'][i]}\n"
                        answers_prompt += f"**A{i+1}**: {st.session_state['user_answers'][i]}\n\n"

                    eval_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": answers_prompt}],
                        "max_tokens": 700
                    }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})

                    evaluation_result = eval_response.json()["choices"][0]["message"]["content"]

                    # Extract score using regex
                    import re
                    match = re.search(r"Score:\s*(\d+)/10", evaluation_result)
                    if match:
                        score = int(match.group(1))
                    else:
                        st.error("Failed to extract score. Please check the evaluation response.")
                        st.text(evaluation_result)  # Show raw response for debugging
                        score = 0  # Default to 0 if extraction fails
                    if email not in test_results:
                        test_results[email] = []
                    
                    test_results[email].append({
                        "skill": skill,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "score": score,
                        "feedback": evaluation_result
                    })

                    save_json(TEST_RESULTS_FILE, test_results)
                    if score >= 5:
                        st.success(f"Congratulations! You scored {score}/10. You passed the test.")

                        cert_prompt = f"Generate a professional certification document for {email} for passing the test with a score of {score}/10."
                        cert_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [{"role": "user", "content": cert_prompt}],
                            "max_tokens": 700
                        }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})

                        certificate = cert_response.json()["choices"][0]["message"]["content"]
                        send_email(email, "Test Certification Achieved!", certificate)
                        st.success("Certificate sent to your email!")
                        st.session_state["taking_test"] = False
                    else:
                        st.error(f"Sorry, you scored {score}/10. You did not pass. Try again!")



        if st.button("Generate Task"):
            with st.spinner("Generating Task & Guidelines..."):
                prompt = f"Generate a detailed real-world certification task for {skill}. Ensure completion and do not leave mid sentence. The submission format can be a .txt file or a video file as per the task requirements."
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 700
                }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})
                task_details = response.json()["choices"][0]["message"]["content"]
                
                obs_prompt = f"Generate an observation sheet to evaluate the following task: {task_details} in max 700 tokens."
                obs_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": obs_prompt}],
                    "max_tokens": 700
                }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})
                obs_sheet = obs_response.json()["choices"][0]["message"]["content"]
                
                if email not in pending_tasks:
                    pending_tasks[email] = []
                pending_tasks[email].append({
                    "task": task_details,
                    "invigilator": invigilator,
                    "observation_sheet": obs_sheet
                })
                save_json(TASKS_FILE, pending_tasks)
                
                send_email(email, "Your Certification Task", task_details)
                send_email(INVIGILATORS[invigilator]["email"], "Observation Sheet", obs_sheet)
                st.success("Task assigned and emails sent!")

        
                if page == "Pending Tasks":
                    st.subheader("Pending Tasks")
                    if email in pending_tasks and pending_tasks[email]:
                        for task_info in pending_tasks[email]:
                            with st.expander(f"Task: {task_info['task'][:50]}..."):
                                st.write(task_info['task'])
                            uploaded_file = st.file_uploader("Upload Code/Video Submission", type=["txt", "mp4", "avi", "mov"], key=f"submission_{task_info['task']}")
                            if uploaded_file:
                                vid= False
                                with st.spinner("Evaluating submission..."):
                                    file_type = uploaded_file.type
                                    if file_type == "text/plain":
                                        # Text file submission
                                        submission_text = uploaded_file.read().decode()
                                    elif file_type.startswith("video/"):
                                        # Video file submission
                                        vid=True
                                        try:
                                            from moviepy.editor import VideoFileClip # type: ignore
                                            # Save the video file
                                            video_path = "temp_video." + uploaded_file.name.split(".")[-1]
                                            with open(video_path, "wb") as f:
                                                f.write(uploaded_file.read())
        
                                            # Extract audio from video
                                            video_clip = VideoFileClip(video_path)
                                            audio_path = "temp_audio.wav"
                                            audio_clip = video_clip.audio
                                            audio_clip.write_audiofile(audio_path)
                                            audio_clip.close()
                                            video_clip.close()
        
                                            # Transcribe audio 
                                            import speech_recognition as sr
                                            def transcribe_audio_chunks(audio_path):
                                                try:
                                                    from pydub import AudioSegment
                                                    import speech_recognition as sr
                                                    import os

                                                    # Load audio file
                                                    audio = AudioSegment.from_wav(audio_path)

                                                    # Set chunk length (in milliseconds)
                                                    chunk_length_ms = 15000

                                                    # Get the number of chunks
                                                    num_chunks = len(audio) // chunk_length_ms

                                                    # Initialize the complete transcript
                                                    complete_transcript = ""

                                                    # Iterate through the chunks
                                                    for i in range(num_chunks):
                                                        start = i * chunk_length_ms
                                                        end = (i + 1) * chunk_length_ms
                                                        chunk = audio[start:end]

                                                        # Export the chunk to a temporary file
                                                        chunk_filename = f"temp_chunk_{i}.wav"
                                                        chunk.export(chunk_filename, format="wav")

                                                        # Transcribe the chunk
                                                        recognizer = sr.Recognizer()
                                                        recognizer.energy_threshold = 150
                                                        with sr.AudioFile(chunk_filename) as source:
                                                            audio_data = recognizer.record(source)
                                                            try:
                                                                text = recognizer.recognize_google(audio_data, language="en-US")
                                                                chunk_transcript = text
                                                            except sr.UnknownValueError:
                                                                chunk_transcript = ""
                                                            except sr.RequestError as e:
                                                                chunk_transcript = ""

                                                        # Append the chunk transcript to the complete transcript
                                                        complete_transcript += chunk_transcript + " "

                                                        # Remove the temporary chunk file
                                                        os.remove(chunk_filename)

                                                    return complete_transcript

                                                except Exception as e:
                                                    st.error(f"Error processing audio chunks: {e}")
                                                    return ""
                                     
                                            submission_text = transcribe_audio_chunks(audio_path)
        
                                            # Clean up temporary files
                                            os.remove(video_path)
                                            os.remove(audio_path)
        
                                        except Exception as e:
                                            st.error(f"Error processing video: {e}")
                                            continue
                                    else:
                                        st.error("Invalid file type. Only .txt, .mp4, .avi, and .mov files are allowed.")
                                        continue
                                    if(vid== True):
                                         evaluation_prompt = f"This submission is a transcript of the video file provided by the user. Evaluate this submission based on the observation sheet: {task_info['observation_sheet']}. Submission Text:\n{submission_text}"
                                    else: 
                                        evaluation_prompt = f"This is the .txt file submitted by the user. Evaluate this submission based on the observation sheet: {task_info['observation_sheet']}. Submission Text:\n{submission_text}"
                                   
                                    eval_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                                        "model": "llama-3.3-70b-versatile",
                                        "messages": [{"role": "user", "content": evaluation_prompt}],
                                        "max_tokens": 700
                                    }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})
                                    evaluation_result = eval_response.json()["choices"][0]["message"]["content"]
        
                                    if email not in submissions:
                                        submissions[email] = []
                                    submissions[email].append({"task": task_info["task"], "evaluation": evaluation_result})
                                    save_json(SUBMISSIONS_FILE, submissions)
        
                                    send_email(INVIGILATORS[task_info['invigilator']]["email"], "Evaluation Results", evaluation_result)
                                    st.success("Submission evaluated and saved!")
elif page == "Invigilator Dashboard":
    st.header("Invigilator Dashboard")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login as Invigilator"):
        if any(inv["email"] == email and inv["password"] == password for inv in INVIGILATORS.values()):
            st.session_state["invigilator"] = email
            st.success("Invigilator logged in!")
        else:
            st.error("Invalid invigilator credentials")

    if "invigilator" in st.session_state:
        st.subheader("Submitted Tasks")
        import hashlib
        for user_email, tasks in submissions.items():
            for idx, task_info in enumerate(tasks):  # Add index
                task_hash = hashlib.md5(task_info['task'].encode()).hexdigest()[:8]  # Unique task hash
                button_key = f"certify_{user_email}_{task_hash}_{idx}"  # Ensure uniqueness
                
                with st.expander(f"User: {user_email}, Task: {task_info['task'][:50]}..."):
                    st.write(f"Task: {task_info['task']}")
                    st.write(f"Evaluation Result: {task_info['evaluation']}")

                    if st.button("Generate Certificate", key=button_key):  # Use unique key
                        cert_prompt = f"Generate a professional certification document for {user_email} for completing the task: {task_info['task']}."
                        cert_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [{"role": "user", "content": cert_prompt}],
                            "max_tokens": 700
                        }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})

                        certificate = cert_response.json()["choices"][0]["message"]["content"]
                        send_email(user_email, "Certification Achieved!", certificate)
                        st.success("Certificate sent to user!")

elif page == "Pending Tasks":
    st.header("Pending Tasks")

    # User Login Section
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login as User"):
        if email in USERS and USERS[email] == password:
            st.session_state["user"] = email
            st.success("User logged in!")
        else:
            st.error("Invalid credentials")

    # Show Pending Tasks if Logged In
    if "user" in st.session_state:
        email = st.session_state["user"]
        st.subheader(f"Pending Tasks for {email}")

        if email in pending_tasks and pending_tasks[email]:
            for task_info in pending_tasks[email]:
                with st.expander(f"Task: {task_info['task'][:50]}..."):
                    st.write(task_info["task"])
                    uploaded_file = st.file_uploader("Upload Code/Video Submission", type=["txt", "mp4", "avi", "mov"], key=f"submission_{task_info['task']}")

                    if uploaded_file:
                        vid1=False
                        with st.spinner("Evaluating submission..."):
                            file_type = uploaded_file.type
                            if file_type == "text/plain":
                                submission_text = uploaded_file.read().decode()
                            elif file_type.startswith("video/"):
                                vid1=True
                                submission_text = ""
                                try:
                                    from moviepy.editor import VideoFileClip  # type: ignore
                                    video_path = "temp_video." + uploaded_file.name.split(".")[-1]
                                    with open(video_path, "wb") as f:
                                        f.write(uploaded_file.read())

                                    video_clip = VideoFileClip(video_path)
                                    audio_path = "temp_audio.wav"
                                    audio_clip = video_clip.audio
                                    audio_clip.write_audiofile(audio_path)
                                    audio_clip.close()
                                    video_clip.close()

                                    # Transcribe audio with Deepgram
                                    # Transcribe audio 
                                    import speech_recognition as sr
                                    def transcribe_audio_chunks(audio_path):
                                        try:
                                            from pydub import AudioSegment
                                            import speech_recognition as sr
                                            import os

                                            # Load audio file
                                            audio = AudioSegment.from_wav(audio_path)

                                            # Set chunk length (in milliseconds)
                                            chunk_length_ms = 15000

                                            # Get the number of chunks
                                            num_chunks = len(audio) // chunk_length_ms

                                            # Initialize the complete transcript
                                            complete_transcript = ""

                                            # Iterate through the chunks
                                            for i in range(num_chunks):
                                                start = i * chunk_length_ms
                                                end = (i + 1) * chunk_length_ms
                                                chunk = audio[start:end]

                                                # Export the chunk to a temporary file
                                                chunk_filename = f"temp_chunk_{i}.wav"
                                                chunk.export(chunk_filename, format="wav")

                                                # Transcribe the chunk
                                                recognizer = sr.Recognizer()
                                                recognizer.energy_threshold = 150
                                                with sr.AudioFile(chunk_filename) as source:
                                                    audio_data = recognizer.record(source)
                                                    try:
                                                        text = recognizer.recognize_google(audio_data, language="en-US")
                                                        chunk_transcript = text
                                                    except sr.UnknownValueError:
                                                        chunk_transcript = ""
                                                    except sr.RequestError as e:
                                                        chunk_transcript = ""

                                                # Append the chunk transcript to the complete transcript
                                                complete_transcript += chunk_transcript + " "

                                                # Remove the temporary chunk file
                                                os.remove(chunk_filename)

                                            return complete_transcript

                                        except Exception as e:
                                            st.error(f"Error processing audio chunks: {e}")
                                            return ""
                                     
                                    submission_text = transcribe_audio_chunks(audio_path)

                                    os.remove(video_path)
                                    os.remove(audio_path)

                                except Exception as e:
                                    st.error(f"Error processing video: {e}")
                                    continue
                            else:
                                st.error("Invalid file type. Only .txt, .mp4, .avi, and .mov files are allowed.")
                                continue

                            # AI Evaluation
                            if(vid1==True):
                                 evaluation_prompt = f"This is a transcript of the video file submitted by the user. If the task is completely incorrect begin your evaluation result by saying Score: 0/100. Give 0 only if the user uploaded something of other topic. If it is similar and the user has tried then give atleast 5 marks. Evaluate this submission based on the observation sheet: {task_info['observation_sheet']}. Submission Text:\n{submission_text}"
                            else:
                                evaluation_prompt = f"This is a .txt file submitted by the user. f the task is completely incorrect begin your evaluation result by saying Score: 0/100. Give 0 only if the user uploaded something of other topic. If it is similar and the user has tried then give atleast 5 marks. Evaluate this submission based on the observation sheet: {task_info['observation_sheet']}. Submission Text:\n{submission_text}"

                            eval_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                                "model": "llama-3.3-70b-versatile",
                                "messages": [{"role": "user", "content": evaluation_prompt}],
                                "max_tokens": 700
                            }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})
                            evaluation_result = eval_response.json()["choices"][0]["message"]["content"]
                            import re
                            match = re.search(r"Score: 0/100", evaluation_result)
                            if match:
                                score = 0
                            else:
                                score = 6

                            if 0 <= score <= 5:
                                st.error("poor/wrong submission, try again")
                            else:
                                if email not in submissions:
                                    submissions[email] = []
                                submissions[email].append({"task": task_info["task"], "evaluation": evaluation_result})
                                save_json(SUBMISSIONS_FILE, submissions)

                                send_email(INVIGILATORS[task_info["invigilator"]]["email"], "Evaluation Results", evaluation_result)
                                pending_tasks[email].remove(task_info)
                                save_json(TASKS_FILE, pending_tasks)
                                st.success("Task evaluated!")
    else:
        st.info("No pending tasks found.")

elif page == "Invigilator Dashboard":
    st.header("Invigilator Dashboard")
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login as Invigilator"):
        if any(inv["email"] == email and inv["password"] == password for inv in INVIGILATORS.values()):
            st.session_state["invigilator"] = email
            st.success("Invigilator logged in!")
        else:
            st.error("Invalid invigilator credentials")

    if "invigilator" in st.session_state:
        st.subheader("Submitted Tasks")
        import hashlib
        for user_email, tasks in submissions.items():
            for idx, task_info in enumerate(tasks):  # Add index
                task_hash = hashlib.md5(task_info['task'].encode()).hexdigest()[:8]  # Unique task hash
                button_key = f"certify_{user_email}_{task_hash}_{idx}"  # Ensure uniqueness
                
                with st.expander(f"User: {user_email}, Task: {task_info['task'][:50]}..."):
                    st.write(f"Task: {task_info['task']}")
                    st.write(f"Evaluation Result: {task_info['evaluation']}")

                    if st.button("Generate Certificate", key=button_key):  # Use unique key
                        cert_prompt = f"Generate a professional certification document for {user_email} for completing the task: {task_info['task']}."
                        cert_response = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                            "model": "llama-3.3-70b-versatile",
                            "messages": [{"role": "user", "content": cert_prompt}],
                            "max_tokens": 700
                        }, headers={"Authorization": f"Bearer {GROQ_API}", "Content-Type": "application/json"})

                        certificate = cert_response.json()["choices"][0]["message"]["content"]
                        send_email(user_email, "Certification Achieved!", certificate)
                        st.success("Certificate sent to user!")

elif page == "Pending Tasks":
    st.header("Pending Tasks")
    
    # User Login Section
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login as User"):
        if email in USERS and USERS[email] == password:
            st.session_state["user"] = email
            st.success("User logged in!")
    

elif page == "Test Results":
    st.header("Test Results")
    TEST_RESULTS_FILE = "test_results.json"
    test_results = load_json(TEST_RESULTS_FILE)
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login as User"):
        if email in USERS and USERS[email] == password:
            st.session_state["user"] = email
            st.success("User logged in!")
        else:
            st.error("Invalid credentials")

    if "user" in st.session_state:
        email = st.session_state["user"]
        st.subheader(f"Test Results for {email}")

        if email in test_results and test_results[email]:
            import matplotlib.pyplot as plt

            scores = []
            dates = []

            for test in test_results[email]:
                # Generate a unique hash for each test entry
                test_hash = hashlib.md5(f"{test['skill']}_{test['date']}".encode()).hexdigest()[:8]

                st.write(f"**Skill:** {test['skill']}")
                st.write(f"**Date:** {test['date']}")
                st.write(f"**Score:** {test['score']}/10")
                st.write("**Feedback:**")

                # Assign a unique key to each text_area
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
        else:
            st.info("No test results found.")
