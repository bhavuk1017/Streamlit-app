# Certification Platform

A modular Streamlit application for managing certifications, tests, and tasks.

## Project Structure

- `app.py` - Main Streamlit application entry point
- `config.py` - Configuration settings and constants
- `utils.py` - General utility functions
- `email_service.py` - Email handling functionality
- `video_processor.py` - Video processing and transcription
- `auth.py` - User and invigilator authentication
- `test_manager.py` - Test generation and evaluation
- `task_manager.py` - Task management and submission handling

## Features

- User and invigilator authentication
- Test generation and evaluation
- Task assignment and submission
- Video submission processing (optional)
- Email notifications
- Test results visualization
- Certificate generation

## Required Files

- `credentials.json` - Google API credentials
- `token.json` - Google OAuth token
- `tasks.json` - Stores pending tasks
- `submissions.json` - Stores task submissions
- `test_results.json` - Stores test results

## Dependencies

### Core Dependencies
```bash
streamlit>=1.10.0
google-auth>=2.6.0
google-auth-oauthlib>=0.4.6
google-auth-httplib2>=0.1.0
google-api-python-client>=2.47.0
matplotlib>=3.5.2
requests>=2.28.0
python-dotenv>=0.20.0
```

### Optional Dependencies (for video processing)
```bash
moviepy>=1.0.3
pydub>=0.25.1
SpeechRecognition>=3.8.1
```

## Installation

1. Install core dependencies:
```bash
pip install streamlit google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client matplotlib requests python-dotenv
```

2. (Optional) Install video processing dependencies:
```bash
pip install moviepy pydub SpeechRecognition
```

3. Set up Google API credentials and OAuth token

4. Run the application:
```bash
streamlit run app.py
```

## Modules Description

### config.py
- Stores API keys, user credentials, and file paths
- Defines available skills and constant values

### utils.py
- JSON file handling functions
- AI response generation using GROQ API

### email_service.py
- Gmail API integration
- Email sending functionality for various purposes

### video_processor.py
- Video file processing (requires optional dependencies)
- Audio extraction and transcription
- Graceful fallback to text-only submissions when dependencies are missing

### auth.py
- User authentication
- Invigilator authentication
- Session management

### test_manager.py
- Test generation using AI
- Test evaluation and scoring
- Results tracking and visualization

### task_manager.py
- Task generation and assignment
- Submission handling and evaluation
- Progress tracking

### app.py
- Main application interface
- Page routing and navigation
- UI components and user interaction

## Note on Video Processing

Video submission processing is an optional feature that requires additional dependencies (`moviepy`, `pydub`, `SpeechRecognition`). If these packages are not installed:
- The system will continue to work with text submissions
- Users will be notified when attempting video uploads
- Clear instructions will be provided for enabling video processing