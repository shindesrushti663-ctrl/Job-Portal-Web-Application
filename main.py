from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "home"


# -----------------------
# DATABASE MODELS
# -----------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    category = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    description = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------
# HOME PAGE
# -----------------------

@app.route("/")
def home():

    location = request.args.get("location")
    category = request.args.get("category")
    company = request.args.get("company")

    jobs = Job.query

    if location:
        jobs = jobs.filter(Job.location.contains(location))

    if category:
        jobs = jobs.filter(Job.category.contains(category))

    if company:
        jobs = jobs.filter(Job.company.contains(company))

    jobs = jobs.all()

    return render_template("index.html", jobs=jobs)


# -----------------------
# REGISTER USER
# -----------------------

@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    # CHECK IF USER EXISTS
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return "Username already exists. Please choose another."

    hashed_password = generate_password_hash(password)

    user = User(
        username=username,
        password=hashed_password,
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return redirect("/")


# -----------------------
# LOGIN USER
# -----------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)

    return redirect("/")


# -----------------------
# LOGOUT
# -----------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")


# -----------------------
# POST JOB
# -----------------------

@app.route("/post_job", methods=["POST"])
@login_required
def post_job():

    job = Job(
        title=request.form["title"],
        company=request.form["company"],
        location=request.form["location"],
        category=request.form["category"],
        salary=request.form["salary"],
        description=request.form["description"]
    )

    db.session.add(job)
    db.session.commit()

    return redirect("/")


# -----------------------
# APPLY JOB
# -----------------------

@app.route("/apply/<int:job_id>")
@login_required
def apply(job_id):

    job = Job.query.get(job_id)

    if not job:
        return "Job not found"

    return f"You applied for {job.title} at {job.company}"


# -----------------------
# AI MATCH ANALYZER
# -----------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.json

    job_desc = data.get("job_description")
    skills = data.get("user_skills")

    result = f"""
Match Analysis

Skills Provided:
{skills}

Job Requirement:
{job_desc[:200]}

Estimated Match: 75%

Suggestion:
Improve skills related to the job requirements.
"""

    return jsonify({"result": result})


# -----------------------
# CREATE DATABASE + RUN
# -----------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)