
import os
import sqlite3
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template_string, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")

DATABASE = "skyovx.db"

# Passwords
PRV_PASSWORD = "220871"
ADMIN_PASSWORD_HASH = generate_password_hash("Hafa@220871")


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


init_db()


# ---------------- HOME PAGE ----------------

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#080808">

<title>SKYOVX | Official Portfolio</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    scroll-behavior: smooth;
}

:root {
    --bg: #080808;
    --card: #111111;
    --gray: #999999;
    --border: #292929;
}

body {
    background: var(--bg);
    color: white;
    font-family: Arial, sans-serif;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    width: 450px;
    height: 450px;
    background: #ffffff0a;
    filter: blur(120px);
    top: 10%;
    left: 25%;
    border-radius: 50%;
    pointer-events: none;
    z-index: -1;
}

header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #080808ed;
    backdrop-filter: blur(18px);
    padding: 12px 8%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
}

.logo {
    width: 170px;
    height: 65px;
    overflow: hidden;
}

.logo img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: invert(1);
    transition: .3s;
}

.logo img:hover {
    transform: scale(1.08);
}

nav {
    display: flex;
    gap: 25px;
}

nav a {
    color: #aaa;
    text-decoration: none;
    font-size: 14px;
    transition: .3s;
}

nav a:hover {
    color: white;
    text-shadow: 0 0 12px white;
}

.menu-btn {
    display: none;
    color: white;
    background: transparent;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 10px 14px;
    cursor: pointer;
}

.hero {
    min-height: 88vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 30px 20px;
    background: radial-gradient(ellipse at center, #222 0%, #080808 70%);
}

.tag {
    color: white;
    border: 1px solid #555;
    padding: 10px 20px;
    border-radius: 30px;
    font-size: 11px;
    letter-spacing: 4px;
    animation: fadeDown 1s ease both;
}

.hero h1 {
    font-size: clamp(55px, 12vw, 120px);
    letter-spacing: 12px;
    color: white;
    text-shadow: 0 0 35px #ffffff55;
    animation: heroTitle 1.2s ease both, glow 3s infinite alternate;
}

.hero h2 {
    font-size: 22px;
    margin-top: 15px;
}

.hero p {
    color: var(--gray);
    line-height: 1.8;
    max-width: 550px;
    margin: 20px auto 30px;
}

.buttons {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    justify-content: center;
}

.btn {
    display: inline-block;
    padding: 15px 28px;
    border-radius: 30px;
    text-decoration: none;
    font-weight: bold;
    font-size: 13px;
    transition: .3s;
    cursor: pointer;
}

.primary {
    background: white;
    color: black;
}

.secondary {
    border: 1px solid #666;
    color: white;
    background: transparent;
}

.btn:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px #ffffff44;
}

section:not(.hero) {
    padding: 85px 8%;
}

.section-title {
    text-align: center;
    margin-bottom: 45px;
}

.section-title span {
    color: #aaa;
    letter-spacing: 5px;
    font-size: 11px;
}

.section-title h2 {
    font-size: 36px;
    margin-top: 12px;
}

.about-box {
    max-width: 800px;
    margin: auto;
    background: var(--card);
    border: 1px solid var(--border);
    padding: 40px;
    border-radius: 18px;
    text-align: center;
    transition: .4s;
}

.about-box:hover {
    border-color: white;
    transform: translateY(-5px);
}

.about-box p {
    color: var(--gray);
    line-height: 2;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 22px;
}

.project {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 30px;
    transition: .4s;
}

.project:hover {
    transform: translateY(-10px);
    border-color: white;
    box-shadow: 0 10px 35px #ffffff12;
}

.number {
    color: #aaa;
    font-size: 12px;
    letter-spacing: 3px;
    margin-bottom: 20px;
}

.project h3 {
    margin-bottom: 15px;
}

.project p {
    color: var(--gray);
    line-height: 1.8;
    font-size: 14px;
}

.project a {
    display: inline-block;
    margin-top: 22px;
    color: white;
    text-decoration: none;
}

.socials {
    max-width: 900px;
    margin: auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
}

.social {
    background: var(--card);
    border: 1px solid var(--border);
    padding: 25px 12px;
    border-radius: 14px;
    text-align: center;
    text-decoration: none;
    color: white;
    transition: .35s;
}

.social .icon {
    display: block;
    color: white;
    font-size: 25px;
    font-weight: bold;
    margin-bottom: 12px;
}

.social:hover {
    border-color: white;
    background: #222;
    transform: translateY(-7px);
    box-shadow: 0 0 20px #ffffff15;
}

.contact-box {
    max-width: 600px;
    margin: auto;
    padding: 40px;
    text-align: center;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    transition: .3s;
}

.contact-box:hover {
    border-color: white;
}

.contact-box p {
    color: var(--gray);
    line-height: 1.8;
    margin-bottom: 25px;
}

/* PRIVATE MESSAGE */

.private-card {
    max-width: 650px;
    margin: auto;
    padding: 40px;
    text-align: center;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    transition: .3s;
}

.private-card:hover {
    border-color: white;
}

.private-icon {
    font-size: 35px;
    margin-bottom: 20px;
}

.private-card p {
    color: var(--gray);
    line-height: 1.8;
    margin-bottom: 25px;
}

.private-card input,
.private-card textarea {
    width: 100%;
    background: #080808;
    border: 1px solid #333;
    border-radius: 10px;
    padding: 16px;
    color: white;
    font-size: 14px;
    outline: none;
    margin-bottom: 15px;
    font-family: Arial, sans-serif;
}

.private-card textarea {
    resize: vertical;
    min-height: 150px;
}

.private-card input:focus,
.private-card textarea:focus {
    border-color: white;
}

.private-card button {
    border: none;
}

.form-message {
    margin-top: 15px;
    color: #ccc;
    font-size: 13px;
}

.reveal {
    opacity: 0;
    transform: translateY(45px);
    transition: opacity .8s ease, transform .8s ease;
}

.reveal.show {
    opacity: 1;
    transform: translateY(0);
}

footer {
    text-align: center;
    padding: 30px;
    border-top: 1px solid var(--border);
    color: #777;
    font-size: 13px;
}

footer span {
    color: white;
    letter-spacing: 3px;
}

@keyframes glow {
    from { text-shadow: 0 0 15px #ffffff44; }
    to { text-shadow: 0 0 45px #ffffffaa; }
}

@keyframes heroTitle {
    from { opacity: 0; transform: scale(.8); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@media(max-width: 700px) {
    header { padding: 10px 5%; }

    .logo {
        width: 140px;
        height: 55px;
    }

    .menu-btn { display: block; }

    nav {
        display: none;
        position: absolute;
        top: 75px;
        left: 0;
        width: 100%;
        padding: 25px;
        background: #101010;
        flex-direction: column;
        text-align: center;
        border-bottom: 1px solid #333;
    }

    nav.active { display: flex; }

    .hero h1 { letter-spacing: 5px; }
    .hero h2 { font-size: 18px; }

    section:not(.hero) { padding: 65px 6%; }

    .section-title h2 { font-size: 28px; }

    .about-box,
    .contact-box,
    .private-card { padding: 25px; }

    .socials { grid-template-columns: repeat(2, 1fr); }
}

@media(prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
    }

    .reveal {
        opacity: 1;
        transform: none;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">
        <img src="{{ url_for('static', filename='skyovx-logo.jpeg') }}"
             alt="SKYOVX Logo">
    </div>

    <button class="menu-btn" onclick="toggleMenu()"
            id="menuButton" aria-expanded="false">
        ☰ MENU
    </button>

    <nav id="nav">
        <a href="#home" onclick="closeMenu()">Home</a>
        <a href="#about" onclick="closeMenu()">About</a>
        <a href="#private" onclick="closeMenu()">PRV Message</a>
        <a href="#socials" onclick="closeMenu()">Socials</a>
        <a href="#contact" onclick="closeMenu()">Contact</a>
    </nav>
</header>

<section class="hero" id="home">
    <div class="tag">WELCOME TO MY WORLD</div>
    <h1>SKYOVX</h1>
    <h2>Independent Soul | Unique Mind</h2>
    <p>
        Not everyone needs to be understood.
        Some are simply meant to be different.
        Welcome to my world.
    </p>

    <div class="buttons">
        <a href="#private" class="btn primary">PRV MESSAGE</a>
        <a href="#socials" class="btn secondary">FOLLOW ME</a>
    </div>
</section>

<section id="about" class="reveal">
    <div class="section-title">
        <span>BEYOND THE SURFACE</span>
        <h2>About Me</h2>
    </div>

    <div class="about-box">
        <p>
            Just a soul with a different perspective.
            I believe in individuality, silence,
            and being true to myself.
            I don't follow the crowd — I create my own path.
        </p>
    </div>
</section>

<!-- PRIVATE MESSAGE -->

<section id="private" class="reveal">
    <div class="section-title">
        <span>PRIVATE SPACE</span>
        <h2>PRV Message</h2>
    </div>

    <div class="private-card">
        <div class="private-icon">🔒</div>
        <h3>Enter Private Space</h3>
        <p>
            A private place to share your thoughts with SKYOVX.
            Enter the access code to continue.
        </p>

        {% if not unlocked %}
        <form method="POST" action="{{ url_for('unlock') }}">
            <input type="password" name="password"
                   placeholder="Enter Access Password"
                   maxlength="100" required>
            <button class="btn primary" type="submit">
                UNLOCK →
            </button>
        </form>
        {% else %}
        <h3 style="margin-bottom:20px;">Send Me A Message</h3>

        <form method="POST" action="{{ url_for('send_message') }}">
            <input type="text" name="name"
                   placeholder="Your Name"
                   maxlength="60" required>

            <textarea name="message"
                      placeholder="Write your message here..."
                      maxlength="3000" required></textarea>

            <button class="btn primary" type="submit">
                SEND MESSAGE ↗
            </button>
        </form>
        <p style="margin-top:20px;">
            <a href="{{ url_for('lock') }}"
               style="color:white;">Lock Private Space</a>
        </p>
        {% endif %}

        {% with messages = get_flashed_messages() %}
            {% for message in messages %}
                <div class="form-message">{{ message }}</div>
            {% endfor %}
        {% endwith %}
    </div>
</section>

<section id="socials" class="reveal">
    <div class="section-title">
        <span>LET'S CONNECT</span>
        <h2>My Socials</h2>
    </div>

    <div class="socials">

        <a class="social" href="https://instagram.com/skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">IG</span>Instagram
        </a>

        <a class="social" href="https://www.tiktok.com/@skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">TK</span>TikTok
        </a>

        <a class="social" href="https://github.com/skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">GH</span>GitHub
        </a>

        <a class="social"
           href="https://discord.com/users/1391832246314340584"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">DC</span>Discord
        </a>

        <a class="social" href="https://wa.me/212773337627"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">WA</span>WhatsApp
        </a>

        <a class="social" href="https://facebook.com/skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">FB</span>Facebook
        </a>

        <a class="social" href="https://www.youtube.com/@skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">YT</span>YouTube
        </a>

        <a class="social" href="https://t.me/skyovx"
           target="_blank" rel="noopener noreferrer">
            <span class="icon">TG</span>Telegram
        </a>

    </div>
</section>

<section id="contact" class="reveal">
    <div class="section-title">
        <span>GET IN TOUCH</span>
        <h2>Contact Me</h2>
    </div>

    <div class="contact-box">
        <p>
            Have something to share?
            Feel free to get in touch.
        </p>

        <a href="https://wa.me/212773337627"
           target="_blank" rel="noopener noreferrer"
           class="btn primary">
            CONTACT ON WHATSAPP
        </a>
    </div>
</section>

<footer>
    © 2026 <span>SKYOVX</span> — ALL RIGHTS RESERVED
</footer>

<script>
function toggleMenu() {
    const nav = document.getElementById("nav");
    const button = document.getElementById("menuButton");

    nav.classList.toggle("active");

    button.setAttribute(
        "aria-expanded",
        nav.classList.contains("active")
    );
}

function closeMenu() {
    document.getElementById("nav").classList.remove("active");
    document.getElementById("menuButton")
        .setAttribute("aria-expanded", "false");
}

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll(".reveal").forEach((element) => {
        observer.observe(element);
    });
} else {
    document.querySelectorAll(".reveal").forEach((element) => {
        element.classList.add("show");
    });
}
</script>

</body>
</html>
"""


# ---------------- ADMIN PAGE ----------------

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SKYOVX | Admin</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: #080808;
    color: white;
    font-family: Arial, sans-serif;
    padding: 30px 6%;
}

h1 {
    text-align: center;
    margin: 20px 0;
    letter-spacing: 5px;
}

.subtitle {
    text-align: center;
    color: #999;
    margin-bottom: 35px;
}

.card {
    max-width: 850px;
    margin: 20px auto;
    padding: 25px;
    background: #111;
    border: 1px solid #292929;
    border-radius: 15px;
}

input {
    width: 100%;
    padding: 15px;
    background: #080808;
    border: 1px solid #444;
    border-radius: 8px;
    color: white;
    margin: 15px 0;
}

button, .btn {
    display: inline-block;
    background: white;
    color: black;
    border: none;
    padding: 13px 22px;
    border-radius: 25px;
    cursor: pointer;
    font-weight: bold;
    text-decoration: none;
}

.message {
    background: #171717;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 22px;
    margin: 18px 0;
    overflow-wrap: anywhere;
}

.message p {
    color: #ccc;
    line-height: 1.8;
    margin: 15px 0;
    white-space: pre-wrap;
}

small { color: #888; }

.logout {
    display: block;
    text-align: center;
    margin: 30px;
    color: #aaa;
}

.error {
    color: #ff7777;
    margin: 15px 0;
}
</style>
</head>
<body>

<h1>SKYOVX</h1>
<p class="subtitle">PRIVATE ADMIN PANEL</p>

{% if not logged_in %}

<div class="card">
    <h2>Admin Login</h2>

    <form method="POST" action="{{ url_for('admin') }}">
        <input type="password" name="password"
               placeholder="Admin Password" required>
        <button type="submit">LOGIN</button>
    </form>

    {% with messages = get_flashed_messages() %}
        {% for message in messages %}
            <p class="error">{{ message }}</p>
        {% endfor %}
    {% endwith %}
</div>

{% else %}

<div class="card">
    <h2>Messages: {{ messages|length }}</h2>
</div>

{% for item in messages %}
<div class="message">
    <h3>{{ item['name'] }}</h3>
    <small>{{ item['created_at'] }}</small>
    <p>{{ item['message'] }}</p>

    <form method="POST"
          action="{{ url_for('delete_message', message_id=item['id']) }}"
          onsubmit="return confirm('Delete this message?')">
        <button type="submit">DELETE</button>
    </form>
</div>
{% else %}
<div class="card">
    <p>No messages yet.</p>
</div>
{% endfor %}

<a class="logout" href="{{ url_for('admin_logout') }}">LOG OUT</a>

{% endif %}

</body>
</html>
"""


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    unlocked = session.get("prv_unlocked", False)
    return render_template_string(HOME_HTML, unlocked=unlocked)


@app.route("/unlock", methods=["POST"])
def unlock():
    password = request.form.get("password", "")

    if password == PRV_PASSWORD:
        session["prv_unlocked"] = True
        flash("Access granted. Welcome!")
    else:
        session["prv_unlocked"] = False
        flash("Incorrect password. Try again.")

    return redirect(url_for("home") + "#private")


@app.route("/lock")
def lock():
    session.pop("prv_unlocked", None)
    return redirect(url_for("home") + "#private")


@app.route("/send-message", methods=["POST"])
def send_message():
    if not session.get("prv_unlocked"):
        return redirect(url_for("home") + "#private")

    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        flash("Please complete all fields.")
        return redirect(url_for("home") + "#private")

    if len(name) > 60 or len(message) > 3000:
        flash("Your message is too long.")
        return redirect(url_for("home") + "#private")

    db = get_db()
    db.execute(
        "INSERT INTO messages (name, message, created_at) VALUES (?, ?, ?)",
        (name, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    db.commit()
    db.close()

    flash("Your message has been sent successfully!")
    return redirect(url_for("home") + "#private")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin_logged_in"):
        if request.method == "POST":
            password = request.form.get("password", "")

            if check_password_hash(ADMIN_PASSWORD_HASH, password):
                session["admin_logged_in"] = True
                return redirect(url_for("admin"))

            flash("Incorrect admin password.")

        return render_template_string(
            ADMIN_HTML,
            logged_in=False,
            messages=[]
        )

    db = get_db()
    messages = db.execute(
        "SELECT * FROM messages ORDER BY id DESC"
    ).fetchall()
    db.close()

    return render_template_string(
        ADMIN_HTML,
        logged_in=True,
        messages=messages
    )


@app.route("/admin/delete/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    db = get_db()
    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()
    db.close()

    return redirect(url_for("admin"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=False)
    