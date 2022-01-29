import logging
import yaml
import re
import jsonpath_ng

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

    def keys(self, listname, docspec = ""):
        keys = {}
        lists = self.get_lists(listname)
        for label, list in lists.items():
            logging.debug(f"Keys in list {label}{listname}")
            if listname == "*" and label.startswith('_') and False:
                continue
            elif label.startswith('_'):
                for filename, doc in list.items():
                    for key in [match.value for match in jsonpath_ng.parse(docspec).find(doc)]:
                        keys[key.lower()] = key
            else:
                for key,value in list.items():
                    keys[key.lower()] = key
        keys_with_capitalization = [ v for k,v in keys.items() ]
        keys_with_capitalization.sort()
        return keys_with_capitalization

    def tags(self, name, listname):
        lists = self.get_lists(listname)
        tags = find_tags(name, -1, lists)
        tags = list(set(tags))
        tags.sort()
        return tags

    def query_valueset(self, tag = '.', inputspec = None, docspec = ""):
        if inputspec == None or inputspec == "":
            inputspec = "*"
        if tag == '.' or tag == '' or tag == None:
            return self.keys(inputspec, docspec)
        else:
            return self.tags(tag, inputspec)

    def labels(self):
        return [ k for k,v in self.lists.items() ]

    def list(self,listname):
        return self.lists[listname]
