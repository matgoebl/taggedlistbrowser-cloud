#!/usr/bin/env python3

import sys
import yaml
import importlib
import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.append("src")
import example_preprocessor as preprocessor_mod

filename="dumped-preannotated-model.yaml"

with open(filename) as f:
    data = yaml.load(f, Loader=yaml.BaseLoader)

preprocessor_mod = importlib.import_module(preprocessor, package="preprocessor")
preprocessor_mod.preprocess(data["lists"], data["annotatedresult"])
