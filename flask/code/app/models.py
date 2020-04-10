# apps/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

class User(UserMixin, db.Model):
    """
    Create a user
    """

    __tablename__ = 'tbl_User'
    
    id = db.Column(db.Integer, primary_key=True)
    userEmail = db.Column(db.String(80), index=True, unique=True)
    username = db.Column(db.String(80), index=True, unique=True)
    userFN = db.Column(db.String(80), index=True)
    userLN = db.Column(db.String(80), index=True)
    userPasswordHash = db.Column(db.String(128))
    userIsAdmin = db.Column(db.Integer, default=False)
    userLastLoginDT = db.Column(db.DateTime, default=False)
    userLoginDT = db.Column(db.DateTime, default=False)
    posts = db.relationship('Acronym', backref='author', lazy='dynamic')

    def setPassdate(self):
        self.userLastLoginDT = datetime.now()


    @property
    def password(self):
        """
        Prevent Password being accessed
        """

        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
      
        self.userPasswordHash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """

        return check_password_hash(self.userPasswordHash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    #Set up user_loader
    @login_manager.user_loader
    def load_user(userID):
        return User.query.get(int(userID))

class AcroTag(db.Model):
    """
    Create AcroTag table
    """

    __tablename__ = 'tbl_AcroTag'
    
    id = db.Column(db.Integer, primary_key=True)
    acroID = db.Column(db.Integer, db.ForeignKey('tbl_Acronym.id'))
    tagID = db.Column(db.Integer, db.ForeignKey('tbl_Tag.id'))


class Acronym(db.Model):
    """
    Create Acronym table
    """

    __tablename__ = 'tbl_Acronym'

    id = db.Column(db.Integer, primary_key=True)
    acronym = db.Column(db.String(80), index=True, unique=True)
    definition = db.Column(db.Text)
    name = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('tbl_User.id'))
    dateCreate = db.Column(db.DateTime, default=False)
    acrotags = db.relationship('AcroTag', cascade='all,delete', backref='acronym', lazy='dynamic')

    column_sortable_list = ('acronym', 'definition', 'author.userLN')

    def __repr__(self):
       return '<Acronym: %s, Def: %s>'%(format(self.acronym),format(self.definition))

class Tag(db.Model):
    """
    Create tag table
    """

    __tablename__ = 'tbl_Tag'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(60), index=True, unique=True)
    acrotags = db.relationship('AcroTag', cascade='all,delete', backref='tagTable', lazy='dynamic')

    def __repr__(self):
       return '<Tag: {}>'.format(self.tag)

# quality_table
class db_quality(db.Model):
    __tablename__ = 'qualityTable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    groceries_quality = db.relationship('db_Grocery', backref='quality', lazy='dynamic')

    def __repr__(self):
        return '<Quality:%s>' % format(self.name)
    
#store_table
class db_store(db.Model):
    __tablename__ = 'storeTable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    groceries_store = db.relationship('db_Grocery', backref='store', lazy='dynamic')

    def __repr__(self):
        return '<Store: %s>' %format(self.name)

#author_table
class db_author(db.Model):
    __tablename__ = 'authorTable'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    groceries_author = db.relationship('db_Grocery', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<Author: %s>' %format(self.name)

class db_Grocery(db.Model):
    """
    Create Groceries table
    """

    __tablename__ = 'groceryTable'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)
    ounces = db.Column(db.Float)
    price_density = db.column_property(price/ounces)
    brand = db.Column(db.String(80))
    #quality_id = db.Column(db.Integer, db.ForeignKey('db_quality.id'))
    #quality_relationship = db.relationship('db_groceries', backref='quality', lazy='dynamic')

    # quality_name = db.Column(db.Integer, db.ForeignKey('quality_table.name'))

    date = db.Column(db.DateTime, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authorTable.id'))
    store_id = db.Column(db.Integer, db.ForeignKey('storeTable.id'))
    quality_id = db.Column(db.Integer, db.ForeignKey('qualityTable.id'))
    #TODO convert ids into values this will require pulling down the other tables, and somehow referencing them
    #column_sortable_list = ('acronym', 'definition', 'author.userLN')

    def __repr__(self):
        return '<Grocery: %s, Def: %s>'%(format(self.name),format(self.price))

