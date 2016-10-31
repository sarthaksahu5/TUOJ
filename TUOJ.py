from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from sqlalchemy.orm import sessionmaker
from models import Register, Problem, Base
from sqlalchemy import create_engine
import os, time, bcrypt
from werkzeug import secure_filename

engine = create_engine('sqlite:///C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\tuoj.db')
app = Flask(__name__)

Session = sessionmaker(bind=engine)
s = Session()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'Input/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'java', 'py'])
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/problems')
def problems():
    if session.get('logged_in'):
        value = True
        user = session['user']
    else:
        value = False
        user = None

    return render_template('Problem.html',problems = s.query(Problem).all(), user = user, value = value)

@app.route('/upload')
def index():
    if not session.get('logged_in'):
        return render_template('error.html')
    else:
        user = session['user']
        if user == 'admin' :
            return render_template('upload.html', user = 'admin', value = True)
        else:
            return render_template('error.html')

@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html', user = session['user'], value = True, profile = s.query(Register).filter_by(user_name = session['user']).first())

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

    register = Register(POST_USERNAME, POST_ROLLNO, POST_FNAME, POST_LNAME, POST_COLLEGE, POST_EMAIL, POST_PASSWORD.encode('utf-8'))
    s.add(register)

    s.commit()

    return home()

'''@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(request.form['problem_id'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))
    else:
        flash('file format not supported')
        return url_for('index.html')'''

@app.route('/uploads', methods=['GET', 'POST'])
def upload():

    if not session.get('logged_in'):
        return render_template('error.html')

    else:
        if session['user'] == 'admin':
            if request.method == 'GET':
                return render_template('uploads.html', user = session['user'], value = True)
            if request.method =='POST':
                problem_id = request.form['id']
                problem_name = request.form['problem_name']
                difficulty = request.form['difficulty']
                content = request.form['content']
                tags = request.form['tags']

                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['problem_name']+'_input.txt'))

                file = request.files['file1']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['problem_name']+'_output.txt'))

                problem = Problem(problem_id, problem_name, difficulty, content, tags)
                s.add(problem)
                s.commit()

                return home()

        else:
            return home()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/problem/<name>/', methods=['GET', 'POST'])
def problem(name):
    if request.method == 'GET':

        if session.get('logged_in'):
            value = True
            user = session['user']
        else:
            value = False
            user = None
        return render_template('problems.html', problem = s.query(Problem).filter_by(problem_name = name).first(), value = value, user = user)

    if request.method == 'POST':

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        os.chdir('C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\Input')

        a = os.system('javac Main.java')
        print(a)
        start_time = time.time()
        b = os.system('java Main > wow.txt')
        print(b)

        '''file1 = name
        os.system('java '+file1+' < wow.txt')'''

        file2 = name+'_input.txt'

        val = os.system('fc wow.txt ' +file2)

        if val:
            return home()
        else:
            return problems()

'''@app.route('/profile/<username>/manage/', methods=['GET', 'POST'])
def manage_profile(username):
    if request.method == 'GET':
        if session.get('logged_in'):
            return render_template('manage_profile.html', value = True, user = session['user'])
        else:
            return home()
    else:
'''


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
