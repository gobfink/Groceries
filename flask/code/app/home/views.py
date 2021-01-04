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
    ROWS_PER_PAGE = 25
    page = request.args.get('page', 1, type=int)

    # Check if filtering was added and if it is reset page
    submitted = request.args.get("submit")
    if submitted != None:
       page = 1

    # Sort Section
    sort_by = request.args.get("sort")
    orderby=db_Grocery.id.asc() # Default ordering is by ID
    if sort_by != None:
       if sort_by == 'name':
          sorttext = 'grocery name'
          orderby=db_Grocery.name.asc()
       if sort_by == '-name':
          sorttext = 'grocery name, descending'
          orderby=db_Grocery.name.desc()
       if sort_by == 'id':
          sorttext = 'ID'
          orderby=db_Grocery.id.asc()
       if sort_by == '-id':
          sorttext = 'ID, descending'
          orderby=db_Grocery.id.desc()
       if sort_by == 'sec':
          sorttext = 'Section'
          orderby=db_Grocery.section.asc()
       if sort_by == '-sec':
          sorttext = 'Section, descending'
          orderby=db_Grocery.section.desc()
       if sort_by == 'ssec':
          sorttext = 'Sub Section'
          orderby=db_Grocery.subsection.asc()
       if sort_by == '-ssec':
          sorttext = 'Sub Section, descending'
          orderby=db_Grocery.subsection.desc()
       if sort_by == 'price':
          sorttext = 'Price'
          orderby=db_Grocery.price.asc()
       if sort_by == '-price':
          sorttext = 'Price, descending'
          orderby=db_Grocery.price.desc()
       if sort_by == 'store':
          sorttext = 'Store'
          orderby=db_store.name
       if sort_by == '-store':
          sorttext = 'Store, descending'
          orderby=db_store.name.desc()
    else:
       sorttext = 'ID'
       sort_by = 'id'

    # Main cursor build
    groceries = db_Grocery.query

    filtertext = ''
    sepStr = ''

    #Filter section
    grocery_name = request.args.get("grocery_name")
    if grocery_name != None and len(grocery_name) > 0:
       filtertext += sepStr + 'grocery name like ' + "'" + grocery_name + "'"
       sepStr = ' and '
       groceries = groceries.filter(db_Grocery.name.like('%' + grocery_name + '%'))
    else:
       grocery_name=""
    store_name = request.args.get("store_name")
    if store_name != None and len(store_name) > 0:
       filtertext += sepStr + 'store name like ' + "'" + store_name + "'"
       sepStr = ' and '
       groceries = groceries.filter(db_store.name.like('%' + store_name + '%'))
    else:
       store_name=""
    section = request.args.get("section")
    if section != None and len(section) > 0:
       filtertext += sepStr + 'section like ' + "'" + section + "'"
       sepStr = ' and '
       groceries = groceries.filter(db_Grocery.section.like('%' + section + '%'))
    else:
       section=""
    subsection = request.args.get("subsection")
    if subsection != None and len(subsection) > 0:
       filtertext += sepStr + 'sub section like ' + "'" + subsection + "'"
       sepStr = ' and '
       groceries = groceries.filter(db_Grocery.subsection.like('%' + subsection + '%'))
    else:
       subsection=""
    if filtertext == '':
        filtertext = 'All Groceries'
    else:
        filtertext = 'Groceries where ' + filtertext
    groceries = groceries.join(db_store, db_Grocery.store)
    groceries = groceries.order_by(orderby)
    totalcount = groceries.count()
    groceries = groceries.paginate(page,ROWS_PER_PAGE, False)

    storelist=getStores()
    sectionlist=getSections()
    subsectionlist=getSubSections()

    next_url = url_for('home.groceries', page=groceries.next_num) if groceries.has_next else None
    prev_url = url_for('home.groceries', page=groceries.prev_num) if groceries.has_prev else None

    feedback = filtertext + ', sorted by ' + sorttext
    return render_template('home/groceries/groceries.html',
                           groceries=groceries.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           sort_by=sort_by,
                           grocery_name=grocery_name,
                           store_name=store_name,
                           section=section,
                           subsection=subsection,
                           storelist = storelist,
                           sectionlist = sectionlist,
                           subsectionlist = subsectionlist,
                           feedback = feedback,
                           pagenum=page,
                           totalcount=totalcount)
