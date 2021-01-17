from collections import defaultdict
from pymongo import MongoClient

import datetime


def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def to_time_stamp(date_time):
    return datetime.datetime.timestamp(date_time)


def date_to_seasion(time):
    y = time.strftime("%y")
    m = time.strftime("%m")
    if (m > 3 and m < 9):
        k = "1"
    else:
        k = "2"
    return str(y) + k


mongo = MongoClient(host="localhost", port=27019)

b4e_db = mongo["B4E_School_Backend"]
b4e_collection = b4e_db["b4e_records"]
b4e_actor_collection = b4e_db["b4e_actors"]

key = {"record_type": "CERTIFICATE"}
records = b4e_collection.find(key)
groups = defaultdict(list)
for obj in records:
    print(timestamp_to_datetime(obj.get('timestamp')))
    groups[obj['manager_public_key']].append(obj)

new_list = groups.values()
print(len(groups))
print(groups.get('0381fc95b27642fe5ae130657f9a9561c313f48d4830a41d6ebb81f16d8920b374'))
