import logging
import yaml
import re

from taggedlist import loader
from taggedlist.helper import find_tags


class TaggedLists:
    def __init__(self):
        self.lists = {}
        self.nested_tags = True

    def load_files(self, files):
        for file in files:
            self.load_file(file)

    def load_file(self, filespec, name = None):
        (label,data) = loader.read_filespec(filespec)
        if name:
            label = name
        self.lists[label] = data

    def __str__(self):
        return yaml.dump(self.lists)

    def get_lists(self,listname):
        if not listname or listname == '*':
            return self.lists
        else:
            return {listname: self.lists[listname]}

    def keys(self,listname):
        keys=[]
        lists = self.get_lists(listname)
        for label, list in lists.items():
            logging.info(f"Keys in list {label}")
            if listname == "*" and label.startswith('_'):
                continue
            for key,value in list.items():
                if key not in keys:
                    keys.append(key)
        keys.sort()
        return keys

    def tags(self, name, listname):
        lists = self.get_lists(listname)
        tags = find_tags(name, -1, lists)
        tags = list(set(tags))
        tags.sort()
        return tags

    def query_valueset(self, tag = '.', inputspec = None):
        if inputspec == None or inputspec == "":
            inputspec = "*"
        if tag == '.' or tag == '' or tag == None:
            return self.keys(inputspec)
        else:
            return self.tags(tag, inputspec)

    def labels(self):
        return [ k for k,v in self.lists.items() ]
