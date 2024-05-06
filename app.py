import requests
from flask import Flask, request, jsonify, make_response, redirect, url_for
from bs4 import BeautifulSoup
from transformers import pipeline
from functools import wraps

app = Flask(__name__)

# Define user credentials
users = {
    "admin": "password",
    "user1": "123456"
}

# Function to verify if the user is logged in
def is_authenticated(request):
    session_cookie = request.cookies.get('session')
    return session_cookie in users

# Decorator to protect routes that require authentication
def require_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(request):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth and auth.username in users and auth.password == users[auth.username]:
        # Create a session cookie upon successful login
        response = make_response(redirect(url_for('get_ans')))
        response.set_cookie('session', auth.username)
        return response
    else:
        return jsonify({"error": "Invalid username or password"}), 401

# Answer route (requires authentication)
@app.route('/answer', methods=['POST'])
@require_authentication
def get_ans():
    request_data = request.get_json()
    if not request_data or 'url' not in request_data or 'question' not in request_data:
        return jsonify({"error": "Invalid request. 'url' and 'question' fields are required."}), 400
   
    url = request_data['url']
    question = request_data['question']

    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch webpage: {e}"}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    relevant_text = text[:5000] 

    try:
        nlp = pipeline("question-answering")
        answer = nlp(question=question, context=relevant_text)
    except Exception as e:
        return jsonify({"error": f"Error processing question: {e}"}), 500

    if answer['score'] > 0.5: 
        return jsonify({"answer": answer['answer']}), 200
    else:
        return jsonify({"answer": "I don’t know the answer"}), 200

if __name__ == '__main__':
    app.run(debug=True)
