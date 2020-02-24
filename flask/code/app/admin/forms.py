# app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, FileField
from wtforms.validators import DataRequired, Optional, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Tag, User

class UploadForm(FlaskForm):
    file = FileField()
    skipFirstRow = SelectField('First Row Has Headers?', coerce=int, choices=[(1,'Yes'),(0,'No')],validators=[])
    submit = SubmitField('Submit')

class DownloadForm(FlaskForm):
    file = StringField('Save As', validators=[DataRequired()])
    addHeader = SelectField('Add Headers ?', coerce=int, choices=[(1,'Yes'),(0,'No')],validators=[])
    submit = SubmitField('Submit')

class TagsForm(FlaskForm):
    """
    Form for admin to add or edit tags
    """
    tag = StringField('Tag', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UsersForm(FlaskForm):
    """
    Form for admin to edit users
    """
    
    username = StringField('Username', validators=[DataRequired()])
    userEmail = StringField('Email', validators=[DataRequired()])
    userFN = StringField('First Name', validators=[])
    userLN = StringField('Last Name', validators=[])
    userIsAdmin = SelectField('Is Admin?', coerce=int, choices=[(1,'Yes'),(0,'No')],validators=[])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')

class UsersAddForm(FlaskForm):
    """
    Form for admin to add users
    """
    
    username = StringField('Username', validators=[DataRequired()])
    userEmail = StringField('Email', validators=[DataRequired()])
    userFN = StringField('First Name', validators=[])
    userLN = StringField('Last Name', validators=[])
    #userIsAdmin = SelectField('Is Admin?', coerce=int, choices=[('1','Yes'),('0','No')],validators=[Optional()])
    userIsAdmin = SelectField('Is Admin?', coerce=int, choices=[(1,'Yes'),(0,'No')],validators=[])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')
