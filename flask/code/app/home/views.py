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
          orderby=db_Grocery.name.asc()
          sort_text='grocery name'
       if sort_by == '-name':
          orderby=db_Grocery.name.desc()
          sort_text='grocery name, descending'
       if sort_by == 'id':
          orderby=db_Grocery.id.asc()
          sort_text='ID'
       if sort_by == '-id':
          orderby=db_Grocery.id.desc()
          sort_text='ID, descending'
       if sort_by == 'sec':
          orderby=db_Grocery.section.asc()
          sort_text='section'
       if sort_by == '-sec':
          orderby=db_Grocery.section.desc()
          sort_text='sorted by section, descending'
       if sort_by == 'ssec':
          orderby=db_Grocery.subsection.asc()
          sort_text='subsection'
       if sort_by == '-ssec':
          orderby=db_Grocery.subsection.desc()
          sort_text='subsection, descending'
       if sort_by == 'price':
          orderby=db_Grocery.price.asc()
          sort_text='price'
       if sort_by == '-price':
          orderby=db_Grocery.price.desc()
          sort_text='price, descending'
       if sort_by == 'store':
          orderby=db_store.name.asc()
          sort_text='store'
       if sort_by == '-store':
          orderby=db_store.name.desc()
          sort_text='name, descending'
    else:
       sort_by = 'id'
       sort_text='ID'

    # Main cursor build
    groceries = db_Grocery.query

    # allcount is the count of groceries in the database
    allcount = groceries.count()

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

    feedback = filtertext + ', sorted by ' + sort_text
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
                           totalcount=totalcount,
                           allcount=allcount)

@home.route('/grocery/add', methods=['GET', 'POST'])
#@login_required
def add_grocery():
    """
    Add a grocery to the database
    """
    add_grocery = True
    flash('You have selected add grocery item')
    return redirect(url_for('home.groceries'))
#    form = AcronymsForm()

#    if form.submit.data:
#       if form.validate_on_submit():
#            if current_user.is_anonymous:
#               authid = 0
#            else:
#               authid = current_user.id
#            acronym = Acronym(acronym=form.acronym.data,
#                          name=form.name.data,
#                          definition=form.definition.data,
#                          author_id=authid,
#                          dateCreate=datetime.datetime.now())

#            db.session.add(acronym)
#            db.session.commit()
            # Better wacronymsay: takes advantage of the fact that when you commit an add, the record acronym is updated
            #             with the new (autogenerated) id by the database
#            new_acro_id=acronym.id
#            formids = request.form.getlist('tag')
#            for tag_id in formids:
#              new_acrotag=AcroTag(acroID=new_acro_id, tagID=tag_id)
#              db.session.add(new_acrotag)

#            db.session.commit()
#            flash('You have successfully added a new
#            return redirect(url_for('home.acronyms'))
#       else:
#    if form.cancel.data:
#        flash('You have cancelled the add of a new Acronym')
#        return redirect(url_for('home.acronyms'))

    # load acronym template
#    return render_template('home/acronyms/acronym.html',
#                           action="Add",
#                           add_acronym=add_acronym,
#                           form=form,
#                           title="Add Acronym",
#                           acronyms_tags=tags,
#                           acronyms_tagids=tagids)

@home.route('/grocery/edit/<int:id>', methods=['GET', 'POST'])
#@login_required
def edit_grocery(id):
    """
    Edit a grocery item
    """
    add_grocery = False
    grocery = db_Grocery.query.get_or_404(id)

    flash('You have selected edit grocery item' + grocery.name)
    return redirect(url_for('home.groceries'))
#    acronym = Acronym.query.get_or_404(id)
    # form = AcronymsForm(obj=acronym)

    # tag_query=Tag.query.all();
    # tagids={}
    # tags={}
    # acrotag_query=AcroTag.query.filter_by(acroID=id).all()
    # associds=[atag.tagID for atag in acrotag_query]

    # for tag in tag_query:
    #   #check it if its associated, else don't
    #   tags[tag.tag] = ( tag.id in associds )
    #   tagids[tag.tag] = tag.id
    #
    # if form.validate_on_submit():
    #     if form.submit.data:
    #       selected_tags={}
    #       # associds has acrotag ids
    #       formids = request.form.getlist('tag')
    #       # Delete all acrotags not in formids
    #       for t in associds:
    #           if t not in formids:
    #              a = AcroTag.query.filter_by(acroID=id).filter_by(tagID=t)
    #              # Remember a is a query string that returns all fields so we only need the id field (field 0)
    #              db.session.delete(a[0])
    #       # Add all tagids in formids not in acrotags
    #       for t in formids:
    #           if t not in associds:
    #              a = AcroTag(acroID=id, tagID=int(t))
    #              db.session.add(a)
    #       acronym.acronym = form.acronym.data
    #       acronym.name = form.name.data
    #       acronym.definition = form.definition.data
    #       db.session.commit()
    #       flash('You have successfully edited the acronym \'' + acronym.acronym + '\'')
    #     else:
    #        flash('You have Cancelled the edit of acronym \'' + acronym.acronym + '\'')
    #
    #     # redirect to the acronym page
    #     return redirect(url_for('home.acronyms'))
    # # Handle submits and cancels when form has missing fields
    # if form.submit.data:
    #     blankFields = ''
    #     sepStr = ''
    #     if form.acronym.data == '':
    #         blankFields = 'Acronym'
    #         sepStr = ','
    #     if form.definition.data == '':
    #         blankFields += sepStr + 'Definition'
    #     flash('You are missing data in fields :' + blankFields)
    # elif form.cancel.data:
    #     flash('You have Cancelled the edit of acronym \'' + acronym.acronym + '\'')
    #     return redirect(url_for('home.acronyms'))
    # form.acronym.data = acronym.acronym
    # return render_template('home/acronyms/acronym.html',
    #                        action="Edit",
    #                        add_acronym=add_acronym,
    #                        form=form,
    #                        acronym=acronym,
    #                        title="Edit Tag",
    #                        acronyms_tags=tags,
    #                        acronyms_tagids=tagids)


@home.route('/grocery/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_grocery(id):
    """
    Delete a grocery entry from the database
    """
    grocery = db_Grocery.query.get_or_404(id)
    flash('You have selected delete grocery item ' + grocery.name)
    return redirect(url_for('home.groceries'))
    # check_admin()
    #
    # acronym = Acronym.query.get_or_404(id)
    # db.session.delete(acronym)
    # db.session.commit()
    # flash('You have successfully deleted the acronym.')
    #
    # # redirect to the acronyms page
    # return redirect(url_for('home.acronyms'))
    #
    # return render_template(title="Delete Acronym")
