from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from sqlalchemy.orm import sessionmaker
from Project import Register, Base
from sqlalchemy import create_engine
import os
import bcrypt
from werkzeug import secure_filename

engine = create_engine('sqlite:///C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\tuoj.db')
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'css/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'db'])
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/problems')
def problems():
    return render_template('Problem.html', value = False)

@app.route('/upload')
def index():
    if not session.get('logged_in'):
        return render_template('error.html')
    else:
        user = session['user']
        if user == 'admin' :
            return render_template('upload.html')
        else:
            return render_template('error.html')

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html', value = False)
    else:
        return render_template('index.html', value = True, user = session['user'] )

@app.route('/login', methods=['POST'])
def do_admin_login():

    POST_USERNAME = str(request.form['username'])
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

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))
    else:
        flash('file format not supported')
        return url_for('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
