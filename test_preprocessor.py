#!/usr/bin/env python3

import sys
import yaml
import importlib
import logging
logging.basicConfig(level=logging.DEBUG,handlers=[logging.StreamHandler()],format="[%(levelname)s] %(message)s")
logging.info(f"Preprocessor testing started...")

sys.path.append("src")
import example_preprocessor as preprocessor_mod

filename="dumped-preannotated-model.yaml"
preprocessor = "example_preprocessor"

with open(filename) as f:
    data = yaml.load(f, Loader=yaml.BaseLoader)

preprocessor_mod = importlib.import_module(preprocessor)
preprocessor_mod.preprocess(data["lists"], data["annotatedresult"], True)
