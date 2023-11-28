from fastapi import APIRouter, Response
from api.db import db

from typing import List

from api.models.agencia import AgenciaLineasModel, AgenciaModel
from api.models.linea import LineaModel


router = APIRouter(prefix="/agencias")


@router.get("/", response_description="Obtener todas las agencias", response_model=List[AgenciaModel], response_model_exclude_none=True)
async def get_agencias(response: Response):
  try:
    agencias = await db.aggregate("agencias", [
      {
        "$project": {
          "_id": 0,
          "lineas": 0
        }
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(agencias) == 0:
      response.status_code = 204
    return agencias


@router.get("/lineas", response_description="Obtener todas las agencias junto con las lineas de cada una", response_model=List[AgenciaLineasModel], response_model_exclude_none=True)
async def get_agencias_lineas(response: Response):
  try:
    agencias = await db.aggregate("agencias", [
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
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(agencias) == 0:
      response.status_code = 204
    return agencias


@router.get("/{id}", response_description="Obtener agencia por idAgencia", response_model=AgenciaModel, response_model_exclude_none=True)
async def get_agencia(id: str, response: Response):
  try:
    proyeccion = {
      "_id": 0,
      "lineas": 0
    }
    agencia = await db.find_one("agencias", {"_id": id}, projection=proyeccion)
  except:
    response.status_code = 500
    return []
  else:
    if len(agencia) == 0:
      response.status_code = 204
    return agencia
  

@router.get("/{id}/lineas", response_description="Obtener lineas de idAgencia", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_agenca_lineas(id: str, response: Response):
  try:
    lineas = await db.aggregate("agencias", [
      {
        "$match": {
          "_id": id
        }
      },
      {
        "$lookup": {
          "from": "lineas",
          "localField": "lineas",
          "foreignField": "_id",
          "as": "lineas"
        }
      },
      {
        "$unwind": "$lineas"
      },
      {
        "$replaceRoot": {
          "newRoot": "$lineas"
        }
      },
      {
        "$project": {
          "_id": 0,
          "viajes": 0,
          "paradas": 0
        }
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(lineas) == 0:
      response.status_code = 204
    return lineas