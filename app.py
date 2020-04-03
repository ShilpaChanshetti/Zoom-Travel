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

if __name__ == '__main__':
    app.run()