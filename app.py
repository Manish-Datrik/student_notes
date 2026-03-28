from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.secret_key = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
db = SQLAlchemy(app)

WEATHER_API_KEY = '7bf1dcc5ff751c472ad5d870f04e9699'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    user_id = db.Column(db.Integer)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/index')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['user_id'] = user.id
            return redirect('/index')
        error = "Login failed"
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if User.query.filter_by(username=u).first():
            error = "Username exists"
        else:
            new_user = User(username=u, password=p)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect('/index')
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        t = request.form.get('title')
        c = request.form.get('content')
        if t and c:
            new_note = Note(title=t, content=c, user_id=session['user_id'])
            db.session.add(new_note)
            db.session.commit()
            return redirect('/index')
    notes = Note.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', notes=notes)

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('about.html')

@app.route('/weather')
def get_weather():
    try:
        city = request.args.get('city', 'New York')
        if WEATHER_API_KEY == 'YOUR_API_KEY_HERE':
            return jsonify({'error': 'Weather API key not configured'}), 400
        
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                'city': data['name'],
                'temp': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure']
            }
            return jsonify(weather_info)
        else:
            return jsonify({'error': 'City not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
