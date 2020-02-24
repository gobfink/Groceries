# app/admin/views.py
from sqlalchemy import func, create_engine, inspect, null
from flask import abort, flash, redirect, render_template, url_for, make_response, send_file
from flask_login import current_user, login_required

from . import admin
from .. import db
from ..models import Tag, User, Acronym, AcroTag

from . forms import TagsForm, UsersForm, UsersAddForm, UploadForm, DownloadForm
from werkzeug.utils import secure_filename

import datetime
import csv

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if current_user.userIsAdmin != 1:
        abort(403)

# Write out the CSV File based on an list of lists

def exportCSV(fileout, recs, addHeader):
  basedir='/code/app/upload/'
  fullpath=basedir+fileout
  with open(fullpath, mode='w') as of:
    writer = csv.writer(of, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    if int(addHeader) == 1:
      myline=['Acronym','Name','Definition','Tags']
      writer.writerow(myline)
    for rec in recs:
      myline=[]
      myline.append(rec.acronym)
      myline.append(rec.name)
      myline.append(rec.definition)
      for acrotag in rec.acrotags:
         myline.append(acrotag.tagTable.tag)
      writer.writerow(myline)
  of.close()
  return 

def getTagID(tagName):
  tag_query=Tag.query.filter_by(tag=tagName).first()
  if tag_query is None: 
    tag=Tag(tag=tagName)
    db.session.add(tag)
    db.session.commit()
    retVal = tag.id 
  else:
    retVal = tag_query.id
  return(retVal)

def setTags(row, acroid):
  if len(row) > 3:
     rowLen=len(row)
     for x in range(3, rowLen):
        tagName=row[x].replace('"', '').strip()
        if len(tagName) > 0:
            tagid=getTagID(tagName)
            acrotag = AcroTag(acroID=acroid, 
                          tagID=tagid)
            db.session.add(acrotag)
            db.session.commit()
  return

def importCSV(filein, skipfirst):
  strOut=''
  basedir='/code/app/upload/'
  fullpath=basedir+filein
  skipit = int(skipfirst)
  with open(fullpath) as ifile:
    csv_reader = csv.reader(ifile, delimiter=',')
    line_count = 0
    sepStr=""
    for row in csv_reader:
        if skipit != 1 or line_count > 0: 
           strOut = strOut + sepStr + row[0] 
           acronym = Acronym(acronym=row[0],
                          name=row[1],
                          definition=row[2],
                          author_id=current_user.id,
                          dateCreate=datetime.datetime.now())
           db.session.add(acronym)
           db.session.commit()
           acroid = acronym.id
           setTags(row, acroid)
           sepStr=","
        line_count+=1
  ifile.close()
  resp="Added Acronyms: " + strOut 
  return (resp)

@admin.route('/Export', methods=['GET','POST'])
@login_required
def export_form():
    """
    Import will prompt for import file
    """
    check_admin()
    
    uploading = False
    
    form = DownloadForm()
  
    if form.validate_on_submit():
       filename = form.file.data
       addHeader = form.addHeader.data
       return redirect(url_for('admin.export_data_file', fileout=filename, addHeader=addHeader))

    return render_template('admin/upload.html', action="Edit",
                           form=form,title="Export File", uploading=uploading)

@admin.route('/Export/<fileout>/<addHeader>', methods=['GET', 'POST'])
@login_required
def export_data_file(fileout,addHeader):
    """
    Export Acronym File 
       Expects a name for the fileout.
       Will put the file into /upload directory that is available locally
       Exports two fields with NO header.  Acronym, Definition
       Will quote delimit both fields seperated by a comma.
    """
    check_admin()
    acros = Acronym.query.all()
    exportCSV(fileout,acros,addHeader)
    #flash('Wrote Acronyms to file /upload/'+fileout)
    #return redirect(url_for('home.acronyms'))
    try:
        return send_file('/code/app/upload/'+fileout, 
                     mimetype='text/csv',
                     attachment_filename=fileout,
                     as_attachment=True)
    except Exception as e:
        return str(e)

@admin.route('/Import', methods=['GET','POST'])
@login_required
def import_form():
    """
    Import will prompt for import file
    """
    check_admin()
    
    form = UploadForm()
  
    uploading = True

    if form.validate_on_submit():
       filename = secure_filename(form.file.data.filename)
       skipFirst = form.skipFirstRow.data
       basedir='/code/app/upload/'
       form.file.data.save(basedir + filename)
       return redirect(url_for('admin.import_data_file',  
                                filein=filename,
                                skipfirst=skipFirst))

    return render_template('admin/upload.html', action="Edit",
                           form=form,title="Upload File", uploading=uploading)

@admin.route('/Import/<filein>/<skipfirst>', methods=['GET', 'POST'])
@login_required
def import_data_file(filein, skipfirst):
    """
    Import Acronym File 
       Expects a name for the file to read in
       Expects the file to be two fields:  Acronym and Definition
       No error checking on import data is done at the moment
       Will append each row of data in the import file to Acronym
       Will set the author to the user importing 
       Will set the creation date to today's date
    """
    check_admin()
    flash(importCSV(filein, skipfirst)) 
    return redirect(url_for('home.acronyms'))


# Tag Views

@admin.route('/tags', methods=['GET', 'POST'])
@login_required
def list_tags():
    """
    List all tags
    """
    check_admin()

    tags = Tag.query.order_by(Tag.tag).all()

    return render_template('admin/tags/tags.html',
                           tags=tags, title="Tags")


@admin.route('/tags/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    """
    Add a tag to the database
    """
    check_admin()

    add_tag = True

    form = TagsForm()

    if form.validate_on_submit():
        tag = Tag(tag=form.tag.data)
        db.session.add(tag)
        db.session.commit()
        flash('You have successfully added a new tag ' + form.tag.data + ' !')
        return redirect(url_for('admin.list_tags'))

    # load tag template
    return render_template('admin/tags/tag.html', action="Add",
                           add_tag=add_tag, form=form,
                           title="Add Tag")


@admin.route('/tags/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    """
    Edit a tag
    """
    check_admin()

    add_tag = False

    tag = Tag.query.get_or_404(id)
    form = TagsForm(obj=tag)
    if form.validate_on_submit():
        tag.tag = form.tag.data
        db.session.commit()
        flash('You have successfully edited the tag.')

        # redirect to the tag page
        return redirect(url_for('admin.list_tags'))

    form.tag.data = tag.tag
    return render_template('admin/tags/tag.html', action="Edit",
                           add_tag=add_tag, form=form,
                           tag=tag, title="Edit Tag")


@admin.route('/tags/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tag(id):
    """
    Delete a tag from the database
    """
    check_admin()

    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('You have successfully deleted the tag.')

    # redirect to the tags page
    return redirect(url_for('admin.list_tags'))

    return render_template(title="Delete Tag")


@admin.route('/users', methods=['GET', 'POST'])
@login_required
def list_users():
    """
    List all users
    """
    check_admin()

    users = User.query.order_by(User.username).all()

    return render_template('admin/users/users.html',
                           users=users, title="Users")

@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """
    Add a user to the database
    """
    check_admin()

    add_user = True

    form = UsersAddForm()
    if form.cancel.data:
       flash('You have cancelled user add.')
       # redirect to the users page
       return redirect(url_for('admin.list_users'))
    elif form.validate_on_submit():
       user = User(userEmail=form.userEmail.data,
                            username=form.username.data,
                            userFN=form.userFN.data,
                            userLN=form.userLN.data,
                            password=form.password.data,
                            userLastLoginDT=datetime.datetime.now(),
                            userLoginDT=null(),
                            userIsAdmin=form.userIsAdmin.data)
       # add user to the database
       db.session.add(user)
       db.session.commit()
       flash('You have successfully added user.')
       # redirect to the users page
       return redirect(url_for('admin.list_users'))
  
    #load new user template
    return render_template('admin/users/user.html', action="Add",
                           add_user=add_user, form=form,
                           title="Add User")

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    Edit a user
    """
    check_admin()

    add_user = False

    user = User.query.get_or_404(id)
    form = UsersForm(obj=user)
    if form.validate_on_submit():
        if form.submit.data:
           user.userEmail = form.userEmail.data
           user.username = form.username.data
           user.userFN=form.userFN.data
           user.userLN=form.userLN.data
           user.userIsAdmin=form.userIsAdmin.data
           db.session.commit()
   
           flash('You have successfully edited the user.')
        else:
           flash('You have cancelled user edit.')

        return redirect(url_for('admin.list_users'))

    form.username.data = user.username
    form.userEmail.data = user.userEmail
    form.userFN.data = user.userFN
    form.userLN.data = user.userLN
    form.userIsAdmin.data = user.userIsAdmin
    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form,
                           user=user, title="Edit User")

@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('You have successfully deleted the user.')

    # redirect to the tags page
    return redirect(url_for('admin.list_users'))

    return render_template(title="Delete User")

