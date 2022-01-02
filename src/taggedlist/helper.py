import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

def find_tags(name, maxdepth, obj, key = None):
    indent=(10-maxdepth)*'-'
    tags=[]
    logger.debug(f"{indent} checking {key}={obj}")
    if maxdepth == 0:
        logger.debug(f"{indent} maxdepth reached")
        return tags
    if type(obj)==type({}):
        logger.debug(f"{indent} iterating dict ...")
        for key, obj in obj.items():
            tags.extend(find_tags(name, maxdepth-1, obj, key))
    elif type(obj)==type([]):
        logger.debug(f"{indent} iterating list ...")
        for obj in obj:
            tags.extend(find_tags(name, maxdepth-1, obj))
    elif key == name:
        logger.debug(f"{indent} found {key}={obj}")
        tags.append(obj)
    else:
        logger.debug(f"{indent} mo match for {key}={obj}")
    return tags

def has_obj_value(value, maxdepth, obj, key = None):
    indent=(10-maxdepth)*'-'
    logger.debug(f"{indent} checking {key}={obj}")
    if maxdepth == 0:
        logger.debug(f"{indent} maxdepth reached")
        return False
    if type(obj)==type({}):
        logger.debug(f"{indent} iterating dict ...")
        for key, obj in obj.items():
            if has_obj_value(value, maxdepth-1, obj, key):
                return True
    elif type(obj)==type([]):
        logger.debug(f"{indent} iterating list ...")
        for obj in obj:
            if has_obj_value(value, maxdepth-1, obj):
                return True
    elif obj == value:
        logger.debug(f"{indent} found {key}={obj}")
        return True
    else:
        logger.debug(f"{indent} mo match for {key}={obj}")
    return False
