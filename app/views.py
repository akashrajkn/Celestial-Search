from flask import Flask,render_template,request
from forms import QueryForm,eovn
from search import search,load_dictionary,process_query,load_posting_list,shunting_yard,boolean_NOT,boolean_OR,boolean_AND
from index import index,is_number
app = Flask(__name__)
app.secret_key = 'bits-hyderabad'

docs = {}

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/query',methods=['GET','POST'])
def query():
	form=QueryForm()
	global docs
	
	if not docs:
		docs = index('static/yahooanswers', 'dictionary-list', 'postings-list')

	if request.method=='GET':
		eovn('static/wikipedia', 'alpha', 'beta')
		return render_template('querytext.html',form=form)
	elif request.method=='POST':

		qstring = 'queried string: ' + form.querytext.data
		ans = search('dictionary-list', 'postings-list', form.querytext.data, 'output')

		ans = sorted(ans, key=lambda x: x[1], reverse=True)

		output = ''
		for docID, count in ans:
			output += 'DocID: ' + str(docID) + ' Count: ' + str(count) + ' Link: ' + '<a href="./static/yahooanswers/' + docs[int(docID)] + '">' + docs[int(docID)] + '</a>' + '</br>'
		'''
		print '~~~~~~~~'
		print output
		'''
		return qstring+'<br/><br/>Search Results: ' + output
if __name__ == '__main__':
	app.run(debug = True)