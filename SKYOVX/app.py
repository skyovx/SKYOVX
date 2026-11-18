
import os
import hmac
import secrets
from functools import wraps

import requests
from flask import (
    Flask, render_template_string, request,
    redirect, url_for, session, flash, abort
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true"
)

PRV_PASSWORD = os.environ.get("PRV_PASSWORD", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL", "")
GOOGLE_SCRIPT_TOKEN = os.environ.get("GOOGLE_SCRIPT_TOKEN", "")

TIMEOUT = 20

# =====================================================
# SKYOVX TEST - 20 QUESTIONS
# Answers are checked ONLY on the server.
# =====================================================

QUESTIONS = [
    {
        "question": "What is my favorite color?",
        "options": ["Black 🖤", "Red ❤️", "Blue 💙", "White 🤍"],
        "answer": "A"
    },
    {
        "question": "What is my favorite food?",
        "options": ["Pizza 🍕", "Tacos 🌮", "Burger 🍔", "Pasta 🍝"],
        "answer": "C"
    },
    {
        "question": "What is my favorite drink?",
        "options": ["Coffee ☕", "Tea 🍵", "Coca-Cola 🥤", "Juice 🍊"],
        "answer": "A"
    },
    {
        "question": "What is my favorite music genre?",
        "options": [
            "Rap 🎤", "Rock 🎸", "Phonk 🔥",
            "Pop 🎶", "Classical 🎻",
            "No specific genre / Other 🎧"
        ],
        "answer": "F"
    },
    {
        "question": "What is my favorite season?",
        "options": ["Winter ❄️", "Summer ☀️", "Autumn 🍂", "Spring 🌸"],
        "answer": "A"
    },
    {
        "question": "What is my favorite animal?",
        "options": ["Cat 🐈", "Dog 🐕", "Wolf 🐺", "Lion 🦁"],
        "answer": "B"
    },
    {
        "question": "What is my favorite time of the day?",
        "options": ["Morning 🌅", "Afternoon ☀️", "Sunset 🌇", "Late Night 🌃"],
        "answer": "C"
    },
    {
        "question": "Which country would I love to visit?",
        "options": ["Japan 🇯🇵", "USA 🇺🇸", "Switzerland 🇨🇭", "Italy 🇮🇹"],
        "answer": "A"
    },
    {
        "question": "Which field interests me the most?",
        "options": [
            "Web Design 🌐", "Cybersecurity 🔐",
            "Graphic Design 🎨", "Marketing 📈"
        ],
        "answer": "B"
    },
    {
        "question": "Which vehicle do I prefer?",
        "options": [
            "Luxury Cars 🏎️", "Motorcycles 🏍️",
            "Private Jets ✈️", "Regular Cars 🚘"
        ],
        "answer": "B"
    },
    {
        "question": "What is my favorite movie genre?",
        "options": ["Horror 👻", "Action 💥", "Romance ❤️", "Comedy 😂"],
        "answer": "B"
    },
    {
        "question": "What do I prefer doing in my free time?",
        "options": [
            "Playing Games 🎮", "Listening to Music 🎧",
            "Watching Movies & Series 🎬", "Reading 📚"
        ],
        "answer": "C"
    },
    {
        "question": "Which phone brand do I prefer?",
        "options": ["iPhone 🍎", "Samsung 📱", "Google Pixel", "Xiaomi"],
        "answer": "A"
    },
    {
        "question": "What color clothes do I prefer?",
        "options": ["Black 🖤", "White 🤍", "Grey 🩶", "Blue 💙"],
        "answer": "A"
    },
    {
        "question": "Which car brand do I like most?",
        "options": [
            "Mercedes-Benz 🚘", "BMW 🚗",
            "Porsche 🏁", "Ferrari 🔥"
        ],
        "answer": "A"
    },
    {
        "question": "What do I prefer during holidays?",
        "options": [
            "Travel & Discover Places ✈️",
            "Stay Home 🏠",
            "Go Out With Friends 🎉",
            "Gaming & Entertainment 🎮"
        ],
        "answer": "A"
    },
    {
        "question": "What is my favorite video game genre?",
        "options": [
            "Action & Adventure ⚔️",
            "Racing 🏎️", "Football ⚽", "Horror 👻"
        ],
        "answer": "A"
    },
    {
        "question": "What attracts me most in technology?",
        "options": [
            "Hacking & Cybersecurity 🔐",
            "Programming & Coding 💻",
            "Artificial Intelligence 🤖",
            "Building Websites 🌐"
        ],
        "answer": "A"
    },
    {
        "question": "What is my biggest future ambition?",
        "options": [
            "Become Financially Independent 💰",
            "Build My Own Company 🏢",
            "Become Famous 🌟",
            "Travel Around the World 🌍"
        ],
        "answer": "B"
    },
    {
        "question": "What would I like people to remember me for?",
        "options": [
            "My Intelligence 🧠",
            "My Success 🏆",
            "My Personality ❤️",
            "My Creativity & Ideas 💡"
        ],
        "answer": "D"
    }
]

LETTERS = ["A", "B", "C", "D", "E", "F"]


# =====================================================
# GOOGLE SHEETS
# =====================================================

def sheets_request(action, **data):
    if not GOOGLE_SCRIPT_URL or not GOOGLE_SCRIPT_TOKEN:
        raise RuntimeError("Google Sheets configuration missing")

    payload = {
        "action": action,
        "token": GOOGLE_SCRIPT_TOKEN,
        **data
    }

    response = requests.post(
        GOOGLE_SCRIPT_URL,
        json=payload,
        timeout=TIMEOUT
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("success"):
        raise RuntimeError(result.get("error", "Google Sheets error"))

    return result


def save_quiz_result(name, score, answers):
    return sheets_request(
        "save_quiz",
        name=name,
        score=score,
        answers=answers
    )


def get_quiz_results():
    return sheets_request("list_results").get("results", [])


# =====================================================
# SECURITY
# =====================================================

def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = csrf_token


def check_csrf():
    token = request.form.get("csrf_token", "")
    saved = session.get("csrf_token", "")

    if not saved or not hmac.compare_digest(token, saved):
        abort(400, description="Invalid form token")


def private_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("prv_unlocked"):
            return redirect(url_for("home"))
        return function(*args, **kwargs)
    return wrapper


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))
        return function(*args, **kwargs)
    return wrapper


# =====================================================
# DESIGN
# =====================================================

STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
background:#080808;color:white;font-family:Arial,sans-serif;
min-height:100vh;padding:25px 6%;
}
a{color:white;text-decoration:none}
.container{max-width:850px;margin:35px auto}
.logo{
text-align:center;font-size:48px;letter-spacing:10px;
font-weight:bold;text-shadow:0 0 25px #ffffff66
}
.subtitle{
text-align:center;color:#999;margin:12px 0 35px;
letter-spacing:3px;font-size:11px
}
.card{
background:#111;border:1px solid #292929;
border-radius:18px;padding:30px;margin:20px 0;
}
h1,h2,h3{margin-bottom:15px}
p{color:#aaa;line-height:1.8}
.btn{
display:inline-block;padding:14px 24px;border-radius:30px;
background:white;color:black;border:0;font-weight:bold;
cursor:pointer;text-align:center;font-size:13px
}
.btn:hover{background:#ddd}
.btn-outline{background:transparent;color:white;border:1px solid #555}
input{
width:100%;padding:15px;margin:12px 0;
background:#080808;color:white;border:1px solid #383838;
border-radius:10px;font-size:15px
}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
.tile{
background:#171717;border:1px solid #393939;
border-radius:15px;padding:25px;transition:.25s
}
.tile:hover{border-color:white;transform:translateY(-3px)}
.emoji{font-size:35px;margin-bottom:15px}
.badge{
display:inline-block;border:1px solid #555;padding:7px 12px;
border-radius:20px;font-size:10px;letter-spacing:2px;color:#bbb
}
.question{padding:25px 0;border-bottom:1px solid #292929}
.question h3{font-size:16px;line-height:1.6}
.option{
display:block;background:#171717;border:1px solid #333;
padding:15px;border-radius:11px;margin:10px 0;
cursor:pointer;font-size:14px
}
.option:hover{border-color:#aaa;background:#202020}
.option input{width:auto;margin-right:10px;accent-color:white}
.error{color:#ff8585;margin:12px 0}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;margin-top:15px}
td,th{text-align:left;padding:12px;border-bottom:1px solid #333}
footer{text-align:center;color:#666;margin:45px 0 10px;font-size:12px}
@media(max-width:600px){
body{padding:18px 5%}
.grid{grid-template-columns:1fr}
.logo{font-size:34px;letter-spacing:6px}
.card{padding:22px}
}
</style>
"""


# =====================================================
# HOME
# =====================================================

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080808">
<title>SKYOVX | Official</title>
""" + STYLE + """
<style>
header{
display:flex;justify-content:space-between;align-items:center;
padding:10px 4%;border-bottom:1px solid #292929
}
header .logo{font-size:28px}
nav{display:flex;gap:20px}
nav a{color:#aaa;font-size:13px}
.hero{
min-height:75vh;display:flex;flex-direction:column;
justify-content:center;align-items:center;text-align:center;
background:radial-gradient(ellipse at center,#222 0%,#080808 70%);
padding:30px 15px
}
.hero h1{font-size:clamp(55px,12vw,110px);letter-spacing:10px}
.hero h2{margin:15px}
.hero p{max-width:550px;margin:15px auto 25px}
section{padding:65px 5%;max-width:1050px;margin:auto}
.section-title{text-align:center;margin-bottom:30px}
.section-title span{color:#999;letter-spacing:4px;font-size:11px}
.section-title h2{margin-top:12px;font-size:32px}
.about-box,.contact-box{
max-width:750px;margin:auto;text-align:center;
background:#111;border:1px solid #292929;
padding:35px;border-radius:18px
}
.socials{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px}
.social{
background:#111;border:1px solid #292929;
padding:22px;text-align:center;border-radius:12px
}
.social:hover{border-color:white}
.social .icon{display:block;font-weight:bold;font-size:24px;margin-bottom:10px}
@media(max-width:650px){
nav{gap:10px;flex-wrap:wrap;justify-content:center}
header{flex-direction:column;gap:15px}
}
</style>
</head>
<body>

<header>
<div class="logo">SKYOVX</div>
<nav>
<a href="#home">Home</a>
<a href="#about">About</a>
<a href="#room">SKYOVX ROOM</a>
<a href="#socials">Socials</a>
<a href="#contact">Contact</a>
</nav>
</header>

<div class="hero" id="home">
<span class="badge">WELCOME TO MY WORLD</span>
<h1>SKYOVX</h1>
<h2>Independent Soul | Unique Mind</h2>
<p>Not everyone needs to be understood. Some are simply meant to be different. Welcome to my world.</p>
<a href="#room" class="btn">ENTER SKYOVX ROOM</a>
</div>

<section id="about">
<div class="section-title">
<span>BEYOND THE SURFACE</span>
<h2>About Me</h2>
</div>
<div class="about-box">
<p>Just a soul with a different perspective. I believe in individuality, silence, and being true to myself. I don't follow the crowd — I create my own path.</p>
</div>
</section>

<section id="room">
<div class="section-title">
<span>CLASSIFIED PRIVATE SPACE</span>
<h2>SKYOVX ROOM</h2>
</div>

<div class="card" style="max-width:700px;margin:auto;text-align:center">
<div style="font-size:42px">🔒</div>

{% if not unlocked %}
<h3>Enter SKYOVX ROOM</h3>
<p>Enter the access code to discover the private world.</p>
<form method="POST" action="{{ url_for('unlock') }}">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<input type="password" name="password"
placeholder="Enter Access Password" maxlength="100" required>
<button class="btn" type="submit">UNLOCK →</button>
</form>
{% else %}
<h3>WELCOME TO SKYOVX ROOM</h3>
<p>Choose your experience.</p>
<div class="grid" style="margin-top:25px;text-align:left">
<a class="tile" href="{{ url_for('quiz_start') }}">
<div class="emoji">🧠</div>
<h3>THE TEST</h3>
<p>Discover how well you know SKYOVX.</p>
<span class="badge">20 QUESTIONS</span>
</a>

<a class="tile" href="{{ url_for('mystery') }}">
<div class="emoji">🔐</div>
<h3>MYSTERY ROOM</h3>
<p>A mysterious space. Something special is waiting.</p>
<span class="badge">CLASSIFIED</span>
</a>
</div>
<a href="{{ url_for('lock') }}" style="display:block;margin-top:25px;color:#aaa">
LOCK SKYOVX ROOM
</a>
{% endif %}

{% for message in get_flashed_messages() %}
<p class="error">{{ message }}</p>
{% endfor %}
</div>
</section>

<section id="socials">
<div class="section-title">
<span>LET'S CONNECT</span>
<h2>My Socials</h2>
</div>
<div class="socials">
<a class="social" href="https://instagram.com/skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">IG</span>Instagram</a>
<a class="social" href="https://www.tiktok.com/@skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">TK</span>TikTok</a>
<a class="social" href="https://github.com/skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">GH</span>GitHub</a>
<a class="social" href="https://discord.com/users/1391832246314340584" target="_blank" rel="noopener noreferrer"><span class="icon">DC</span>Discord</a>
<a class="social" href="https://wa.me/212773337627" target="_blank" rel="noopener noreferrer"><span class="icon">WA</span>WhatsApp</a>
<a class="social" href="https://facebook.com/skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">FB</span>Facebook</a>
<a class="social" href="https://www.youtube.com/@skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">YT</span>YouTube</a>
<a class="social" href="https://t.me/skyovx" target="_blank" rel="noopener noreferrer"><span class="icon">TG</span>Telegram</a>
</div>
</section>

<section id="contact">
<div class="section-title">
<span>GET IN TOUCH</span>
<h2>Contact Me</h2>
</div>
<div class="contact-box">
<p>Have something to share? Feel free to get in touch.</p>
<a href="https://wa.me/212773337627" target="_blank" rel="noopener noreferrer" class="btn">CONTACT ON WHATSAPP</a>
</div>
</section>

<footer>© 2026 SKYOVX — ALL RIGHTS RESERVED</footer>
</body>
</html>
"""


# =====================================================
# QUIZ START
# =====================================================

START_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKYOVX | Start Test</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">SKYOVX</div>
<p class="subtitle">THE PRIVATE CHALLENGE</p>

<div class="card">
<span class="badge">20 QUESTIONS • 20 POINTS</span>
<h2 style="margin-top:20px">Ready for the challenge?</h2>
<p>Enter your name before starting the test.</p>

<form method="POST">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<input name="name" maxlength="60" placeholder="Enter Your Name" required>
<button class="btn" type="submit">START THE TEST →</button>
</form>
</div>
<a href="{{ url_for('home') }}#room">← Back to SKYOVX ROOM</a>
<footer>SKYOVX • PRIVATE CHALLENGE</footer>
</div>
</body>
</html>
"""


# =====================================================
# QUIZ
# =====================================================

QUIZ_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKYOVX | The Test</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">SKYOVX</div>
<p class="subtitle">HOW WELL DO YOU KNOW ME?</p>

<div class="card">
<span class="badge">20 QUESTIONS</span>
<span class="badge">PLAYER: {{ name }}</span>

<h2 style="margin-top:20px">THE TEST</h2>
<p>Choose one answer for every question. Your final score will be revealed at the end.</p>

<div class="progress"><div style="width:100%"></div></div>

<form method="POST" action="{{ url_for('quiz_submit') }}">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

{% for q in questions %}
{% set q_index = loop.index0 %}
<div class="question">
<h3>{{ loop.index }}. {{ q.question }}</h3>

{% for option in q.options %}
<label class="option">
<input type="radio"
name="q{{ q_index }}"
value="{{ 'ABCDEF'[loop.index0] }}"
required>
{{ 'ABCDEF'[loop.index0] }} — {{ option }}
</label>
{% endfor %}
</div>
{% endfor %}

<button class="btn" type="submit"
onclick="return confirm('Are you ready to submit your answers?')">
SUBMIT MY ANSWERS →
</button>
</form>
</div>
<footer>SKYOVX • YOUR CHALLENGE</footer>
</div>
</body>
</html>
"""


# =====================================================
# RESULT
# =====================================================

RESULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKYOVX | Your Result</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">SKYOVX</div>
<p class="subtitle">CHALLENGE COMPLETED</p>

<div class="card" style="text-align:center;padding:45px 25px">
<div style="font-size:55px">🏆</div>
<h2>Congratulations, {{ name }}!</h2>
<p>You have completed the SKYOVX challenge.</p>

<div style="font-size:75px;font-weight:bold;margin:30px 0;
text-shadow:0 0 25px #ffffff55">
{{ score }}<span style="font-size:28px;color:#888">/20</span>
</div>

<p>Your result has been recorded.</p>
<p style="margin-top:15px">Thank you for taking the challenge.</p>
</div>

<a class="btn" href="{{ url_for('quiz_start') }}">TRY AGAIN ↻</a>
<a class="btn btn-outline" href="{{ url_for('home') }}#room">HOME</a>

<footer>SKYOVX • ALL RIGHTS RESERVED</footer>
</div>
</body>
</html>
"""


# =====================================================
# MYSTERY ROOM
# =====================================================

MYSTERY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKYOVX | Mystery Room</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">SKYOVX</div>
<p class="subtitle">CLASSIFIED PRIVATE SPACE</p>

<div class="card" style="text-align:center;padding:55px 25px">
<div style="font-size:65px">🔐</div>
<h2>MYSTERY ROOM</h2>
<p>Not everything is meant to be discovered immediately.</p>
<p style="margin:20px 0"><span class="badge">CLASSIFIED</span></p>
</div>

<a href="{{ url_for('home') }}#room">← BACK TO SKYOVX ROOM</a>
</div>
</body>
</html>
"""


# =====================================================
# ADMIN
# =====================================================

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SKYOVX | Admin</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">SKYOVX</div>
<p class="subtitle">PRIVATE ADMIN PANEL</p>

{% if not logged_in %}
<div class="card">
<h2>Admin Login</h2>
<form method="POST">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<input type="password" name="password" placeholder="Admin Password" required>
<button class="btn" type="submit">LOGIN</button>
</form>
{% for message in get_flashed_messages() %}
<p class="error">{{ message }}</p>
{% endfor %}
</div>

{% else %}

<div class="card">
<h2>{{ results|length }} Quiz Attempts</h2>
<p>SKYOVX TEST RESULTS</p>
</div>

<div class="card">
<h2>Participants Results</h2>
{% if results %}
<div class="table-wrap">
<table>
<thead>
<tr><th>Name</th><th>Score</th><th>Date</th></tr>
</thead>
<tbody>
{% for item in results %}
<tr>
<td>{{ item.name }}</td>
<td>{{ item.score }}/20</td>
<td>{{ item.created_at }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
{% else %}
<p>No quiz attempts yet.</p>
{% endif %}
</div>

<a href="{{ url_for('admin_logout') }}">LOG OUT</a>

{% for message in get_flashed_messages() %}
<p class="error">{{ message }}</p>
{% endfor %}

{% endif %}
<footer>SKYOVX ADMIN</footer>
</div>
</body>
</html>
"""


# =====================================================
# ROUTES
# =====================================================

@app.route("/")
def home():
    return render_template_string(
        HOME_HTML,
        unlocked=session.get("prv_unlocked", False)
    )


@app.route("/unlock", methods=["POST"])
def unlock():
    check_csrf()
    password = request.form.get("password", "")

    if PRV_PASSWORD and hmac.compare_digest(password, PRV_PASSWORD):
        session.clear()
        session["prv_unlocked"] = True
        flash("Welcome to SKYOVX ROOM.")
    else:
        session["prv_unlocked"] = False
        flash("Incorrect password. Try again.")

    return redirect(url_for("home") + "#room")


@app.route("/lock")
def lock():
    session.pop("prv_unlocked", None)
    session.pop("quiz_name", None)
    return redirect(url_for("home") + "#room")


@app.route("/quiz/start", methods=["GET", "POST"])
@private_required
def quiz_start():
    if request.method == "POST":
        check_csrf()
        name = request.form.get("name", "").strip()

        if not name or len(name) > 60:
            flash("Please enter a valid name.")
            return redirect(url_for("quiz_start"))

        session["quiz_name"] = name
        return redirect(url_for("quiz"))

    return render_template_string(START_HTML)


@app.route("/quiz")
@private_required
def quiz():
    name = session.get("quiz_name")

    if not name:
        return redirect(url_for("quiz_start"))

    public_questions = [
        {
            "question": q["question"],
            "options": q["options"]
        }
        for q in QUESTIONS
    ]

    return render_template_string(
        QUIZ_HTML,
        questions=public_questions,
        name=name
    )


@app.route("/quiz/submit", methods=["POST"])
@private_required
def quiz_submit():
    check_csrf()

    name = session.get("quiz_name")
    if not name:
        return redirect(url_for("quiz_start"))

    answers = []

    for i, question in enumerate(QUESTIONS):
        answer = request.form.get(f"q{i}", "").upper()
        valid = LETTERS[:len(question["options"])]

        if answer not in valid:
            flash("Please answer all questions.")
            return redirect(url_for("quiz"))

        answers.append(answer)

    score = sum(
        answers[i] == question["answer"]
        for i, question in enumerate(QUESTIONS)
    )

    try:
        save_quiz_result(name, score, answers)
    except Exception:
        app.logger.exception("Could not save quiz result")
        flash("Could not save your result. Please try again.")
        return redirect(url_for("quiz"))

    session.pop("quiz_name", None)

    return render_template_string(
        RESULT_HTML,
        name=name,
        score=score
    )


@app.route("/mystery")
@private_required
def mystery():
    return render_template_string(MYSTERY_HTML)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        check_csrf()
        password = request.form.get("password", "")

        if ADMIN_PASSWORD and hmac.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        flash("Incorrect admin password.")

    if not session.get("admin_logged_in"):
        return render_template_string(
            ADMIN_HTML,
            logged_in=False,
            results=[]
        )

    try:
        results = get_quiz_results()
    except Exception:
        app.logger.exception("Could not load quiz results")
        results = []
        flash("Could not load results from Google Sheets.")

    return render_template_string(
        ADMIN_HTML,
        logged_in=True,
        results=results
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=False)
