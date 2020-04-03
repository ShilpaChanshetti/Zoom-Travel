from flask import Flask, render_template
import datetime
import re
app = Flask(__name__)

@app.route("/")
def home():
    #print('s')
    return render_template('index.html')