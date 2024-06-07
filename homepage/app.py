from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
import mysql.connector
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# MySQL configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nature",
    database="test"
)

@app.route('/analysis')
def analysis():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT rating, COUNT(*) as count FROM feedback GROUP BY rating")
    data = cursor.fetchall()
    cursor.close()
    
    labels = [item['rating'] for item in data]
    values = [item['count'] for item in data]
    
    feedback_data = {
        'labels': labels,
        'values': values
    }
    
    return render_template('analysis.html', feedback_data=feedback_data)

@app.route('/submit_feedback', methods=[ 'POST', 'GET'])
def submit_feedback():
    if request.method == 'POST':
        username = request.form['username']
        user_type = request.form['user_type']
        district = request.form['district']
        police_station = request.form['police_station']
        feedback = request.form['feedback']
        rating = request.form['rating']
    
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO feedback (username, user_type, district, police_station, feedback, rating)
            VALUES (%s, %s, %s, %s ,%s, %s)
        """, (username, user_type, district, police_station, feedback, rating))
        db.commit()
        cursor.close()
    
        flash('Feedback submitted successfully!')
        return redirect(url_for('submit_feedback'))
    else:
        return render_template('feedback.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
    
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('login'))
        
        else:
            flash('Invalid username or password')
            return redirect(url_for('analysis'))
    else:
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return f"Welcome, User ID: {session['user_id']}"
    else:
        return redirect(url_for('index'))

@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/register',  methods=['POST', 'GET'] )
def register():
    if request.method == 'POST':
        username = request.form['username']
        email= request.form['email']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, password))
        db.commit()
        cursor.close()
    
        flash('Registered successfully!')
        return redirect(url_for('register'))
    else:
        return render_template('registration.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
