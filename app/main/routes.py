from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..models import Volunteer

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main_bp.get("/dashboard")
@login_required
def dashboard():
    volunteers_count = Volunteer.query.count()
    return render_template("dashboard.html", volunteers_count=volunteers_count)
