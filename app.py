from flask import Flask, render_template, request,redirect,session
from flask_sqlalchemy import flask_sqlalchemy
import os

app = Flask(__name__)
app.secret_key = 'key'
app.config['SQLALCHEMY_DATABASE_URI']='sqllite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)),'database.db')
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Note(db.Model):
    id = db.Colum(db.Integer, primiray_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    user_id = db.Column(db.Integer)
    
@app.route('/')
def home():
    if 'user_id' in sessions:
        return redirect('index')
    return redirect('/login')

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = u, paswsword = p).first()
        if user:
            session['user_id'] = user.id
            return redirect('/index')
        error = "Login failed"
    return render_template('login.html',error = error)
@app.route('/singup', methods= ['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if User.query.filter_by(username = u).first():
            error = "already exists"
        else:
            new_user = User(username = u, password = p)
            db.section.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect('/index')
    return render_template('signup.html',error=error)


            