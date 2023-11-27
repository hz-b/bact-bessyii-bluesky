# app.py
from fastapi import APIRouter, Body, Request, Response, HTTPException, status, FastAPI, Depends
import numpy as np
from typing import List
from pymongo import MongoClient


from bact_bessyii_bluesky.applib.bba import measure_quad_response
from bact_analysis_bessyii.bba import app as bbaAnalysis
from bact_bessyii_bluesky.applib.bba.measurement_config import MeasurementConfig
from bact_bessyii_mls_ophyd.db.mongo_repository import InitializeMongo

app = FastAPI()
router = APIRouter()

# MongoDB connection
db_init = InitializeMongo()

@router.post('/measurements/', response_model=dict)
async def add_measurement(data: dict, connector: InitializeMongo = Depends(db_init)):
    #extract the input from post service
    prefix = data['prefix']
    currents = np.array(data['currents'])
    catalog_name = data['catalog_name']
    machine_name = data['machine_name']
    measurement_name = data['measurement_name']
    # Perform the measurement and return the uids
    uids =  measure_quad_response.main(prefix, currents,machine_name,catalog_name, measurement_name,try_run=True)

    # Create a MeasurementConfig object
    measurement_config = MeasurementConfig(
        prefix=prefix,
        currents=currents,
        catalog_name=catalog_name,
        machine_name=machine_name,
        measurement_name=measurement_name,
        uids=uids
    )
    print(f"Measurement completed with uid:{uids}")
    #call the bba analysis
    bbaAnalysis.main(uids[0])
    # Store the measurement configuration in MongoDB
    measurement_config.currents = measurement_config.currents.tolist()
    collection = connector.get_collection("measurements")
    collection.insert_one(measurement_config.__dict__)
    # Return the uids as a response
    return {'uids': uids}


@router.get("/measurements", response_description="List all measurements", response_model=list)
async def get_configurations(connector: InitializeMongo = Depends(db_init)):
    collection = connector.get_collection("measurements")
    configurations = list(collection.find(limit=100))
    return configurations

@router.get("/favicon.ico")
async def favicon():
    return ""
# app.include_router(router, tags=["index"], prefix="")
app.include_router(router, tags=["measurements"], prefix="/measurements")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
