from flask_wtf import Form
from wtforms import TextField,SubmitField

LIMIT = None                # (for testing) to limit the number of documents indexed
IGNORE_STOPWORDS = True     # toggling the option for ignoring stopwords
IGNORE_NUMBERS = True       # toggling the option for ignoring numbers
IGNORE_SINGLES = True       # toggling the option for ignoring single character tokens
RECORD_TIME = False         # toggling for recording the time taken for indexer
BYTE_SIZE = 4               # docID is in int


class QueryForm(Form):
	querytext=TextField("Enter text")
	
	
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

def eovn(document_directory, dictionary_file, postings_file):
	print (str(document_directory))

