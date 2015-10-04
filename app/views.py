from flask import Flask, render_template, request
from forms import QueryForm
from search import search
from index import index

app = Flask(__name__)
app.secret_key = 'bits-hyderabad'

docs = {}
corpus_path = 'static/wikipedia/'

@app.route('/', methods=['GET', 'POST'])
def query():
    form=QueryForm()
    global docs

    # If indexing not yet done, then index the corpus
    if not docs:
        docs = index(corpus_path, 'dictionary-list', 'postings-list')

    if request.method=='GET':
        return render_template('querytext.html', form=form)
    elif request.method == 'POST':
        qstring = 'Queried string: ' + form.querytext.data
        results = search('dictionary-list', 'postings-list', form.querytext.data)

        results = sorted(results, key=lambda x: x[1], reverse=True)

        output = []
        for docID, count in results:
            res = {}
            res['docID'] = str(docID)
            res['count'] = str(count)
            res['link'] = corpus_path + docs[int(docID)]
            res['caption'] = docs[int(docID)]
            output.append(res)
            #output += 'DocID: ' + str(docID) + ' Count: ' + str(count) + ' Link: ' + '<a href=".' + corpus_path + docs[int(docID)] + '">' + docs[int(docID)] + '</a>' + '</br>'

        #return qstring + '<br/><br/>Search Results: ' + output

        return render_template('results.html', form=form, output=output)

        

if __name__ == '__main__':
    app.run(debug = True)