from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

class VolunteerForm(FlaskForm):
    full_name = StringField("Nombre completo", validators=[DataRequired(), Length(max=200)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=255)])
    phone = StringField("Teléfono", validators=[Optional(), Length(max=50)])
    city = StringField("Ciudad", validators=[Optional(), Length(max=120)])
    availability = StringField("Disponibilidad", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("Notas", validators=[Optional()])

class VolunteersCSVImportForm(FlaskForm):
    file = FileField(
        "CSV",
        validators=[
            FileRequired(),
            FileAllowed(["csv"], "Solo se permiten ficheros CSV."),
        ],
    )
