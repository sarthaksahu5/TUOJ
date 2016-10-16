from flask import Flask, flash, redirect, render_template, request, session, abort
from sqlalchemy.orm import sessionmaker
from Project import Register, Base
from sqlalchemy import create_engine
import os
import bcrypt

engine = create_engine('sqlite:///C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\tuoj.db')
app = Flask(__name__)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return "Hello " + session['user'] + "!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():

    POST_USERNAME = request.form['username']
    POST_PASSWORD = request.form['password']

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(Register).filter(Register.user_name.in_([POST_USERNAME])).first()

    if( query ):
        if bcrypt.hashpw(POST_PASSWORD.encode('utf-8'), query.password) == query.password:
            session['logged_in'] = True
            session['user'] = POST_USERNAME
        else:
            flash('Wrong Password')

    return home()

@app.route('/register', methods=['POST'])
def register():

    POST_USERNAME = request.form['username']
    POST_ROLLNO   = request.form['rollno']
    POST_FNAME    = request.form['fname']
    POST_LNAME    = request.form['lname']
    POST_COLLEGE  = request.form['college']
    POST_EMAIL    = request.form['email']
    POST_PASSWORD = request.form['password']

    Session = sessionmaker(bind=engine)
    s = Session()

    register = Register(POST_USERNAME, POST_ROLLNO, POST_FNAME, POST_LNAME, POST_COLLEGE, POST_EMAIL, POST_PASSWORD.encode('utf-8'))
    s.add(register)

    s.commit()

    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
