from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, SignupForm
from .google import verify_google_id_token
from ..extensions import db
from ..models import User, UserRole

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

def _redirect_after_login():
    nxt = request.args.get("next") or request.form.get("next")
    if nxt and _is_safe_url(nxt):
        return redirect(nxt)
    return redirect(url_for("main.dashboard"))

def _apply_admin_role_bootstrap(user: User) -> None:
    admins = current_app.config.get("ADMIN_EMAILS", set())
    if user.email and user.email.lower() in admins:
        user.role = UserRole.ADMIN
    else:
        # Si no está en admins, garantizar reader
        user.role = user.role or UserRole.READER

@auth_bp.get("/login")
@auth_bp.post("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(form.password.data):
            flash("Credenciales inválidas.", "error")
            return render_template("auth_login.html", form=form)

        user.last_login_at = datetime.utcnow()
        _apply_admin_role_bootstrap(user)
        db.session.commit()

        login_user(user, remember=bool(form.remember.data))
        return _redirect_after_login()

    return render_template("auth_login.html", form=form)

@auth_bp.get("/signup")
@auth_bp.post("/signup")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Ese email ya está registrado. Inicia sesión.", "error")
            return render_template("auth_signup.html", form=form)

        user = User(email=email)
        user.set_password(form.password.data)
        user.created_at = datetime.utcnow()

        _apply_admin_role_bootstrap(user)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("auth_signup.html", form=form)

@auth_bp.post("/google")
def google_login():
    # CSRF para AJAX: se envía con header X-CSRFToken (Flask-WTF)
    # (ver auth.js)
    if current_user.is_authenticated:
        return jsonify({"ok": True, "redirect": url_for("main.dashboard")})

    payload = request.get_json(silent=True) or {}
    credential = (payload.get("credential") or "").strip()

    if not credential:
        return jsonify({"ok": False, "error": "Falta credential (ID token)."}), 400

    client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    try:
        idinfo = verify_google_id_token(credential, client_id)
    except ValueError:
        return jsonify({"ok": False, "error": "ID token inválido."}), 401

    google_sub = idinfo.get("sub")
    email = (idinfo.get("email") or "").strip().lower()
    email_verified = bool(idinfo.get("email_verified"))

    if not google_sub:
        return jsonify({"ok": False, "error": "ID token sin sub."}), 400
    if not email:
        return jsonify({"ok": False, "error": "ID token sin email."}), 400
    if not email_verified:
        return jsonify({"ok": False, "error": "Email Google no verificado."}), 403

    user = User.query.filter_by(google_sub=google_sub).first()
    if not user:
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            if user_by_email.google_sub and user_by_email.google_sub != google_sub:
                return jsonify({"ok": False, "error": "Email ya vinculado a otra cuenta Google."}), 409
            user_by_email.google_sub = google_sub
            user = user_by_email
        else:
            user = User(email=email, google_sub=google_sub)

    user.last_login_at = datetime.utcnow()
    _apply_admin_role_bootstrap(user)

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({"ok": True, "redirect": url_for("main.dashboard")})

@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
