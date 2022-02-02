#!/usr/bin/env python3
import dotenv
import argparse
import sys
import re
import json
import os
import logging
import yaml
import glob
import copy
import datetime
import jsonpath_ng
import urllib.parse
from string import Template
from flask import Flask, request, render_template, make_response, g
from flask_basicauth import BasicAuth
from jinja2 import Environment, select_autoescape
from werkzeug.middleware.proxy_fix import ProxyFix

from taggedlist import TaggedLists, AnnotatedResults
from taggedlist.helper import array_flatten_sort_uniq

has_dotenv = True if os.environ.get('DOTENV') != None else False
dotenv.load_dotenv(os.environ.get('DOTENV','.env'), verbose = has_dotenv, override = has_dotenv)

verbose = int(os.environ.get('VERBOSE','1'))
port = int(os.environ.get('PORT','5000'))
datadir = os.environ.get('DATADIR','data')
files = os.environ.get('FILES','model/hostlist.yaml,model/internal.yaml,model/external.yaml,model/./_docs/./*/*.json').split(',')
tagspec = os.environ.get('TAGS','.,service,user,color,info,summary,type')
docspec = os.environ.get('DOCSPEC','hosts[*]')
docextract = os.environ.get('DOCEXTRACT','summary:info,emails[*]')
mailspec = os.environ.get('MAILSPEC','emails,testemail')
mailsubject = os.environ.get('MAILSUBJECT','Hello from administration')
mailbody = os.environ.get('MAILBODY',"The hosts\n{items}\n\nfrom documents\n{docs}\n\nare affected.")
preannotated_model = os.environ.get('PREANNOTATION','0') == "1"
apptitle = os.environ.get('APPTITLE','Tagged List Browser')
auth_user = os.environ.get('BASIC_AUTH_USERNAME')
auth_pass = os.environ.get('BASIC_AUTH_PASSWORD')

tagspecs = { t.split("=")[0]: t.split("=")[-1] for t in tagspec.split(",")}
tags = [ t.split("=")[0] for t in tagspec.split(",")]

logging.basicConfig(level=logging.WARNING-10*verbose,handlers=[logging.StreamHandler()],format="[%(levelname)s] %(message)s")

init_start_time = datetime.datetime.now()

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

if auth_user and auth_pass:
    app.config['BASIC_AUTH_USERNAME'] = auth_user
    app.config['BASIC_AUTH_PASSWORD'] = auth_pass
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app)


if preannotated_model:
    logging.debug(f"Prepare full annotated model...")
    result = model.query_valueset(None, None, docspec)
    annotatedresult_main = AnnotatedResults(model, result)
    annotatedresult_main.preannotate(tagspecs, docspec, docextract)

init_duration = datetime.datetime.now() - init_start_time
logging.info(f"done. Initialization took {init_duration.total_seconds():.3f} seconds.")


@app.route("/")
def index():
    results = {}
    resultkeys = []
    errormsg = None
    try:
        if 'q' in request.args or 'f' in request.args:
            preannotation_usable = (request.args.get('t') == "." or request.args.get('t') == None) and (request.args.get('i') == "*" or request.args.get('i') == None) and preannotated_model == True
            if preannotation_usable:
                annotatedresult = copy.deepcopy(annotatedresult_main)
            else:
                result = model.query_valueset(request.args.get('t'), request.args.get('i'), docspec)
                annotatedresult = AnnotatedResults(model,result)
            if request.args.get('q'):
                annotatedresult.search(request.args.get('q').split())
            if request.args.get('f'):
                annotatedresult.filter(request.args.get('f').split(), tagspecs, docspec)
            if ( request.args.get('o') == "table" or request.args.get('o') == "yaml" or (request.args.get('i') and request.args.get('i').startswith('_')) ) and not preannotation_usable:
                annotatedresult.annotate(tagspecs)
            results = annotatedresult.results()
            resultkeys = annotatedresult.keys()
    except Exception as e:
        errormsg = repr(e)
    logging.debug(f"Results: {yaml.dump(results)}")

    if request.args.get('o') == "yaml" and not errormsg:
        response = make_response(yaml.dump(results), 200)
        response.mimetype = "text/plain"
        return response

    doclabel = [ label for label in model.labels() if label.startswith('_') ][0]  # only first doc
    alldocs = [ list(v.get(doclabel).keys()) for k,v in results.items() if v.get(doclabel)  ]
    alldocs = array_flatten_sort_uniq(alldocs)

    mailaddrs = []
    for tag in mailspec.split(','):
        jsonpath_expr = jsonpath_ng.parse(tag)
        for doc in [ v for k,v in model.list(doclabel).items() if k in alldocs ]:
            matches = [match.value for match in jsonpath_expr.find(doc)]
            mailaddrs.extend( matches )
    mailaddrs = urllib.parse.quote(";".join(array_flatten_sort_uniq(mailaddrs)))

    mailbody_filled = mailbody.format( items=chr(10).join([k for k,v in results.items()]), docs=chr(10).join(alldocs) )
    mailto = mailaddrs + "?subject=" + urllib.parse.quote(mailsubject,safe='') + "&body=" + urllib.parse.quote(mailbody_filled,safe='')

    return render_template('index.html.jinja', results=results, resultkeys=resultkeys, errormsg=errormsg, labels=['*'] + model.labels(), tags=tags, apptitle=apptitle, alldocs=alldocs, mailto=mailto, mailaddrs=mailaddrs )

@app.route('/id/<string:id>')
def detail(id):
    results = None
    errormsg = None
    results_yaml = None
    try:
        if preannotated_model:
            annotatedresult = copy.deepcopy(annotatedresult_main)
            annotatedresult.search([id])
        else:
            result = model.query_valueset(None, None, docspec)
            annotatedresult = AnnotatedResults(model,result)
            annotatedresult.search([id])
            annotatedresult.annotate(tagspecs)
        results = annotatedresult.results()
        results_yaml = yaml.dump(annotatedresult.results(),default_flow_style=False,encoding=None,width=160, indent=4)
    except Exception as e:
        errormsg = repr(e)

    data = {}
    try:
        filenames = sorted(glob.glob(datadir + "/" + id.lower() + '_*.json'))
        for filename in filenames:
            with open(filename, 'r') as f:
                data['.'.join(os.path.basename(filename).split('.')[:-1])] = json.dumps(json.load(f), indent=2)
                f.close()
    except:
        pass

    return render_template('detail.html.jinja', results=results, results_yaml=results_yaml, errormsg=errormsg, id=id, data=data, apptitle=apptitle )

@app.route('/doc/<string:doc>/<path:id>')
def doc(doc,id):
    doc_json = None
    errormsg = None
    try:
        result = model.list(doc)[id]
        doc_json = json.dumps(result, indent=2)
    except Exception as e:
        errormsg = repr(e)

    return render_template('doc.html.jinja', doc_json=doc_json, errormsg=errormsg, id=id, doc=doc, apptitle=apptitle )


@app.before_request
def start_timer():
  g.time_start = datetime.datetime.now()

@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers["Cache-Control"] = "no-store, max-age=0"

    if 'time_start' in g:
        page_duration = datetime.datetime.now() - g.time_start
        page_duration_fmt = f"{page_duration.total_seconds():.3f}"
        if response.response and 200 <= response.status_code < 300 and response.content_type.startswith('text/html'):
            response.set_data(response.get_data().replace(b'%PAGETIME%', bytes(page_duration_fmt, 'utf-8')))

    return response

app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
