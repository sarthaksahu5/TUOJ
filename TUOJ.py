from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from sqlalchemy.orm import sessionmaker
import os, time, bcrypt
from sqlalchemy import *
from werkzeug import secure_filename
from MySQLdb import escape_string as thwart
from models import *
import gc
import MySQLdb

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'Input/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'java', 'py', 'cpp'])
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

'''###############################################################
            UTILITY FUNCTIONS
###############################################################'''


def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="localhost8000",
                           db="tuoj")
    c = conn.cursor()

    return c, conn


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


'''###############################################################
            DEALING WITH ERROR HANDLING
###############################################################'''


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


'''############################################################
      DEALING WITH USER MODEL-REGISTRATION,LOGIN,LOGOUT
#############################################################'''


@app.route('/profile/<username>')
def profile(username):
    if session.get('logged_in'):
        try:
            # Connection to the database
            c, conn = connection()
            #retrieving the data from register table and the profile table
            c.execute("SELECT * FROM register where user_name = '{0}'".format(session['user']))
            register_obj = c.fetchone()
            c.execute("SELECT * FROM profile where user_name = '{0}'".format(session['user']))
            profile_obj = c.fetchone()

            total = profile_obj[6]+profile_obj[5]+profile_obj[4]+profile_obj[3]+profile_obj[2]
            print(total)
            if total == 0:
                total = 1
            c.close()
            conn.close()
            gc.collect()
            return render_template('profile.html', user = session['user'], value = True, register_obj = register_obj, profile_obj = profile_obj, total = total)
        
        except Exception as e:
            return "Hi ! " + str(e)
    else:
        return render_template('index.html', value = False)

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
    try:
        # Connection to the database
        c, conn = connection()
        # Checking for record in database
        x = c.execute("SELECT * FROM register where user_name = '{0}'".format(POST_USERNAME))
        data = c.fetchone()[6]
        if int(x) > 0:
            if bcrypt.hashpw(POST_PASSWORD.encode('utf-8'), data) == data:
                session['logged_in'] = True
                session['user'] = POST_USERNAME
                flash("You are now Logged In !")
            else:
                flash('Wrong Password')
        c.close()
        conn.close()
        gc.collect()
        return home()
    except Exception as e:
        return "Hi ! " + str(e)

@app.route('/register', methods=['POST'])
def register():
    try:
        POST_USERNAME = request.form['username']
        POST_ROLLNO = request.form['rollno']
        POST_FNAME = request.form['fname']
        POST_LNAME = request.form['lname']
        POST_COLLEGE = request.form['college']
        POST_EMAIL = request.form['email']
        POST_PASSWORD = request.form['password']

        # Connection to the database
        c, conn = connection()

        # Making the password a hash
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(POST_PASSWORD, salt)

        # Checking for already existing record in database
        x = c.execute("SELECT * FROM register where user_name = '{0}'".format(POST_USERNAME))
        if int(x) > 0:
            flash("That username is already taken !")
            return home()

        # If the table doesn't contain the record, then put the record into the table.
        else:
            c.execute("INSERT INTO register VALUES ('{0}','{1}', '{2}','{3}','{4}','{5}','{6}')".format(
                          thwart(POST_USERNAME),
                          thwart(POST_ROLLNO),
                          thwart(POST_FNAME),
                          thwart(POST_LNAME),
                          thwart(POST_COLLEGE),
                          thwart(POST_EMAIL),
                          thwart(hashed_pw)
                        )
                    )
            conn.commit()
            # Generate the profile of the user whenever a user registers.
            c.execute("INSERT INTO profile(user_name) VALUES ('{0}')".format(
                          thwart(POST_USERNAME)
                        )
                     )
            conn.commit()
            flash("Thanks For Registering !")
            c.close()
            conn.close()
            gc.collect()
            return home()

    except Exception as e:
        return str(e)


@app.route('/<user_name>/<int:id>')
def submission(user_name, id):

    if session.get('logged_in'):
        try:
            c,conn = connection()
            c.execute("SELECT * FROM submission WHERE submission_no = '{0}'".format(id))
            solution = c.fetchone()
            return render_template('problem_solution.html', value = True, user = session['user'], solution = solution)
        except Exception as e:
            return str(e)

@app.route('/profile/<name>/manage/', methods=['GET', 'POST'])
def manage_profile(name):
    if session.get('logged_in') and name == session['user'] :
        try:
            # Connection to the database
            c, conn = connection()
            # Getting the record from database
            c.execute("SELECT * FROM register where user_name = '{0}'".format(name))
            register_obj = c.fetchone()

            if request.method == 'GET':
                return render_template('manage_profile.html', value = True, user = session['user'], register_obj = register_obj)

            else:
                update_rollno = request.form['roll_no']
                update_fname = request.form['first_name']
                update_lname = request.form['last_name']
                update_college = request.form['college']

                # updating the table in the database
                c.execute("UPDATE register SET roll_no = '{0}',first_name = '{1}',last_name = '{2}',college = '{3}' where user_name = '{4}'".format
                    (
                        thwart(update_rollno),
                        thwart(update_fname),
                        thwart(update_lname),
                        thwart(update_college),
                        name
                    )
                )
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
                return home()
        except Exception as e:
            return str(e)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


'''############################################################################
        DEALING WITH THE PROBLEM MODEL
############################################################################'''


@app.route('/problem/<name>/edit/', methods=['GET', 'POST'])
def edit_question(name):
    if session.get('logged_in'):
        try:
            # Connection to the database
            c, conn = connection()
            c.execute("SELECT * FROM problem where problem_name = '{0}'".format(name))
            problem = c.fetchone() 
            if request.method == 'GET':
                return render_template('edit_question.html', value=True, user=session['user'],
                                       problem=problem)
            if request.method == 'POST':

                update_pname = request.form['problem_name']
                update_pdifficulty = request.form['difficulty']
                update_pcontent = request.form['content']
                update_ptags = request.form['tags']

                c.execute("UPDATE problem SET problem_name = '{0}', difficulty = '{1}', content = '{2}', tags = '{3}' where problem_name = '{4}'".format
                    (
                        thwart(update_pname),
                        thwart(update_pdifficulty),
                        thwart(update_pcontent),
                        thwart(update_ptags),
                        name
                    )
                )
                conn.commit()
                c.close()
                conn.close()

                app.config['ALLOWED_EXTENSIONS'] = {'txt'}
                if request.files['file'].filename != '':
                    file = request.files['file']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id'] + '_input.txt'))

                if request.files['file1'].filename != '':
                    file = request.files['file1']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id'] + '_output.txt'))

                return problems()

        except Exception as e:
            return str(e)


@app.route('/problem/<name>/delete/', methods=['GET', 'POST'])
def delete_question(name):
    if session.get('logged_in') and session['user'] == 'admin':
        try:
            # Connection to the database
            c, conn = connection()
            c.execute("SELECT * FROM problem where problem_name = '{0}'".format(name))
            problem = c.fetchone()

            if request.method == 'GET':
                return render_template('confirm.html', value=True, user=session['user'], name=name)

            if request.method == 'POST':
                if request.form['choice'] == 'Yes':
                    os.chdir('/home/sarthak/Desktop/TUOJ/Input')
                    file = problem[0]
                    os.system('rm /s ' + file + '_input.txt, ' + file + '_output.txt')
                    c.execute("DELETE problem where problem_name = '{0}'".format(name))
                    conn.commit()

            c.close()
            conn.close()
            gc.collect()
            return problems()

        except Exception as e:
            return str(e)


@app.route('/problems/')
def problems():
    if session.get('logged_in'):
        value = True
        user = session['user']
    else:
        value = False
        user = None
    try:
        # Connection to the database
        c, conn = connection()
        c.execute("SELECT * FROM problem")
        problems = c.fetchall()
        c.close()
        conn.close()
        gc.collect()
        return render_template('Problem.html', problems=problems, user=user, value=value)
    except Exception as e:
        return str(e)

@app.route('/submissions/')
def submissions():
    if session.get('logged_in'):
        try:
            # Connection to the database
            c, conn = connection()
            c = conn.cursor(MySQLdb.cursors.DictCursor)
            c.execute("SELECT * FROM problem, submission where submission.user_name = '{0}' and problem.problem_id = submission.problem_id order by submission.submission_time desc".format(session['user']))
            submissions = c.fetchall()
            c.close()
            conn.close()
            gc.collect()
            return render_template('submission_history.html', submissions=submissions, user=session['user'], value=True)
        except Exception as e:
            return str(e)

@app.route('/upload')
def index():
    if not session.get('logged_in'):
        return render_template('error.html')
    else:
        user = session['user']
        if user == 'admin':
            return render_template('upload.html', user='admin', value=True)
        else:
            return render_template('error.html')


'''##############################################################################
    BACKEND AND UPLOAD HANDLING, TESTING THE PROBLEMS, AND GENERATING THE VERDICT
###############################################################################'''


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return render_template('error.html')

    else:
        if session['user'] == 'admin':
            try:
                # Connection to the database
                c, conn = connection()

                if request.method == 'GET':
                    return render_template('uploads.html', user=session['user'], value=True)
                if request.method == 'POST':
                    problem_id = request.form['id']
                    problem_name = request.form['problem_name']
                    difficulty = request.form['difficulty']
                    content = request.form['content']
                    tags = request.form['tags']

                    app.config['ALLOWED_EXTENSIONS'] = {'txt'}

                    file = request.files['file']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id'] + '_input.txt'))

                    file = request.files['file1']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], request.form['id'] + '_output.txt'))

                    # if problem_id != None and problem_name != None and difficulty != None and content != None:
                    c.execute("INSERT INTO problem(problem_id,problem_name,difficulty,content,tags) VALUES ('{0}','{1}', '{2}','{3}','{4}')".format(
                          thwart(problem_id),
                          thwart(problem_name),
                          thwart(difficulty),
                          thwart(content),
                          thwart(tags)
                        )
                    )
                    conn.commit()
                    c.close()
                    conn.close()
                    gc.collect()
                    return home()
            except Exception as e:
                return str(e)

        else:
            return home()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/problem/<name>/', methods=['GET', 'POST'])
def problem(name):

    try:
        # Connection to the database
        c, conn = connection()
        c.execute("SELECT * FROM problem where problem_name = '{0}'".format(name))
        problem = c.fetchone()
        
        if request.method == 'GET':

            if session.get('logged_in'):
                value = True
                user = session['user']
            else:
                value = False
                user = None
            return render_template('problems.html', problem=problem, value=value, user=user)

        if request.method == 'POST':

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'Main'))

            os.chdir('/home/sarthak/Desktop/TUOJ/Input')
            print(5)
            os.system('mv Main Main.txt')
            file_string = open('Main.txt', 'r').read()

            B = 0
            C = 0
            if ( request.form['language'] == 'C++'):
                os.system('mv Main.txt Main.cpp')
                a = os.system('g++ Main.cpp -o Main')
                if ( a == 0):
                    B = os.system('Main < ' + name + 'input.txt > check.txt')
                    C = os.system('fc ' + name + '_output.txt check.txt')
                os.system('rm Main.cpp, Main.exe, check.txt')

            if ( request.form['language'] == 'Java'):
                os.system('mv Main.txt Main.java')
                a = os.system('javac Main.java')
                if ( a == 0):
                    B = os.system('java Main < ' + name + '_input.txt > check.txt')
                    C = os.system('fc ' + name + '_output.txt check.txt')
                os.system('rm /f Main.java, Main.class, check.txt')

            if ( request.form['language'] == 'Python'):
                os.system('mv Main.txt Main.py')
                a = 0
                B = os.system('python Main.py < ' + name + '_input.txt > check.txt')
                C = os.system('fc ' + name + '_output.txt check.txt')
                os.system('rm /f Main, Main.py, check.txt')

            c.execute("SELECT * FROM profile WHERE user_name = '{0}'".format(session['user']))
            profile = c.fetchone()

            if ( a == 1 ):
                status = 'CTE'
                CTE = profile[2]
                CTE += 1
                c.execute("UPDATE profile set CTE = '{0}' WHERE user_name = '{1}'".format(CTE,session['user']))
                conn.commit()
            else:
                if ( B == 1 ):
                    status = 'RE'
                    RE = profile[2]
                    RE += 1
                    c.execute("UPDATE profile set RE = '{0}' WHERE user_name = '{1}'".format(RE,session['user']))
                    conn.commit()
                else:
                    if ( C == 1 ):
                        status = 'WA'
                        WA = profile[2]
                        WA += 1
                        c.execute("UPDATE profile set WA = '{0}' WHERE user_name = '{1}'".format(WA,session['user']))
                        conn.commit()
                    else:
                        status = 'AC'
                        Correct_Answer = profile[2]
                        Correct_Answer += 1
                        c.execute("UPDATE profile set Correct_Answer = '{0}' WHERE user_name = '{1}'".format(Correct_Answer,session['user']))
                        conn.commit()

            c.execute("INSERT INTO submission(user_name, problem_id, status, language_used, solution) VALUES ('{0}','{1}', '{2}','{3}','{4}')".format(
                          thwart(session['user']),
                          thwart(name),
                          thwart(status),
                          thwart(request.form['language']),
                          thwart(file_string)
                        )
                    )
            conn.commit()
            c.execute("SELECT * FROM problem where problem_id = '{0}'".format(name))
            problem = c.fetchone()
            total_submissions = problem[4]
            total_submissions += 1
            c.execute("UPDATE problem set total_submissions = '{0}'".format(total_submissions))
            conn.commit()
            if ( status == 'AC' ):
                correct_submissions = problem[5]
                correct_submissions += 1
                c.execute("UPDATE problem set correct_submissions = '{0}'".format(correct_submissions))
                conn.commit()
            c.close()
            conn.close()
            gc.collect()
            return render_template('Result.html', a=a, B=B, C=C, value=True, user=session['user'])
    
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
