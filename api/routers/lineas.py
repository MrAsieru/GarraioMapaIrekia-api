from fastapi import APIRouter, Response
from api.db import db

from typing import List

from api.models.linea import LineaModel, RespuestaPatronLineaModel
from api.models.parada import ParadaModel


router = APIRouter(prefix="/lineas")


@router.get("/", response_description="Obtener todas las rutas", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_lineas(response: Response):
  try:
    rutas = await db.aggregate("lineas", [
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
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(rutas) == 0:
      response.status_code = 204
    return rutas


@router.get("/{id}", response_description="Obtener ruta por idLinea", response_model=LineaModel, response_model_exclude_none=True)
async def get_linea(id: str, response: Response, incluirViajes: bool = False, incluirPatrones: bool = False, incluirParadas: bool = False):
  try:
    proyeccion = {
      "_id": 0
    }
    if not incluirViajes:
      proyeccion["viajes"] = 0
    if not incluirPatrones:
      proyeccion["patrones"] = 0
    if not incluirParadas:
      proyeccion["paradas"] = 0
    ruta = await db.find_one("lineas", {"_id": id}, proyeccion)
  except:
    response.status_code = 500
    return []
  else:
    if not ruta:
      response.status_code = 204
    return ruta


@router.get("/{id}/paradas", response_description="Obtener paradas de idLinea", response_model=List[ParadaModel], response_model_exclude_none=True)
async def get_linea_paradas(id: str, response: Response):
  try:
    paradas = await db.aggregate("lineas", [
      {
        "$match": {
          "_id": id
        }
      },
      {
        "$lookup": {
          "from": "paradas",
          "localField": "paradas",
          "foreignField": "_id",
          "as": "paradas"
        }
      },
      {
        "$unwind": "$paradas"
      },
      {
        "$replaceRoot": {
          "newRoot": "$paradas"
        }
      },
      {
        "$project": {
          "_id": 0,
          "lineas": 0,
          "viajes": 0
        }
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(paradas) == 0:
      response.status_code = 204
    return paradas


@router.get("/{id}/patrones", response_description="Obtener patrones de idLinea", response_model=List[RespuestaPatronLineaModel], response_model_exclude_none=True)
async def get_linea_patrones(id: str, response: Response):
  try:
    patrones = await db.aggregate("lineas", [
      {
        '$match': {
          '_id': id
        }
      },
      {
        '$unwind': {
          'path': '$patrones'
        }
      },
      {
        '$replaceRoot': {
          'newRoot': '$patrones'
        }
      },
      {
        '$addFields': {
          'numViajes': {
            '$size': '$viajes'
          }
        }
      },
      {
        '$project': {
          'viajes': 0
        }
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(patrones) == 0:
      response.status_code = 204
    return patrones