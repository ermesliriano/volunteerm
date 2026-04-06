from flask import Blueprint, flash, redirect, render_template, request, url_for, Response
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Volunteer
from ..utils.permissions import require_crud
from ..utils.csv_utils import parse_volunteers_csv, EXPECTED_HEADERS
from .forms import VolunteerForm, VolunteersCSVImportForm

volunteers_bp = Blueprint("volunteers", __name__, url_prefix="/volunteers")

@volunteers_bp.get("")
@login_required
def list_volunteers():
    q = (request.args.get("q") or "").strip()
    query = Volunteer.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Volunteer.full_name.ilike(like),
                Volunteer.email.ilike(like),
                Volunteer.city.ilike(like),
            )
        )

    volunteers = query.order_by(Volunteer.full_name.asc()).all()
    return render_template("volunteers_list.html", volunteers=volunteers, q=q)

@volunteers_bp.get("/<int:volunteer_id>")
@login_required
def volunteer_detail(volunteer_id: int):
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    return render_template("volunteer_detail.html", volunteer=volunteer)

@volunteers_bp.get("/new")
@volunteers_bp.post("/new")
@login_required
@require_crud
def volunteer_new():
    form = VolunteerForm()
    if form.validate_on_submit():
        v = Volunteer(
            full_name=form.full_name.data.strip(),
            email=(form.email.data or "").strip().lower() or None,
            phone=(form.phone.data or "").strip() or None,
            city=(form.city.data or "").strip() or None,
            availability=(form.availability.data or "").strip() or None,
            notes=(form.notes.data or "").strip() or None,
            created_by_id=current_user.id,
        )
        db.session.add(v)
        db.session.commit()
        flash("Voluntario creado.", "message")
        return redirect(url_for("volunteers.list_volunteers"))
    return render_template("volunteer_form.html", form=form, mode="new")

@volunteers_bp.get("/<int:volunteer_id>/edit")
@volunteers_bp.post("/<int:volunteer_id>/edit")
@login_required
@require_crud
def volunteer_edit(volunteer_id: int):
    v = Volunteer.query.get_or_404(volunteer_id)
    form = VolunteerForm(obj=v)

    if form.validate_on_submit():
        v.full_name = form.full_name.data.strip()
        v.email = (form.email.data or "").strip().lower() or None
        v.phone = (form.phone.data or "").strip() or None
        v.city = (form.city.data or "").strip() or None
        v.availability = (form.availability.data or "").strip() or None
        v.notes = (form.notes.data or "").strip() or None
        db.session.commit()
        flash("Voluntario actualizado.", "message")
        return redirect(url_for("volunteers.volunteer_detail", volunteer_id=v.id))

    return render_template("volunteer_form.html", form=form, mode="edit", volunteer=v)

@volunteers_bp.post("/<int:volunteer_id>/delete")
@login_required
@require_crud
def volunteer_delete(volunteer_id: int):
    v = Volunteer.query.get_or_404(volunteer_id)
    db.session.delete(v)
    db.session.commit()
    flash("Voluntario eliminado.", "message")
    return redirect(url_for("volunteers.list_volunteers"))

@volunteers_bp.get("/import")
@volunteers_bp.post("/import")
@login_required
@require_crud
def import_csv():
    form = VolunteersCSVImportForm()

    if form.validate_on_submit():
        file = form.file.data
        rows, errors = parse_volunteers_csv(file)

        if errors:
            for err in errors[:10]:
                flash(err, "error")
            return render_template(
                "volunteers_import.html",
                form=form,
                expected_headers=EXPECTED_HEADERS,
            )

        created = 0
        updated = 0
        skipped = 0

        for rec in rows:
            email = rec["email"].strip().lower()
            email = email if email else None

            existing = None
            if email:
                existing = Volunteer.query.filter_by(email=email).first()

            if existing:
                existing.full_name = rec["full_name"]
                existing.phone = rec["phone"] or None
                existing.city = rec["city"] or None
                existing.availability = rec["availability"] or None
                existing.notes = rec["notes"] or None
                updated += 1
            else:
                v = Volunteer(
                    full_name=rec["full_name"],
                    email=email,
                    phone=rec["phone"] or None,
                    city=rec["city"] or None,
                    availability=rec["availability"] or None,
                    notes=rec["notes"] or None,
                    created_by_id=current_user.id,
                )
                db.session.add(v)
                created += 1

        db.session.commit()
        flash(f"Importación completada: {created} creados, {updated} actualizados, {skipped} omitidos.", "message")
        return redirect(url_for("volunteers.list_volunteers"))

    return render_template("volunteers_import.html", form=form, expected_headers=EXPECTED_HEADERS)

@volunteers_bp.get("/sample.csv")
@login_required
def sample_csv():
    # Muestra cabecera esperada + ejemplo
    content = ",".join(EXPECTED_HEADERS) + "\n" + \
              "Ada Lovelace,[email protected],+34 600 000 000,Madrid,Fines de semana,Interés en apoyo logístico\n"
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=volunteers_sample.csv"},
    )
