from flask_wtf import Form
from wtforms import TextField, SubmitField

class QueryForm(Form):
    querytext=TextField("Enter text: ")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)