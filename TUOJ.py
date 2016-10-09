from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("main.html")


@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/login/', methods=["GET", "POST"])
def login_page():
    return render_template("login.html")


if __name__ == "__main__":
    app.run()