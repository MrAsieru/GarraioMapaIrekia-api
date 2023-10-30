from datetime import datetime
import os
from fastapi import FastAPI
from typing import List
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from api.models.agencia import AgenciaModel, AgenciaLineasModel
from api.models.posicion import PosicionesModel, PosicionesRequestModel
from api.models.linea import LineaModel
from api.models.parada import ParadaModel


app = FastAPI()
if not os.environ.get('MONGODB_API_USER') is None:
  client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{os.environ['MONGODB_API_USER']}:{os.environ['MONGODB_API_USER_PASSWORD']}@mongodb:27017/{os.environ['MONGODB_INITDB_DATABASE']}", tz_aware=True)
  db = client[os.environ['MONGODB_INITDB_DATABASE']]
else:
  #TODO: Quitar
  client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://apiUser:apiUser@192.168.1.10:27017/gtfs", tz_aware=True)
  db = client["gtfs"]


# CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=False,
  allow_methods=['*'],
  allow_headers=['*'],
)


@app.get("/agencias", response_description="Obtener todas las agencias", response_model=List[AgenciaModel], response_model_exclude_none=True)
async def get_agencies():
  agencias = await db["agencias"].aggregate([
    {
      "$project": {
        "_id": 0,
        "lineas": 0
      }
    }]).to_list(1000)
  return agencias

@app.get("/agencias/lineas", response_description="Obtener todas las agencias junto con las lineas de cada una", response_model=List[AgenciaLineasModel], response_model_exclude_none=True)
async def get_agencies():
  agencias = await db["agencias"].aggregate([
      {
        "$lookup": {
          "from": "lineas",
          "localField": "lineas",
          "foreignField": "_id",
          "as": "lineas"
        }
      },
      {
        "$project": {
          "_id": 0,
          "lineas": {
            "_id": 0,
            "viajes": 0,
            "paradas": 0
          }
        }
      }]).to_list(1000)
  return agencias
    
@app.get("/agencias/{id}", response_description="Obtener agencia por idAgencia", response_model=AgenciaModel, response_model_exclude_none=True)
async def get_agency_id(id: str):
  proyeccion = {
    "_id": 0,
    "lineas": 0
  }
  agencia = await db["agencias"].find_one({"_id": id}, projection=proyeccion)
  return agencia

@app.get("/lineas", response_description="Obtener todas las rutas", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_routes():
  rutas = await db["lineas"].aggregate([
    {
      "$lookup": {
        "from": "agencias",
        "localField": "idAgencia",
        "foreignField": "_id",
        "as": "agencia"
      }
    },
    {
      "$unwind": "$agencia"
    },
    {
      "$project": {
        "_id": 0,
        "agencia": {
          "_id": 0,
          "lineas": 0
        },
        "viajes": 0,
        "paradas": 0
      }
    }]).to_list(1000)
  return rutas

@app.get("/lineas/{id}", response_description="Obtener ruta por idLinea", response_model=LineaModel, response_model_exclude_none=True)
async def get_route_id(id: str):
  ruta = await db["lineas"].aggregate([
    {
      "$match": {
        "_id": id
      }
    },
    {
      "$lookup": {
        "from": "agencias",
        "localField": "idAgencia",
        "foreignField": "_id",
        "as": "agencia"
      }
    },
    {
      "$unwind": "$agencia"
    },
    {
      "$project": {
        "_id": 0,
        "agencia": {
          "_id": 0,
          "lineas": 0
        },
        "viajes": 0,
        "paradas": 0
      }
    }]).to_list(1)
  return ruta[0]

@app.get("/paradas", response_description="Obtener todas las paradas", response_model=List[ParadaModel], response_model_exclude_none=True)
async def get_stops():
  proyeccion = {
    "_id": 0,
    "lineas": 0,
    "viajes": 0
  }
  paradas = await db["paradas"].find(projection=proyeccion).to_list(1000)
  return paradas

@app.get("/paradas/{id}", response_description="Obtener parada por stop_id", response_model=ParadaModel, response_model_exclude_none=True)
async def get_stop_id(id: str):
  proyeccion = {
    "_id": 0,
    "lineas": 0,
    "viajes": 0
  }
  parada = await db["paradas"].find_one({"_id": id}, projection=proyeccion)
  return parada

@app.post("/posicionesVehiculos", response_description="Obtener posiciones de los vehiculos para la fecha y agencias solicitadas", response_model=PosicionesModel, response_model_exclude_none=True)
async def get_posicionesVehiculos(datos: PosicionesRequestModel):
  documentos = await db["posiciones"].aggregate([
    {
      '$match': {
        'fecha': datetime.fromisoformat(datos.fecha), 
        'idAgencia': {
          '$in': datos.agencias
        }
      }
    },
    {
      '$group': {
        '_id': None, 
        'fecha': {
          '$first': '$fecha'
        }, 
        'agencias': {
          '$push': '$$ROOT'
        }
      }
    },
    {
      '$project': {
        '_id': 0, 
        'agencias': {
          '_id': 0, 
          'fecha': 0
        }
      }
    }]).to_list(1)
  print(documentos[0])
  return documentos[0]
