from fastapi import APIRouter, Response
from api.db import db

from datetime import datetime

from api.models.posicion import PosicionesModel, PosicionesRequestModel


router = APIRouter(prefix="/posiciones")


@router.post("/", response_description="Obtener posiciones de los vehiculos para la fecha y agencias solicitadas", response_model=PosicionesModel, response_model_exclude_none=True)
async def get_posiciones(datos: PosicionesRequestModel, response: Response):
  try:
    documentos = await db.aggregate("posiciones", [
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
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(documentos) == 0:
      response.status_code = 204
    return documentos[0]