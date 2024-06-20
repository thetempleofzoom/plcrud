import os
from forms import AddForm, DelForm, ClaimForm, GuestForm
from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
# Key for Forms
app.config['SECRET_KEY'] = 'mysecretkey'

############################################

# SQL DATABASE AND MODELS

##########################################
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#### addressing the naming convention for foreign keys
naming = {
      "ix": "ix_%(column_0_label)s",
      "uq": "uq_%(table_name)s_%(column_0_name)s",
      "ck": "ck_%(table_name)s_%(constraint_name)s",
      "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
      "pk": "pk_%(table_name)s"
    }

db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming))

app.app_context().push()
migrate = Migrate(app, db, render_as_batch=True)


class Guests(db.Model):
    guest_name = db.Column(db.String(15), primary_key=True)
    plusone = db.Column(db.Integer)
    #one guest, many foods
    food = db.relationship('Food', backref='guests', lazy='dynamic')

    def __init__(self, name, plusone):
        self.guest_name = name
        self.plusone = plusone

    def __repr__(self):
        return f"{self.guest_name} +{self.plusone} "

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(15), unique=True)
    quantity = db.Column(db.Integer, nullable=False)
    guest = db.Column(db.String(15), db.ForeignKey(Guests.guest_name), nullable=False)

    def __init__(self, name, quantity, guest):
        self.item_name = name
        self.quantity = quantity
        self.guest = guest

    def __repr__(self):
        if self.guest =='0':
            return f"{self.quantity} {self.item_name} is still unclaimed"
        else:
            return f"{self.quantity} {self.item_name} claimed by {self.guest}"



############################################

# VIEWS WITH FORMS

##########################################
@app.route('/', methods=['GET'])
def summary():
    # Grab the list of food from database
    allfood = Food.query.all()
    allguests = Guests.query.all()
    base = Guests.query.count()
    plusall = Guests.query.with_entities(Guests.plusone).all()
    plus = [p[0] for p in plusall]
    plus = sum(plus)
    totguests = base+plus
    return render_template('list.html', allfood=allfood, allguests=allguests,
                           totguests=totguests)


@app.route('/add', methods=['GET', 'POST'])
def add_food():
    form = AddForm()

    if form.validate_on_submit():
        name = form.item.data
        qty = form.quantity.data

        try:
            # Add new item to database
            new_item = Food(name, qty, 0)
            print(new_item)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('summary'))
        except IntegrityError:
            flash('Item already exists! Try another')
            db.session.rollback()
            form.item.data = ""
            return render_template('add.html', form=form)

    return render_template('add.html', form=form)


@app.route('/guest', methods=['GET', 'POST'])
def add_guest():
    form = GuestForm()

    if form.validate_on_submit():
        name = form.guest_name.data
        plusone = form.plusone.data

        # Add new guest to database
        new_item = Guests(name, plusone)
        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for('summary'))

    return render_template('guest.html', form=form)


@app.route('/delete', methods=['GET', 'POST'])
def del_food():
    form = DelForm()

    result = db.session.query(Food.item_name).all()
    form.tbd.choices = [res[0] for res in result]
    #print(form.tbd.choices)


    if form.validate_on_submit():
        tbds = form.tbd.data
        for tbd in tbds:
            d = Food.query.filter_by(item_name=tbd).first()
            print(d)
            db.session.delete(d)
            db.session.commit()
        return redirect(url_for('summary'))

    return render_template('delete.html', form=form)


@app.route('/claim', methods=['GET', 'POST'])
def claim_food():
    form = ClaimForm()
    # Grab the list of unclaimed guests from database
    nofood=[]
    allguests = Guests.query.with_entities(Guests.guest_name).all()
    print(allguests)
    #takes first arg of tuple [(a1[0],), (a2[0], )] returned from query
    nofood = [a[0] for a in allguests]

    # Grab the list of unclaimed food from database
    noguest = []
    allfood = Food.query.filter(Food.guest == '0').all()
    print(allfood)
    for a in allfood:
        x = a.item_name
        noguest.append(x)
    print(noguest)

    form.you.choices = nofood
    form.item.choices = noguest

    if form.validate_on_submit():
        you = form.you.data
        item = form.item.data
        for i in item:
            update = Food.query.filter_by(item_name=i).first()
            update.guest = you
            db.session.commit()
        return redirect(url_for('summary'))

    return render_template('claim.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
