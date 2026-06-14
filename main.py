from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from flask import Flask, render_template, request, send_file
import os
import pdfplumber
import sqlite3
import json
from chart_generator import create_chart
from flask import session, redirect, url_for
from flask_bcrypt import Bcrypt

from skill_bank import skills
from career_bank import career_rules
from gap_analyzer import find_skill_gaps
from score_calculator import calculate_scores
from roadmap_bank import roadmaps
from report_generator import create_report

app = Flask(
    __name__,
    template_folder="web_pages",
    static_folder="assets"
)
app.secret_key = "careercompass_secret_key"
bcrypt = Bcrypt(app)
latest_filename = ""
latest_skills = []
latest_careers = []
latest_scores = {}
latest_gaps = {}
latest_roadmaps = {}
UPLOAD_FOLDER = "uploaded_docs"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Reports table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            skills TEXT,
            careers TEXT,
            scores TEXT,
            gaps TEXT,
            roadmaps TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()

            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (username, hashed_pw))

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            return "User already exists"

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()

        if user and bcrypt.check_password_hash(user[0], password):
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/")
def home():
    if "user" not in session:
        return redirect ("/login")
    return render_template(
        "home.html",
        filename="",
        skills=[],
        careers=[],
        gaps={},
        scores={},
        roadmaps={}
    )


@app.route("/upload", methods=["POST"])
def upload():

    resume = request.files["resume"]

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(file_path)

    # Read PDF
    text = ""

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

    text = text.lower()

    # Detect Skills
    detected_skills = []

    for skill in skills:

        if skill.lower() in text:
            detected_skills.append(skill)

    detected_skills = list(set(detected_skills))

    # Career Recommendation
    recommended_careers = []

    for career, required_skills in career_rules.items():

        matches = 0

        for skill in required_skills:

            if skill in detected_skills:
                matches += 1

        if matches >= 2:
            recommended_careers.append(career)

    # Skill Gap Analysis
    skill_gaps = find_skill_gaps(
        detected_skills,
        career_rules
    )

    # Career Readiness Score
    career_scores = calculate_scores(
        detected_skills,
        career_rules
    )
    create_chart(career_scores)
    if "user" in session:

     conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO user_reports
        (
            username,
            filename,
            skills,
            careers,
            scores,
            gaps,
            roadmaps
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        session["user"],
        resume.filename,
        json.dumps(detected_skills),
        json.dumps(recommended_careers),
        json.dumps(career_scores),
        json.dumps(skill_gaps),
        json.dumps({})
    ))

    conn.commit()
    conn.close()

    # Learning Roadmaps
    recommended_roadmaps = {}

    for career in recommended_careers:

        if career in roadmaps:
            recommended_roadmaps[career] = roadmaps[career]
            global latest_filename
            global latest_skills
            global latest_careers
            global latest_scores
            global latest_gaps
            global latest_roadmaps

            latest_filename = resume.filename
            latest_skills = detected_skills
            latest_careers = recommended_careers
            latest_scores = career_scores
            latest_gaps = skill_gaps
            latest_roadmaps = recommended_roadmaps

    return render_template(
        "home.html",
        filename=resume.filename,
        skills=detected_skills,
        careers=recommended_careers,
        gaps=skill_gaps,
        scores=career_scores,
        roadmaps=recommended_roadmaps
    )

@app.route("/download_report")
def download_report():

    pdf_file = create_report(
        latest_filename,
        latest_skills,
        latest_careers,
        latest_scores,
        latest_gaps,
        latest_roadmaps
    )

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route("/my_reports")
def my_reports():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        SELECT filename, timestamp
        FROM user_reports
        WHERE username = ?
        ORDER BY id DESC
    """, (session["user"],))

    reports = c.fetchall()

    conn.close()

    return render_template(
        "my_reports.html",
        reports=reports
    )
if __name__ == "__main__":
    app.run(debug=True)