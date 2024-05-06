from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import openai

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {
    "admin": "password"
}

openai.api_key = 'your_openai_api_key'

def is_authenticated():
    return session.get('logged_in')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            return redirect(url_for('generate_text'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/generate_text', methods=['POST'])
def generate_text():
    if not is_authenticated():
        return 'Unauthorized', 401

    data = request.get_json()
    topic = data.get('topic')
    format = data.get('format')

    prompt = f"Generate a {format} about {topic}."
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150
    )
    generated_text = response.choices[0].text.strip()

    return jsonify({'text': generated_text})

if __name__ == '__main__':
    app.run(debug=True)
