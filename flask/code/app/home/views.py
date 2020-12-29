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
    ROWS_PER_PAGE = 20
    page = request.args.get('page', 1, type=int)
    
    # Sort Section
    sort_by = request.args.get("sort")
    orderby=db_Grocery.id.asc() # Default ordering is by ID
    if sort_by != None:
       if sort_by == 'name':
          orderby=db_Grocery.name.asc()
       if sort_by == '-name':
          orderby=db_Grocery.name.desc()
       if sort_by == 'id':
          orderby=db_Grocery.id.asc()
       if sort_by == '-id':
          orderby=db_Grocery.id.desc()
       if sort_by == 'sec':
          orderby=db_Grocery.section.asc()
       if sort_by == '-sec':
          orderby=db_Grocery.section.desc()
       if sort_by == 'ssec':
          orderby=db_Grocery.subsection.asc()
       if sort_by == '-ssec':
          orderby=db_Grocery.subsection.desc()
       if sort_by == 'price':
          orderby=db_Grocery.price.asc()
       if sort_by == '-price':
          orderby=db_Grocery.price.desc()
    else:
       sort_by = 'id'

    groceries = db_Grocery.query.order_by(orderby).paginate(page,ROWS_PER_PAGE, False)

    next_url = url_for('home.groceries', page=groceries.next_num) if groceries.has_next else None
    prev_url = url_for('home.groceries', page=groceries.prev_num) if groceries.has_prev else None
    totalcount = db_Grocery.query.count()
    return render_template('home/groceries/groceries.html',
                           groceries=groceries.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           sort_by=sort_by,
                           pagenum=page,
                           totalcount=totalcount)
