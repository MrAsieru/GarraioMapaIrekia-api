from fastapi import APIRouter, Response
from api.db import db

from typing import List

from api.models.parada import ParadaModel
from api.models.viaje import ViajeModel


router = APIRouter(prefix="/viajes")


@router.get("/{id}", response_description="Obtener viaje por idViaje", response_model=ViajeModel, response_model_exclude_none=True)
async def get_viaje(id: str, response: Response, incluirHorarios: bool = False, incluirParadas: bool = False, incluirFechas: bool = False, incluirFrecuencias: bool = False):
  try:
    proyeccion = {
      "_id": 0
    }
    if not incluirHorarios:
      proyeccion["horarios"] = 0
    if not incluirParadas:
      proyeccion["paradas"] = 0
    if not incluirFechas:
      proyeccion["fechas"] = 0
    if not incluirFrecuencias:
      proyeccion["frecuencias"] = 0
    
    parada = await db.find_one("viajes", {"_id": id}, projection=proyeccion)
  except:
    response.status_code = 500
    return []
  else:
    if len(parada) == 0:
      response.status_code = 204
    return parada


@router.get("/{id}/paradas", response_description="Obtener paradas de idViaje", response_model=List[ParadaModel], response_model_exclude_none=True)
async def get_viaje_paradas(id: str, response: Response):
  try:
    paradas = await db.aggregate("viajes", [
      {
        '$match': {
          '_id': id
        }
      },
      {
        '$lookup': {
          'from': 'paradas', 
          'localField': 'paradas', 
          'foreignField': '_id', 
          'as': 'paradas'
        }
      },
      {
        '$unwind': '$paradas'
      },
      {
        '$replaceRoot': {
          'newRoot': '$paradas'
        }
      },
      {
        '$project': {
          '_id': 0, 
          'lineas': 0, 
          'viajes': 0
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