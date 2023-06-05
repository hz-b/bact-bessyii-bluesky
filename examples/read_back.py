from databroker import catalog

db = catalog["heavy"]
uid = '3c256552-7c81-4a1f-bf92-bfec5587cd3a'
run = db[uid]
stream =run.primary
dataX = stream.read()
print(f"data came: {dataX}")

print(dataX.bpm_elem_data[2])
