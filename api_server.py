from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from test_manager import save_test_result, handle_test_completion
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
    flask_app.run(port=8501)

# Start Flask server in background
threading.Thread(target=run_flask, daemon=True).start()
