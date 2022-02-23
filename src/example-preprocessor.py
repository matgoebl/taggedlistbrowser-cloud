import logging

def preprocess(model, annotatedresult):
    logging.info(f"Preprocessing...")
    for label, list in annotatedresult.taggedlists.lists.items():
        if label.startswith('_'):
            for filename, doc in list.items():
                logging.info(f"Preprocessing {label}:{filename} ...")
                logging.debug(annotatedresult.taggedlists.lists["hostlist"])
                for host in doc["hosts"]:
                    annotatedresult.add_item(host,"bookings",filename.split("/")[0],doc["info"])
