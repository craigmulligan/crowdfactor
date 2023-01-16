import logging
from lib.db import DB
import pickle

def shelve_it(func):
    def new_func(param):
        key = str(func.__code__) + "-" + param
        db = DB.get_db()
        result = db.get_cache(key)

        if result is None:
            value = func(param)
            db.insert_cache(key, pickle.dumps(value))
            return value 

        v = result["value"]
        return pickle.loads(v)

    return new_func
