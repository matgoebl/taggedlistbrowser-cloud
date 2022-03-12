import logging
import yaml
import re
import jsonpath_ng
import fnmatch
import urllib

from taggedlist.helper import find_tags, has_obj_value

class AnnotatedResults:
    def __init__(self,lists,items):
        self.taggedlists = lists
        self.items = {}
        self.capitalization_map = {}
        for item in items:
            self.add_item(item)
        self.is_annotated = False

    def annotate(self, tagspecs = {}):
        for item in self.items:
            self.add_item(item)
            for label, list in self.taggedlists.lists.items():
                if item in list:
                    self.add_item(item, label, 'data', list[item])
                    for tag, tagpath in tagspecs.items():
                        if tag == '.':
                            continue
                        jsonpath_expr = jsonpath_ng.parse(tagpath)
                        matches = [match.value for match in jsonpath_expr.find(list[item])]
                        self.add_item(item, label, tag, matches)
                elif label.startswith('_'):
                    for filename, doc in list.items():
                        if has_obj_value(item, -1, doc):
                            self.add_item(item,label,filename)
        self.is_annotated = True

    def preannotate(self, tagspecs = {}, docspec = "", docextract = ""):
        logging.info(f"Running preannotation ...")
        for item in self.items:
            self.add_item(item)

        for label, list in self.taggedlists.lists.items():
            logging.info(f"Preannotating {label} ...")
            if not label.startswith('_'):
                for item in list:
                    self.add_item(item, label, 'data', list[item])
                    for tag, tagpath in tagspecs.items():
                        if tag == '.':
                            continue
                        jsonpath_expr = jsonpath_ng.parse(tagpath)
                        matches = [match.value for match in jsonpath_expr.find(list[item])]
                        self.add_item(item, label, tag, matches)
            else:
                for filename, doc in list.items():
                    logging.info(f"Preannotating {label}:{filename} ...")
                    for item in [match.value for match in jsonpath_ng.parse(docspec).find(doc)]:
                        self.add_item(item,label,filename)
                    (tag, extractpaths) = docextract.split(':',2)  # TODO: docextract only available for preannotated mode
                    extract = []
                    for extractpath in extractpaths.split(','):
                        extractresults = [match.value for match in jsonpath_ng.parse(extractpath).find(doc)]
                        if extractresults and extractresults[0]:
                            try:
                                extract.append( ", ".join(extractresults) )
                            except:
                                extract.append( str(extractresults) )
                    self.taggedlists.lists[label][filename][tag] = "; ".join(extract)
        self.is_annotated = True

    def add_item(self, item, label = None, tag = None, data = None ):
        if item.lower() in self.capitalization_map:
            item = self.capitalization_map[item.lower()]
        else:
            self.capitalization_map[item.lower()] = item
        if not item in self.items:
            self.items[item] = {}
        if not label or not tag:
            return
        if not label in self.items[item]:
            self.items[item][label] = {}
        self.items[item][label][tag] = data

    def search(self, exprs):
        if not exprs:
            return
        new_items = {}
        for expr in exprs:
            if expr.startswith( '/'):
                if expr[-1] == '/':  # strip optional trailing slash (convention for regex)
                    expr = expr[:-1]
                logging.debug(f"Searching regex '{expr}'")
                regex = re.compile(expr[1:], re.IGNORECASE)
                new_items.update( { k:v for k,v in self.items.items() if regex.match(k) } )
            else:
                logging.debug(f"Searching string {expr}")
                new_items.update( { k:v for k,v in self.items.items() if fnmatch.fnmatch(k.lower(),expr.lower()) } )
        self.items = new_items

    def filter(self, filters, tagspecs = {}, docspec = ""):
        all_keep_items = [ k for k,v in self.items.items() ]
        for filter in filters:
            logging.debug(f"Filtering for '{filter}'")
            keep_items = []
            inputspec = None  # list(self.taggedlists.lists.keys())[0]
            if filter.find(':') >= 0:
                (inputspec, filter) = filter.split(':',2)
            if not self.taggedlists.lists.get(inputspec):
                logging.info(f"Filtering for '{filter}: input '{inputspec}' does not exist.'")
                self.items = {}
                return
            if filter.find('=') >= 0:
                (tag, tagvalue) = filter.split('=',2)
                tagvalue = urllib.parse.unquote(tagvalue)
                if self.is_annotated:
                    for item, annotation in self.items.items():
                        if ( tagvalue != '' and annotation.get(inputspec) and annotation[inputspec].get(tag) and len([ True for i in annotation[inputspec][tag] if fnmatch.fnmatch(i.lower(),tagvalue.lower()) ]) > 0 ) or \
                           ( tagvalue == '' and len( (annotation.get(inputspec) and annotation[inputspec].get(tag)) or "" ) == 0 ):
                            logging.debug(f"Filter found {tagvalue} in {inputspec}:{tag}")
                            keep_items.append(item)
                else:
                    jsonpath_expr = jsonpath_ng.parse(tagspecs[tag])
                    logging.debug(f"Filtering for {inputspec}:{tagspecs[tag]}({tag}) == {tagvalue}")
                    for item, tags in self.taggedlists.lists[inputspec].items():
                        matches = [match.value for match in jsonpath_expr.find(tags)]
                        if len([ True for i in matches if fnmatch.fnmatch(i.lower(),tagvalue.lower()) ]) > 0:
                            logging.debug(f"Filter found {tagvalue} in {inputspec}:{tag}")
                            keep_items.append(item)
            else:
                keep_items = [match.value for match in jsonpath_ng.parse(docspec).find(self.taggedlists.lists[inputspec][filter])]
                logging.debug(f"Filtering for keys {keep_items}")
            all_keep_items = [ k for k in all_keep_items if k in keep_items ]
        self.items = { k:v for k,v in self.items.items() if k in all_keep_items }

    def keys(self):
        return [ k for k,v in self.items.items() ]

    def results(self):
        return self.items
