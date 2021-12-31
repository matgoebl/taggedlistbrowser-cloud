#!/usr/bin/env python3
import dotenv
import argparse
import sys
import re
import json
import os
import logging
import yaml
from string import Template
from flask import Flask, request, render_template
from jinja2 import Environment, select_autoescape
from werkzeug.middleware.proxy_fix import ProxyFix

from taggedlist import TaggedLists, AnnotatedResults

dotenv.load_dotenv()
verbose = int(os.environ.get('VERBOSE','0'))
port = int(os.environ.get('PORT','5000'))
datadir = os.environ.get('DATADIR','data')
files = os.environ.get('FILES','model/hostlist.yaml,model/internal.yaml,model/external.yaml,model/./_docs/./*/*.json').split(',')
tags = os.environ.get('TAGS','.').split(',')

logging.basicConfig(level=logging.WARNING-10*verbose,handlers=[logging.StreamHandler()],format="[%(levelname)s] %(message)s")

model = TaggedLists()
model.load_files(files)

Flask.jinja_options = {
    'autoescape': select_autoescape(
        disabled_extensions=('txt'),
        default_for_string=True,
        default=True),
    'line_statement_prefix': '%'
}
app = Flask(__name__)


@app.route("/")
def index():
    results = None
    errormsg = None
    try:
        if 'q' in request.args:
            result = model.query_valueset(request.args.get('t'), request.args.get('i'))
            annotatedresult = AnnotatedResults(model,result)
            if request.args.get('q'):
                annotatedresult.search(request.args.get('q'))
            annotatedresult.annotate()
            if request.args.get('f'):
                annotatedresult.filter(request.args.get('f').split(' '))
            results = annotatedresult.keys()
    except Exception as e:
        errormsg = str(e)
    return render_template('index.html.jinja', results=results, errormsg=errormsg, labels=['*'] + model.labels(), tags=tags )


@app.route('/id/<string:id>')
def detail(id):
    results = None
    errormsg = None
    try:
        result = model.query_valueset()
        annotatedresult = AnnotatedResults(model,result)
        annotatedresult.search(id)
        annotatedresult.annotate()
        results = annotatedresult.results()
        results_yaml = yaml.dump(annotatedresult.results(),default_flow_style=False,encoding=None,width=160, indent=4)
    except Exception as e:
        errormsg = str(e)

    data = None
    try:
        with open(datadir + "/" + id + '.json', 'r') as f:
            data = json.load(f)
            f.close()
            data = json.dumps(data, indent=2)
    except:
        pass

    return render_template('detail.html.jinja', results=results, results_yaml=results_yaml, errormsg=errormsg, id=id, data=data)


@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
