from flask_wtf import Form
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired

class TestForm(Form):
    field_one = StringField('COSTCENTER:', validators=[DataRequired()])
    field_two = StringField('PERSONID:')
    field_three = StringField('DISPLAYNAME:')
    field_four = StringField('WONUM:')
    field_id = HiddenField('ID:')
