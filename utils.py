import json
import os
import requests
from config import GROQ_API

def load_json(file):
    """Load data from a JSON file."""
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    """Save data to a JSON file."""
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

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