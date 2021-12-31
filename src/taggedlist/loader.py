import logging
import yaml
import json
import re
import os
import glob

def read_filespec(filespec):
    if filespec.find('*') >= 0:
        return read_fileset(filespec)
    else:
        return read_file(filespec)

def read_fileset(filespec):
    logging.info(f"Reading all {filespec} ...")
    filenames = sorted(glob.glob(filespec))
    data = {}
    for i, filename in enumerate(filenames):
        (label,content)=read_file(filename)
        data[label] = content

    label = os.path.splitext(filespec)[0]
    if label.find('/./') >= 0:
        label = label.split('/./')[-2]
    return (label,data)


def read_file(filename):
    logging.info(f"Reading {filename} ...")
    with open(filename) as f:
        pathfilename, ext = os.path.splitext(filename)
        if ext == '.json':
            data = json.load(f)
        elif ext == '.yaml':
            data = yaml.load(f, Loader=yaml.BaseLoader)
        else:
            return

        label = os.path.basename(pathfilename)
        if pathfilename.find('/./') >= 0:
            label = pathfilename.split('/./')[-1]

        logging.debug(f"Data {label}: {data}")
        return (label,data)
