from flask import Flask,render_template,request
from forms import QueryForm,eovn,index,is_number
from search import search,load_dictionary,process_query,load_posting_list,shunting_yard,boolean_NOT,boolean_OR,boolean_AND
#from index import index,is_number
app = Flask(__name__)
app.secret_key = 'bits-pharmacy-hyderabad'
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/query',methods=['GET','POST'])
def query():
	form=QueryForm()

	index('nltk_data/corpora/aaaaa', 'dictionary-list', 'postings-list')

	if request.method=='GET':
		eovn('nltk_data/corpora/aaaaa', 'alpha', 'beta')
		return render_template('querytext.html',form=form)
	elif request.method=='POST':

		qstring = 'queried string: ' + form.querytext.data
		ans = search('dictionary-list', 'postings-list', form.querytext.data, 'output')
		return qstring+'<br/><br/>Search Results: ' +ans
if __name__ == '__main__':
    app.run(debug = True)