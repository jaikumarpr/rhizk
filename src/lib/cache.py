import uuid
from pymemcache.client.base import Client
import json

# Configure memcached client
client = Client(('localhost', 11211))

# Helper functions for serialization/deserialization
def json_serializer(key, value):
    if isinstance(value, str):
        return value, 1
    return json.dumps(value), 2

def json_deserializer(key, value, flags):
    if flags == 1:
        return value.decode('utf-8')
    if flags == 2:
        return json.loads(value.decode('utf-8'))
    raise Exception("Unknown serialization format")

# Use these serializer/deserializer with the memcached client
client = Client(('localhost', 11211), serializer=json_serializer, deserializer=json_deserializer)

def add_schedule(schedule):
    id = str(uuid.uuid4())
    client.set(id, schedule)
    return id

def get_schedule(id):
    schedule = client.get(id)
    if schedule is None:
        raise KeyError(f"No schedule found for id: {id}")
    return schedule

def remove_schedule(id):
    client.delete(id)

# Optional: Add a function to check if a schedule exists
def schedule_exists(id):
    return client.get(id) is not None
