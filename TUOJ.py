from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from sqlalchemy.orm import sessionmaker
from Project import Register, Problem, Submission, Base
from sqlalchemy import create_engine, and_, desc
import os, time, bcrypt
from werkzeug import secure_filename

engine = create_engine('sqlite:///C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\tuoj.db')
app = Flask(__name__)

Session = sessionmaker(bind=engine)
s = Session()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'Input/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'java', 'py', 'cpp'])
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/problems/')
def problems():
    if session.get('logged_in'):
        value = True
        user = session['user']
    else:
        value = False
        user = None

    return render_template('Problem.html',problems = s.query(Problem).all(), user = user, value = value)

@app.route('/submissions/')
def submissions():
    if session.get('logged_in'):
        return render_template('submission_history.html',submissions = s.query(Problem, Submission).filter(Submission.user_name == session['user']).filter(Problem.problem_id == Submission.problem_id).order_by(desc(Submission.submission_time)), user = session['user'], value = True)

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

                app.config['ALLOWED_EXTENSIONS'] = {'txt'}

                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id']+'_input.txt'))

                file = request.files['file1']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id']+'_output.txt'))

                #if problem_id != None and problem_name != None and difficulty != None and content != None:
                problem = Problem(problem_id, problem_name, difficulty, content, tags)
                s.add(problem)
                s.commit()

                return home()

        else:
            return home()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/problem/<name>/edit/', methods=['GET', 'POST'])
def edit_question(name):
    if session.get('logged_in'):
        if request.method == 'GET':
            return render_template('edit_question.html', value = True, user = session['user'], problem = s.query(Problem).filter_by(problem_name = name).first())
        if request.method == 'POST':
            problem = s.query(Problem).filter_by(problem_name = name).first()

            problem.problem_name = request.form['problem_name']
            problem.difficulty = request.form['difficulty']
            problem.content = request.form['content']
            problem.tags = request.form['tags']

            s.commit()

            app.config['ALLOWED_EXTENSIONS'] = {'txt'}
            if request.files['file'].filename != '':
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id']+'_input.txt'))

            if request.files['file1'].filename != '':
                file = request.files['file1']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id']+'_output.txt'))

            return problems()

@app.route('/problem/<name>/delete/', methods=['GET', 'POST'])
def delete_question(name):

    if session.get('logged_in') and session['user'] == 'admin' :
        if request.method == 'GET':
            return render_template('confirm.html', value = True, user = session['user'], name = name)

        if request.method == 'POST':
            if request.form['choice'] == 'Yes':
                problem = s.query(Problem).filter_by(problem_name = name).first()

                os.chdir('C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\Input')
                file = problem.problem_id
                os.system('del /s '+file+'_input.txt, '+file+'_output.txt')

                s.delete(problem)
                s.commit()

    return problems()

@app.route('/<user_name>/<int:id>')
def submission(user_name, id):

    if session.get('logged_in'):
        return render_template('problem_solution.html', value = True, user = session['user'], solution = s.query(Submission).filter_by(submission_no = id).first())

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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'Main'))

        os.chdir('C:\\Users\\Saurav Verma\\Downloads\\Compressed\\flaskSamples\\6-FlaskLogin\\Input')

        os.system('rename Main Main.txt')
        file_string = open('Main.txt', 'r').read()

        b = 0
        c = 0
        if( request.form['language'] == 'C++'):
            os.system('rename Main.txt Main.cpp')
            a = os.system('g++ Main.cpp -o Main')
            if( a == 0):
                b = os.system('Main < '+name+'_input.txt > check.txt')
                c = os.system('fc '+name+'_output.txt check.txt')
            os.system('del /f Main.cpp, Main.exe, check.txt')

        if( request.form['language'] == 'Java'):
            os.system('rename Main.txt Main.java')
            a = os.system('javac Main.java')
            if( a == 0):
                b = os.system('java Main < '+name+'_input.txt > check.txt')
                c = os.system('fc '+name+'_output.txt check.txt')
            os.system('del /f Main.java, Main.class, check.txt')

        if( request.form['language'] == 'Python'):
            os.system('rename Main.txt Main.py')
            a = 0
            b = os.system('python Main.py < '+name+'_input.txt > check.txt')
            c = os.system('fc '+name+'_output.txt check.txt')
            os.system('del /f Main, Main.py, check.txt')

        if( a==1 ):
            status = 'CTE'
        else:
            if( b==1 ):
                status = 'RE'
            else:
                if( c==1 ):
                    status = 'WA'
                else:
                    status = 'AC'

        submission = Submission(session['user'], name, status, request.form['language'], file_string)
        s.add(submission)
        s.commit()

        problem = s.query(Problem).filter_by(problem_id = name).first()
        problem.total_submissions += 1
        if( status == 'AC' ):
            problem.correct_submissions += 1
        s.commit()

        return render_template('Result.html', a = a, b =b, c = c, value = True, user = session['user'])

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
