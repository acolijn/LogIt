from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email

class LogbookForm(FlaskForm):
    logbook_name = StringField('Logbook Name', validators=[DataRequired()])
    allowed_keywords = TextAreaField('Allowed Keywords (comma-separated)')
    submit = SubmitField('Create Logbook', id='create_logbook')

class AddUsersToLogbookForm(FlaskForm):
    logbook_select = SelectField('Select Logbook', choices=[], validators=[DataRequired()])
    #username = StringField('Username', validators=[DataRequired()])
    user_select = SelectField('Select User', coerce=str)  # <-- This line
    submit = SubmitField('Add User to Logbook', id='add_user_to_logbook')
