from flask import current_app
import shelve


def shelve_it(func):
    def new_func(param):
        key = str(func.__code__) + param
        file_name = current_app.config["CACHE_URL"]
        with shelve.open(file_name) as d:
            if key not in d:
                d[key] = func(param)
            return d[key]

    return new_func
