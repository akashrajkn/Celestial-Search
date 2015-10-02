from flask_wtf import Form
from wtforms import TextField,SubmitField

class QueryForm(Form):
	querytext=TextField("Enter text")
	
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

def eovn(document_directory, dictionary_file, postings_file):
	print (str(document_directory))

