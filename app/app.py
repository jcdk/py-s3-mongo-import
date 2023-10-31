import os 
from flask import Flask, render_template, request

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import custom modules
from importToMongo import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload',methods=['POST'])
def upload():
    global filename
    if request.method=='POST':
        flags = {}
        if 'flags' in request.form:
            flags = request.form['flags']
        file = request.files['file']

        try:
            response = importToMongo(file, flags)
            # return render_template('index.html', text=response)
            return response
        except Exception as e:
            # return render_template('index.html', text=str(e))
            return str(e)

if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0', port=8000)