# app/home/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, SelectField, BooleanField, FieldList, TextAreaField, FloatField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField


def _required(form, field):
    if not field.raw_data or not field.raw_data[0]:
       raise ValidationError('Field is required') 

class GroceryForm(FlaskForm):
    """
    Form for adding/editing groceries
    """
    name = StringField('Name', validators=[_required, Length(1,80)])
    brand = StringField('Brand', validators=[_required, Length(1,80)])
    store = SelectField('Store', coerce=int, validators=[_required])
    price = FloatField('Price')
    ounces = FloatField('Ounces')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


class GrocerySearchForm(Form):
    """
    Form for the Grocery search button
    """
    select = SelectField('')
    search = StringField('')
