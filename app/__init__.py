from flask import Flask

app = Flask(__name__)
app.secret_key = 'akash-raj'
if __name__ == '__main__':
    app.run()
import app.views