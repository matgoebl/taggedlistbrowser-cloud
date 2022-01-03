import logging
import yaml
import re
import jsonpath_ng

from taggedlist.helper import find_tags, has_obj_value

class AnnotatedResults:
    def __init__(self,lists,items):
        self.taggedlists = lists
        self.items = {}
        for item in items:
            self.items[item] = {}

    def annotate(self):
        for item in self.items:
            self.items[item] = {}
            for label, list in self.taggedlists.lists.items():
                if item in list:
                    self.items[item][label] = list[item]
                elif label.startswith('_'):
                    for filename, doc in list.items():
                        if has_obj_value(item, -1, doc):
                            if not label in self.items[item]:
                                self.items[item][label] = []
                            self.items[item][label].append(filename)

    def search(self, expr):
        if not expr:
            return
        if expr.find('*') >= 0:
            logging.debug(f"Searching regex '{expr}'")
            regex = re.compile(expr)
            self.items = { k:v for k,v in self.items.items() if regex.match(k) }
        else:
            logging.debug(f"Searching substring {expr}")
            self.items = { k:v for k,v in self.items.items() if k.startswith(expr) }

    def filter(self, filters, tagspecs = {}, docspec = ""):
        keep_items = []
        for filter in filters:
            logging.debug(f"Filtering for '{filter}'")
            inputspec = None
            if filter.find(':') >= 0:
                (inputspec, filter) = filter.split(':',2)
            if filter.find('=') >= 0:
                (tagpath, tagvalue) = filter.split('=',2)
                jsonpath_expr = jsonpath_ng.parse(tagspecs[tagpath])
                logging.debug(f"Filtering for {inputspec}:{tagspecs[tagpath]}({tagpath}) == {tagvalue}")
                for item, tags in self.taggedlists.lists[inputspec].items():
                    matches = [match.value for match in jsonpath_expr.find(tags)]
                    if tagvalue in matches:
                        logging.debug(f"Filter found {tagvalue} in {inputspec}:{tagpath}")
                        keep_items.append(item)
            else:
                keep_items = [match.value for match in jsonpath_ng.parse('hosts[*]').find(self.taggedlists.lists[inputspec][filter])]
                logging.debug(f"Filtering for keys {keep_items}")
        self.items = { k:v for k,v in self.items.items() if k in keep_items }

    def keys(self):
        return [ k for k,v in self.items.items() ]

    def results(self):
        return self.items
