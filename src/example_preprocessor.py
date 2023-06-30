import logging

def preprocess(model_lists, annotatedresult_items, testing = False):
    logging.info(f"Preprocessing...")

    def add_doc_item(item,type,doc,element):
        if testing:
            logging.debug(f"{item} {type} {doc} + {element}")
        if type not in annotatedresult_items[item]:
            annotatedresult_items[item][type] = {}
        if doc not in annotatedresult_items[item][type]:
            annotatedresult_items[item][type][doc] = []
        annotatedresult_items[item][type][doc].append(element)

    for label, list in model_lists.items():
        if label.startswith('_'):
            for filename, doc in list.items():
                logging.info(f"Preprocessing {label}:{filename} ...")
                for host in doc["hosts"]:
                    add_doc_item(host,"bookings",filename.split("/")[0],doc["info"])

def oidc_authorize(userinfo):
    if userinfo and userinfo["sub"] != 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx':
        return f"Sorry, you are not authorized, your userinfo is {userinfo}."
