"""Read data back and export them to a json file
"""

from bson import ObjectId
import bz2
from databroker import catalog
import json


class ObjectIdEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


uid = "3c256552-7c81-4a1f-bf92-bfec5587cd3a"
uid = "bcf9be93-88e3-46e0-b1e7-3e173756f525"
prefix = "bba-measured"

db = catalog["heavy"]
run = db[uid]
stream = run.primary

# export metadata first
filename = f"{prefix}-{uid}-metadata.json.bz2"
print(f"exporting metadata to {filename}")
with bz2.open(filename, "wt") as json_file:
    json.dump(stream.metadata, json_file, cls=ObjectIdEncoder, indent=4)

# export data
filename = f"{prefix}-{uid}-raw-data.json.bz2"
print(f"exporting data to {filename}")
db = stream.read()
print(f"data came: {db}")
with bz2.open(filename, "wt") as json_file:
    json.dump(db.compute().to_dict(), json_file, cls=ObjectIdEncoder, indent=4)
