# app/home/views.py
import datetime
from wtforms import BooleanField
from flask import abort, render_template, redirect, flash, url_for, request
from flask_login import current_user, login_required
from ..models import db_Grocery, db_store
from .. import db

from .forms import GroceryForm, GrocerySearchForm

from . import home

from ..Core import *


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


@home.route('/stats', methods=['GET', 'POST'])
def stats():
    """
    Statistical Page
    """
    sql='select count(*) as groceryCnt, st.name from groceryTable as gt left join storeTable as st on st.id = gt.store_id group by st.name;'
    grocerystats = executeSQLm(sql)
    sql='select count(*) as urlCnt, st.name from urlTable as gt left join storeTable as st on st.id = gt.store_id group by st.name;'
    urlstats = executeSQLm(sql)
    sql='select count(*) as groceryCnt, st.name, gt.section, gt.subsection from groceryTable as gt left join storeTable as st on st.id = gt.store_id group by st.name, gt.section,gt.subsection order by st.name, gt.section, gt.subsection'
    detailstats = executeSQLm(sql)
    return render_template('home/stats/stats.html',
                       urlstats=urlstats,
                       detailstats=detailstats,
                       grocerystats=grocerystats)

@home.route('/groceries', methods=['GET', 'POST'])
def groceries():
    """
    Display the different groceries
    """
    #grocery_list = []

    columns_to_display = ['name', 'section', 'subsection', 'price', 'ounces', 'reported_price_per_unit', 'price_density', 'brand', 'date',
                          'store', 'url']
    #grocery_search = GrocerySearchForm(request.form)

    # Create a choice list of tuples from the columns_to_display
    #grocery_search.select.choices = [(c, c) for c in columns_to_display]

    ROWS_PER_PAGE = 25
    page = request.args.get('page', 1, type=int)
    
    groceries = db_Grocery.query.paginate(page,ROWS_PER_PAGE, False)
    next_url = url_for('home.groceries', page=groceries.next_num) if groceries.has_next else None
    prev_url = url_for('home.groceries', page=groceries.prev_num) if groceries.has_prev else None
    #groceries = db_Grocery.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    #groceries = db_Grocery.query.all()
    #q_groceries = db_Grocery.query.all()
    #search_query = ""
    #selected_choice = ""

    #if request.method == 'POST':
    #    search_query = request.form["search"]
    #    selected_choice = request.form["select"]
    #
    # flash(q_groceries)

    # Convert sqlalchemy model into a dictionary so that jinja2 html can parse it easier
    # TODO I bet the performance here is going to be awful once we start adding allot of groceries
    #for grocery in q_groceries:
        # Do all of the direct fields first
    #    raw = grocery.__dict__
        # Manually add all backrefs to the raw dict
    #    raw['store'] = grocery.store.name

    #    fields = {field: raw[field] for field in columns_to_display}
    #    if search_query:
    #        if search_query in str(raw[selected_choice]):
    #            grocery_list.append(fields)
    #    else:
    #        grocery_list.append(fields)
    #
    # flash(grocery_list)

    #number_of_groceries = len(q_groceries)
    #groceries_showing = len(grocery_list)

    return render_template('home/groceries/groceries.html',
    #                       groceries_queried=q_groceries,
                           groceries=groceries.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           column_titles=columns_to_display)
    #                       totalcount=number_of_groceries,
    #                       subcount=groceries_showing,
    #                       search_form=grocery_search,
    #                       g_list=grocery_list)
