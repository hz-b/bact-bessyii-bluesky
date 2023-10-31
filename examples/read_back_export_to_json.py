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


db = catalog["heavy_local"]
uid = "3c256552-7c81-4a1f-bf92-bfec5587cd3a"
uid = "bcf9be93-88e3-46e0-b1e7-3e173756f525"
run = db[uid]
stream = run.primary
db = stream.read()
print(f"data came: {db}")


filename = f"bba-measured-raw-data-{uid}.json.bz2"
with bz2.open(filename, "wt") as json_file:
    json.dump(db.to_dict(), json_file, cls=ObjectIdEncoder, indent=4)
