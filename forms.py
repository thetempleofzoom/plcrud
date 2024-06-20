from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectMultipleField, SelectField

class AddForm(FlaskForm):

    item = StringField('Food Suggestion:')
    quantity = IntegerField('Quantity (default 1):', default=1)
    submit = SubmitField('Add Item')


class GuestForm(FlaskForm):

    guest_name = StringField('Your Name:')
    plusone = IntegerField('Additional Guests?', default=0)
    submit = SubmitField('Add Guest(s)')


class DelForm(FlaskForm):
    # call database for unclaimed list
    tbd = SelectMultipleField(choices=[])
    submit = SubmitField('Remove Item(s)')


class ClaimForm(FlaskForm):
    you = SelectField('Your Name:', choices=[])
    item = SelectMultipleField('Bringing?', choices = [])
    submit = SubmitField('Claim Item(s)')
