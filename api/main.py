import os
from fastapi import FastAPI
from typing import List
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware

from api.models.agency import AgencyModel, AgencyRoutesModel
from api.models.route import RouteModel
from api.models.stop import StopModel


app = FastAPI()
if not os.environ.get('MONGODB_API_USER') is None:
  client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{os.environ['MONGODB_API_USER']}:{os.environ['MONGODB_API_USER_PASSWORD']}@mongodb:27017/{os.environ['MONGODB_INITDB_DATABASE']}")
  db = client[os.environ['MONGODB_INITDB_DATABASE']]
else:
  #TODO: Quitar
  client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://apiUser:apiUser@192.168.1.10:27017/gtfs")
  db = client["gtfs"]


# CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=False,
  allow_methods=['*'],
  allow_headers=['*'],
)


@app.get("/agencies", response_description="Obtener todas las agencias", response_model=List[AgencyModel], response_model_exclude_none=True)
async def get_agencies():
  agencias = await db["agencies"].find().to_list(1000)
  return agencias

@app.get("/agencies/routes", response_description="Obtener todas las agencias junto con las lineas de cada una", response_model=List[AgencyRoutesModel], response_model_exclude_none=True)
async def get_agencies():
  agencias = await db["agencies"].aggregate([
      {
        "$lookup": {
          "from": "routes",
          "localField": "_id",
          "foreignField": "agency",
          "as": "routes"
        }
      },
      {
        "$project": {
          "_id": 0,
          "routes": {
            "_id": 0,
            "agency": 0
          }
        }
      }]).to_list(1000)
  return agencias
    
@app.get("/agencies/{id}", response_description="Obtener agencia por agency_id", response_model=AgencyModel, response_model_exclude_none=True)
async def get_agency_id(id: str):
  agencia = await db["agencies"].find_one({"agency_id": id})
  return agencia

@app.get("/routes", response_description="Obtener todas las rutas", response_model=List[RouteModel], response_model_exclude_none=True)
async def get_routes():
  rutas = await db["routes"].aggregate([
    {
      "$lookup": {
        "from": "agencies",
        "localField": "agency",
        "foreignField": "_id",
        "as": "agency"
      }
    },
    {
      "$unwind": "$agency"
    }]).to_list(1000)
  return rutas

@app.get("/routes/{id}", response_description="Obtener ruta por route_id", response_model=RouteModel, response_model_exclude_none=True)
async def get_route_id(id: str):
  ruta = await db["routes"].aggregate([
    {
      "$match": {
        "route_id": id
      }
    },
    {
      "$lookup": {
        "from": "agencies",
        "localField": "agency",
        "foreignField": "_id",
        "as": "agency"
      }
    },
    {
      "$unwind": "$agency"
    }]).to_list(1)
  return ruta[0]

@app.get("/stops", response_description="Obtener todas las paradas", response_model=List[StopModel], response_model_exclude_none=True)
async def get_stops():
  paradas = await db["stops"].find().to_list(1000)
  return paradas

@app.get("/stops/{id}", response_description="Obtener parada por stop_id", response_model=StopModel, response_model_exclude_none=True)
async def get_stop_id(id: str):
  parada = await db["stops"].find_one({"stop_id": id})
  return parada