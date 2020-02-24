# app/home/views.py
import datetime
from wtforms import BooleanField 
from flask import abort, render_template, redirect, flash, url_for, request
from flask_login import current_user, login_required
from ..models import Acronym, Tag, AcroTag, User
from .. import db

from . forms import AcronymsForm, AcronymSearchForm, AddTagForm

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

@home.route('/acronyms', methods=['GET','POST'])
def acronyms():
    """
    List all acronyms
    """
    totalcount = Acronym.query.count()

    up='headerSortUp'
    down='headerSortDown'
    blank=''
    sortem = [blank, blank, blank, blank, blank]
    search = AcronymSearchForm(request.form)
    searchVal=request.args.get('searchVal')
    choice = request.args.get('choice')
    sorter = ''
    dir = ''
    if request.method == 'POST':
       sorter = request.args.get('sort')
       dir = request.args.get('dir')
       searchVal = request.form["search"]
       choice = request.form["select"]
       searchStr = "%{}%".format(searchVal)
       if choice == 'acronym':
          acronyms = Acronym.query.filter(Acronym.acronym.like(searchStr))
       elif choice == 'name':
          acronyms = Acronym.query.filter(Acronym.name.like(searchStr))
       elif choice == 'definition':
          acronyms = Acronym.query.filter(Acronym.definition.like(searchStr))
       else:
          #Need to find all tag ids that match the search term,
          tags = Tag.query.filter(Tag.tag.like(searchStr))
          taglist = []
          for tag in tags:
              taglist.append(tag.id) 
          # then find all acroIDs in acrotag
          acrotags = AcroTag.query.filter(AcroTag.tagID.in_(taglist))
          acrolist = []
          for acrotag in acrotags:
              acrolist.append(acrotag.acroID)
          # then find all acronyms that have acroid in the acroID list
          acronyms = Acronym.query.filter(Acronym.id.in_(acrolist))
       subcount = acronyms.count()
       if (sorter == 'acronym'):
          if dir == 'desc':
              sortem = [down, blank, blank, blank, blank]
              acronyms = acronyms.order_by(Acronym.acronym.desc())
          else:
              sortem = [up, blank, blank, blank, blank]
              acronyms = acronyms.order_by(Acronym.acronym)
       elif (sorter == 'name'):
          if dir == 'desc':
              sortem = [blank, down, blank, blank, blank]
              acronyms = acronyms.order_by(Acronym.name.desc())
          else:
              sortem = [blank, up, blank, blank, blank]
              acronyms = acronyms.order_by(Acronym.name)
       elif (sorter == 'definition'):
          if dir == 'desc':
              sortem = [blank, blank, down, blank, blank]
              acronyms = acronyms.order_by(Acronym.definition.desc())
          else:
              sortem = [blank, blank, up, blank, blank]
              acronyms = acronyms.order_by(Acronym.definition)
       elif (sorter == 'author'):
          if dir == 'desc':
              sortem = [blank, blank, blank, down, blank]
              acronyms = acronyms.join(User, Acronym.author).order_by(User.userLN.desc())
          else:
              sortem = [blank, blank, blank, up, blank]
              acronyms = acronyms.join(User, Acronym.author).order_by(User.userLN)
       elif (sorter == 'date'):
          if dir == 'desc':
              sortem = [blank, blank, blank, blank, down]
              acronyms = acronyms.order_by(Acronym.dateCreate.desc())
          else:
              sortem = [blank, blank, blank, blank, up]
              acronyms = acronyms.order_by(Acronym.dateCreate)
       #acronyms = acronyms.order_by(Acronym.acronym)
    else:
       sorter = request.args.get('sort')
       dir = request.args.get('dir')
       if (sorter == 'acronym'):
           if dir == 'desc':
              sortem = [down, blank, blank, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.acronym.desc()).all()
           else:
              sortem = [up, blank, blank, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.acronym).all()
       elif (sorter == 'name'):
           if dir == 'desc':
              sortem = [blank, down, blank, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.name.desc()).all()
           else:
              sortem = [blank, up, blank, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.name).all()
       elif (sorter == 'definition'):
           if dir == 'desc':
              sortem = [blank, blank, down, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.definition.desc()).all()
           else:
              sortem = [blank, blank, up, blank, blank]
              acronyms = Acronym.query.order_by(Acronym.definition).all()
       elif (sorter == 'author'):
           if dir == 'desc':
              sortem = [blank, blank, blank, down, blank]
              acronyms = Acronym.query.join(User, Acronym.author).order_by(User.userLN.desc()).all()
           else:
              sortem = [blank, blank, blank, up, blank]
              acronyms = Acronym.query.join(User, Acronym.author).order_by(User.userLN).all()
       elif (sorter == 'date'):
           if dir == 'desc':
              sortem = [blank, blank, blank, blank, down]
              acronyms = Acronym.query.order_by(Acronym.dateCreate.desc()).all()
           else:
              sortem = [blank, blank, blank, blank, up]
              acronyms = Acronym.query.order_by(Acronym.dateCreate).all()
       else:
           acronyms = Acronym.query.order_by(Acronym.acronym).all()
       subcount = len(acronyms) 
    tags = Tag.query.all() 
    return render_template('home/acronyms/acronyms.html',
                           acronyms=acronyms,
                           searchVal=searchVal,
                           choice=choice,
                           tags=tags,
                           totalcount=totalcount,
                           sortem=sortem,
                           sorter=sorter,
                           dir=dir,
                           subcount=subcount,
                           title='Acronyms',
                           form=search) 

@home.route('/acronyms/add', methods=['GET', 'POST'])
#@login_required
def add_acronym():
    """
    Add a acronym to the database
    """      
    add_acronym = True

    """
    Create dynamic objects on the form
      - Query the tag database
      - Turn into actual string values
      - DIsplay in the form
    """
    tags={}
    tagids={}
    tag_query=Tag.query.all();
    for tag in tag_query:
      tags[tag.tag] = 0
      tagids[tag.tag] = tag.id

    form = AcronymsForm()

    if form.submit.data:
       if form.validate_on_submit():
            if current_user.is_anonymous:
               authid = 0
            else:
               authid = current_user.id
            acronym = Acronym(acronym=form.acronym.data, 
                          name=form.name.data,
                          definition=form.definition.data,
                          author_id=authid,
                          dateCreate=datetime.datetime.now())

            db.session.add(acronym)
            db.session.commit()
            # Better way: takes advantage of the fact that when you commit an add, the record acronym is updated
            #             with the new (autogenerated) id by the database
            new_acro_id=acronym.id
            formids = request.form.getlist('tag')
            for tag_id in formids:
              new_acrotag=AcroTag(acroID=new_acro_id, tagID=tag_id)
              db.session.add(new_acrotag)

            db.session.commit()
            flash('You have successfully added a new acronym - \'' + form.acronym.data + '\'')
            return redirect(url_for('home.acronyms'))
       else:
            flash('Fill in required fields!')
    if form.cancel.data:
        flash('You have cancelled the add of a new Acronym')
        return redirect(url_for('home.acronyms'))

    # load acronym template
    return render_template('home/acronyms/acronym.html', 
                           action="Add",
                           add_acronym=add_acronym,
                           form=form,
                           title="Add Acronym",
                           acronyms_tags=tags,
                           acronyms_tagids=tagids)

@home.route('/acronyms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_acronym(id):
    """
    Edit a acronym
    """
    add_acronym = False
    
    acronym = Acronym.query.get_or_404(id)
    form = AcronymsForm(obj=acronym)
   
    tag_query=Tag.query.all();
    tagids={}
    tags={}
    acrotag_query=AcroTag.query.filter_by(acroID=id).all()
    associds=[atag.tagID for atag in acrotag_query]

    for tag in tag_query:
      #check it if its associated, else don't
      tags[tag.tag] = ( tag.id in associds ) 
      tagids[tag.tag] = tag.id

    if form.validate_on_submit():
        if form.submit.data:
          selected_tags={}
          # associds has acrotag ids
          formids = request.form.getlist('tag')
          # Delete all acrotags not in formids
          for t in associds:
              if t not in formids:
                 a = AcroTag.query.filter_by(acroID=id).filter_by(tagID=t)   
                 # Remember a is a query string that returns all fields so we only need the id field (field 0)
                 db.session.delete(a[0])
          # Add all tagids in formids not in acrotags          
          for t in formids:
              if t not in associds:
                 a = AcroTag(acroID=id, tagID=int(t))
                 db.session.add(a)
          acronym.acronym = form.acronym.data
          acronym.name = form.name.data
          acronym.definition = form.definition.data
          db.session.commit()
          flash('You have successfully edited the acronym \'' + acronym.acronym + '\'')
        else:
           flash('You have Cancelled the edit of acronym \'' + acronym.acronym + '\'')

        # redirect to the acronym page
        return redirect(url_for('home.acronyms'))
    # Handle submits and cancels when form has missing fields
    if form.submit.data:
        blankFields = ''
        sepStr = ''
        if form.acronym.data == '':
            blankFields = 'Acronym' 
            sepStr = ','
        if form.definition.data == '':
            blankFields += sepStr + 'Definition'
        flash('You are missing data in fields :' + blankFields)
    elif form.cancel.data:
        flash('You have Cancelled the edit of acronym \'' + acronym.acronym + '\'')
        return redirect(url_for('home.acronyms'))
    form.acronym.data = acronym.acronym
    return render_template('home/acronyms/acronym.html', 
                           action="Edit",
                           add_acronym=add_acronym, 
                           form=form,
                           acronym=acronym, 
                           title="Edit Tag", 
                           acronyms_tags=tags,
                           acronyms_tagids=tagids)


@home.route('/acronyms/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_acronym(id):
    """
    Delete a acronym from the database
    """
    check_admin()

    acronym = Acronym.query.get_or_404(id)
    db.session.delete(acronym)
    db.session.commit()
    flash('You have successfully deleted the acronym.')

    # redirect to the acronyms page
    return redirect(url_for('home.acronyms'))

    return render_template(title="Delete Acronym")
