from lib.cache import shelve_it
from uuid import uuid4

def test_cache():

    @shelve_it
    def get_data(_):
        return uuid4() 

    id = "123"
    first = get_data(id) 
    second = get_data(id)
    assert first == second
