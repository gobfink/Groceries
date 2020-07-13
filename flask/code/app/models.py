# apps/models.py

from datetime import datetime
from app import db

#store_table
class db_store(db.Model):
    __tablename__ = 'storeTable'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    groceries_store = db.relationship('db_Grocery', backref='store', lazy='dynamic')

    def __repr__(self):
        return '<Store: %s>' %format(self.name)


class db_Grocery(db.Model):
    """
    Create Groceries table
    """

    __tablename__ = 'groceryTable'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    category = db.Column(db.String(60))
    section = db.Column(db.String(60))
    subsection = db.Column(db.String(60))
    price = db.Column(db.Float)
    ounces = db.Column(db.Float)
    reported_price_per_unit = db.Column(db.String(30))
    brand = db.Column(db.String(80))
    date = db.Column(db.DateTime, default=False)
    price_density = db.column_property(price/ounces)
    store_id = db.Column(db.Integer, db.ForeignKey('storeTable.id'))
    url = db.Column(db.Sbtring(120))


    #TODO convert ids into values this will require pulling down the other tables, and somehow referencing them
    #column_sortable_list = ('acronym', 'definition', 'author.userLN')

    def __repr__(self):
        return '<Grocery: %s, Def: %s>'%(format(self.name),format(self.price))

class db_Urls(db.Model):
    """
    Create Groceries table
    """


    __tablename__ = 'urlTable'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100))
    Updated = db.Column(db.DateTime, default=False)
    hits = db.Column(db.Integer)
    store = db.Column(db.Integer, db.ForeignKey('storeTable.id'))
    scraped = db.Column(db.tinyint(1))
    category = db.Column(db.String(50))
    section = db.Column(db.String(50))
    subsection = db.Column(db.String(50))
    #TODO makesure timestamp is setup to change on update


    def __repr__(self):
        return '<URL: %s, section: %s, subsection %s>'%(format(self.url),format(self.section), format(self.subsection))

