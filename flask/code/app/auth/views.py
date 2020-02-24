# app/auth/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

import sqlalchemy

from . import auth
from . forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
import datetime

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an employee to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(userEmail=form.userEmail.data,
                            username=form.username.data,
                            userFN=form.userFN.data,
                            userLN=form.userLN.data,
                            password=form.password.data,
                            userLastLoginDT=datetime.datetime.now(),
                            userLoginDT=sqlalchemy.sql.null(),
                            userIsAdmin=0)

        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(
                form.password.data):

            # log employee in
            login_user(user)

            # set new login datetime stamp for successful login
            if user.userLoginDT != None:
               user.userLastLoginDT=user.userLoginDT
            user.userLoginDT=datetime.datetime.now()
            db.session.commit()

            # redirect to home page 
            return redirect(url_for('home.homepage'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))
