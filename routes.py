from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('companion.companion_chat_text'))
    return render_template("main/home.html", user=current_user)

@routes.route('/chat')
@login_required
def chat():
    return render_template("companion/chat.html", user=current_user)

@routes.route('/voice')
@login_required
def voice():
    return render_template("companion/voice.html", user=current_user)