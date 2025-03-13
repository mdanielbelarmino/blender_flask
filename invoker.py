import function

import os
import shutil

from flask import Flask
from flask import request
from flask import abort
from subprocess import call

app = Flask(__name__)

@app.route('/')
def invoke():
	return function.render(request)

@app.after_request
def cleanup(response):
    location = '/tmp/SadTom.stl'
    os.remove(location)
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)