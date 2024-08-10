import uuid


cache = {}

def cache_schedule(schedule):
    id = str(uuid.uuid4())
    cache[id] = schedule
    return id

def get_schedule(id):
    return cache[id]
    

