# app/home/views.py
import datetime
from wtforms import BooleanField
from flask import abort, render_template, redirect, flash, url_for, request
from flask_login import current_user, login_required
from ..models import db_Grocery, db_store
from .. import db

from .forms import GroceryForm, GrocerySearchForm

from . import home


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if current_user.userIsAdmin != 1:
        abort(403)


@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """

    return render_template('home/index.html', title="Welcome")


@home.route('/groceries', methods=['GET', 'POST'])
def groceries():
    """
    Display the different groceries
    """
    grocery_list = []

    columns_to_display = ['id', 'name', 'section', 'subsection', 'price', 'ounces', 'reported_price_per_unit', 'price_density', 'brand', 'date',
                          'store']
    grocery_search = GrocerySearchForm(request.form)

    # Create a choice list of tuples from the columns_to_display
    grocery_search.select.choices = [(c, c) for c in columns_to_display]

    q_groceries = db_Grocery.query.all()
    search_query = ""
    selected_choice = ""

    if request.method == 'POST':
        search_query = request.form["search"]
        selected_choice = request.form["select"]

    # flash(q_groceries)

    # Convert sqlalchemy model into a dictionary so that jinja2 html can parse it easier
    # TODO I bet the performance here is going to be awful once we start adding allot of groceries
    for grocery in q_groceries:
        # Do all of the direct fields first
        raw = grocery.__dict__
        # Manually add all backrefs to the raw dict
        raw['store'] = grocery.store.name

        fields = {field: raw[field] for field in columns_to_display}
        if search_query:
            if search_query in str(raw[selected_choice]):
                grocery_list.append(fields)
        else:
            grocery_list.append(fields)

    # flash(grocery_list)

    number_of_groceries = len(q_groceries)
    groceries_showing = len(grocery_list)

    return render_template('home/groceries/groceries.html',
                           groceries_queried=q_groceries,
                           column_titles=columns_to_display,
                           totalcount=number_of_groceries,
                           subcount=groceries_showing,
                           search_form=grocery_search,
                           g_list=grocery_list)