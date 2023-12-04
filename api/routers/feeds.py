from fastapi import APIRouter, Response
from api.db import db

from typing import List

from api.models.feed import FeedModel


router = APIRouter(prefix="/feeds")


@router.get("/", response_description="Obtener feeds", response_model=List[FeedModel], response_model_exclude_none=True)
async def get_feeds(response: Response):
  try:
    proyeccion = {
      "idFeed": 1,
      "nombre": 1,
      "fuentes": 1,
      "info": 1,
      "atribuciones": 1,
      "agencias": {
        "$map": {
          "input": "$agencias",
          "as": "agencia",
          "in": {
            "id": "$$agencia._id",
            "nombre": "$$agencia.nombre"
          }
        }
      },
      "lineas": {
        "$map": {
          "input": "$lineas",
          "as": "linea",
          "in": {
            "id": "$$linea._id",
            "nombreCorto": "$$linea.nombreCorto",
            "nombreLargo": "$$linea.nombreLargo"
          }
        }
      },
      "viajes": {
        "$map": {
          "input": "$viajes",
          "as": "viaje",
          "in": {
            "id": "$$viaje._id",
            "nombre": "$$viaje.nombre"
          }
        }
      }
    }

    feeds = await db.aggregate("feeds", [
      {
        '$lookup': {
          'from': 'agencias', 
          'localField': 'atribuciones.idAgencia', 
          'foreignField': '_id', 
          'as': 'agencias'
        }
      },
      {
        '$lookup': {
          'from': 'lineas', 
          'localField': 'atribuciones.idLinea', 
          'foreignField': '_id', 
          'as': 'lineas'
        }
      },
      {
        '$lookup': {
          'from': 'viajes', 
          'localField': 'atribuciones.idViaje', 
          'foreignField': '_id', 
          'as': 'viajes'
        }
      },
      {
        '$project': proyeccion
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(feeds) == 0:
      response.status_code = 204
    return feeds
  

@router.get("/tiempoReal", response_description="Obtener feeds con tiempo real", response_model=List[FeedModel], response_model_exclude_none=True)
async def get_feeds_tr(response: Response):
  try:
    feeds = await db.find("feeds", {"tiempoReal": {"$exists": True}}, projection={"idFeed": 1, "nombre": 1, "tiempoReal": 1})
  except:
    response.status_code = 500
    return []
  else:
    if len(feeds) == 0:
      response.status_code = 204
    return feeds