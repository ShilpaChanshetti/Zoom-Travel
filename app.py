# from flask import Flask, render_template
# import datetime
# import re
# app = Flask(__name__)

# @app.route("/")
# def home():
#     #print('s')
#     return render_template('index.html')

from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def aboutUs():
    return render_template('about-us.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run()