from fastapi import APIRouter, Response
from api.db import db

from typing import List
from datetime import datetime, timedelta

from api.models.agencia import AgenciaModel
from api.models.linea import LineaModel
from api.models.parada import ParadaModel, ViajeParadaModel


router = APIRouter(prefix="/paradas")


@router.get("/", response_description="Obtener todas las paradas", response_model=List[ParadaModel], response_model_exclude_none=True)
async def get_paradas(response: Response, incluirLineas: bool = False, incluirViajes: bool = False, incluirAgencias: bool = False):
  try:
    proyeccion = {
      "_id": 0
    }
    if not incluirLineas:
      proyeccion["lineas"] = 0
    if not incluirViajes:
      proyeccion["viajes"] = 0
    if not incluirAgencias:
      proyeccion["agencias"] = 0
    paradas = await db.find("paradas", projection=proyeccion)
  except:
    response.status_code = 500
    return []
  else:
    if len(paradas) == 0:
      response.status_code = 204
    return paradas


@router.get("/{id}", response_description="Obtener parada por stop_id", response_model=ParadaModel, response_model_exclude_none=True)
async def get_parada(id: str, response: Response, incluirLineas: bool = False, incluirViajes: bool = False, incluirAgencias: bool = False):
  try:
    proyeccion = {
      "_id": 0
    }
    if not incluirLineas:
      proyeccion["lineas"] = 0
    if not incluirViajes:
      proyeccion["viajes"] = 0
    if not incluirAgencias:
      proyeccion["agencias"] = 0
    parada = await db.find_one("paradas", {"_id": id}, projection=proyeccion)
  except:
    response.status_code = 500
    return []
  else:
    if not parada:
      response.status_code = 204
    return parada


@router.get("/{id}/lineas", response_description="Obtener lineas de idParada", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_parada_lineas(id: str, response: Response, incluirViajes: bool = False, incluirPatrones: bool = False, incluirParadas: bool = False):
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
    lineas = await db.aggregate("paradas", [
      {
        '$match': {
          '_id': id
        }
      },
      {
        '$lookup': {
          'from': 'lineas', 
          'localField': 'lineas', 
          'foreignField': '_id', 
          'as': 'lineas'
        }
      },
      {
        '$project': {
          'lineas': 1
        }
      },
      {
        '$unwind': '$lineas'
      },
      {
        '$replaceRoot': {
            'newRoot': '$lineas'
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
    if len(lineas) == 0:
      response.status_code = 204
    return lineas


@router.get("/{id}/horarios", response_description="Obtener horarios de idParada", response_model=List[ViajeParadaModel], response_model_exclude_none=True)
async def get_parada_horarios(id: str, response: Response, desde: datetime = None, hasta: datetime = None):
  try:
    # Establecer valores predeterminados
    if desde is None:
      desde = datetime.utcnow()
    if hasta is None:
      hasta = desde + timedelta(hours=2)
    
    print(f"Fecha: {desde}, hasta: {hasta}")

    documentos = await db.aggregate("paradas", [
      {
        '$match': {
          '$or': [
            {
              '_id': id
            },
            {
              'paradaPadre': id
            }
          ]
        }
      },
      {
        '$lookup': {
          'from': 'viajes', 
          'localField': 'viajes', 
          'foreignField': '_id', 
          'as': 'viajes'
        }
      },
      {
        '$unwind': {
          'path': '$viajes'
        }
      },
      {
        '$lookup': {
          'from': 'agencias', 
          'localField': 'viajes.idAgencia', 
          'foreignField': '_id', 
          'as': 'viajes.agencia'
        }
      },
      {
        '$addFields': {
          'viajes.idParada': '$_id'
        }
      },
      {
        '$replaceRoot': {
          'newRoot': '$viajes'
        }
      },
      {
        '$unwind': {
          'path': '$agencia', 
          'preserveNullAndEmptyArrays': False
        }
      },
      {
        '$addFields': {
          'zonaHoraria': '$agencia.zonaHoraria',
          'desdeFechaLocal': {
            '$dateFromParts': {
              'year': {
                '$year': {
                  'date': desde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'month': {
                '$month': {
                  'date': desde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'day': {
                '$dayOfMonth': {
                  'date': desde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }
            }
          },
          'hastaFechaLocal': {
            '$dateFromParts': {
              'year': {
                '$year': {
                  'date': hasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'month': {
                '$month': {
                  'date': hasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'day': {
                '$dayOfMonth': {
                  'date': hasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }
            }
          },
          'desdeHoraLocal': {
            '$dateToString': {
              'date': desde, 
              'format': '%H:%M:%S', 
              'timezone': '$agencia.zonaHoraria'
            }
          },
          'hastaHoraLocal': {
            '$dateToString': {
              'date': hasta, 
              'format': '%H:%M:%S', 
              'timezone': '$agencia.zonaHoraria'
            }
          }
        }
      },
      {
        '$match': {
          '$expr': {
            '$or': [
              {
                '$in': [
                  {
                    '$dateFromParts': {
                      'year': {
                        '$year': {
                          'date': desde, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'month': {
                        '$month': {
                          'date': desde, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'day': {
                        '$dayOfMonth': {
                          'date': desde, 
                          'timezone': '$zonaHoraria'
                        }
                      }
                    }
                  }, '$fechas'
                ]
              }, {
                '$in': [
                  {
                    '$dateFromParts': {
                      'year': {
                        '$year': {
                          'date': hasta, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'month': {
                        '$month': {
                          'date': hasta, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'day': {
                        '$dayOfMonth': {
                          'date': hasta, 
                          'timezone': '$zonaHoraria'
                        }
                      }
                    }
                  }, '$fechas'
                ]
              }
            ]
          }
        }
      },
      {
        '$addFields': {
          'horario': {
            '$filter': {
              'input': '$horarios', 
              'as': 'horario', 
              'cond': {
                '$and': [
                  {
                    '$eq': [
                      '$$horario.idParada', "$idParada"
                    ]
                  },
                  {
                    '$cond': {
                      'if': {
                        '$in': [
                            '$desdeFechaLocal', '$fechas'
                        ]
                      }, 
                      'then': {
                        '$cond': {
                          'if': {
                            '$in': [
                              '$hastaFechaLocal', '$fechas'
                            ]
                          }, 
                          'then': {
                            '$cond': {
                              'if': {
                                '$lt': [
                                  '$desdeHoraLocal', { '$ifNull': [ "$$horario.horaSalida", "$$horario.horaLlegada" ] }
                                ]
                              }, 
                              'then': {
                                '$cond': {
                                  'if': {
                                    '$lt': [
                                      { '$ifNull': [ "$$horario.horaSalida", "$$horario.horaLlegada" ] }, '$hastaHoraLocal'
                                    ]
                                  }, 
                                  'then': 1, 
                                  'else': {
                                    '$lt': [
                                      '$hastaHoraLocal', '$desdeHoraLocal'
                                    ]
                                  }
                                }
                              }, 
                              'else': {
                                '$cond': {
                                  'if': {
                                    '$lt': [
                                      { '$ifNull': [ "$$horario.horaSalida", "$$horario.horaLlegada" ] }, '$hastaHoraLocal'
                                    ]
                                  }, 
                                  'then': {
                                    '$lt': [
                                      '$hastaHoraLocal', '$desdeHoraLocal'
                                    ]
                                  }, 
                                  'else': 0
                                }
                              }
                            }
                          }, 
                          'else': {
                            '$lt': [
                              '$desdeHoraLocal', { '$ifNull': [ "$$horario.horaSalida", "$$horario.horaLlegada" ] }
                            ]
                          }
                        }
                      }, 
                      'else': {
                        '$cond': {
                          'if': {
                            '$in': [
                              '$hastaFechaLocal', '$fechas'
                            ]
                          }, 
                          'then': {
                            '$lt': [
                              { '$ifNull': [ "$$horario.horaSalida", "$$horario.horaLlegada" ] }, '$hastaHoraLocal'
                            ]
                          }, 
                          'else': False
                        }
                      }
                    }
                  }
                ]
              }
            }
          }
        }
      },
      {
        '$match': {
          'horario': {
            '$ne': []
          }
        }
      },
      {
        '$unwind': {
          'path': "$horario"
        }
      },
      {
        '$project': {
          'agencia': 0,
          'paradas': 0, 
          'fechas': 0,
          'horarios': 0
        }
      }
    ]) 
  except:
    response.status_code = 500
    return []
  else:
    if len(documentos) == 0:
      response.status_code = 204
    return documentos


@router.get("/{id}/agencias", response_description="Obtener agencias de idParada", response_model=List[AgenciaModel], response_model_exclude_none=True)
async def get_parada_agencias(id: str, response: Response):
  try:
    documentos = await db.aggregate("paradas", [
      {
        '$match': {
          '$or': [
            {
              '_id': id
            },
            {
              'paradaPadre': id
            }
          ], 
          'agencias': {
            '$exists': True
          }
        }
      },
      {
        '$unwind': '$agencias'
      },
      {
        '$group': {
          '_id': '$agencias'
        }
      },
      {
        '$lookup': {
          'from': 'agencias', 
          'localField': '_id', 
          'foreignField': '_id', 
          'as': 'agencia'
        }
      },
      {
        '$unwind': '$agencia'
      },
      {
        '$replaceRoot': {
          'newRoot': '$agencia'
        }
      },
      {
        '$project': {
          '_id': 0, 
          'lineas': 0
        }
      }
    ])
  except:
    response.status_code = 500
    return []
  else:
    if len(documentos) == 0:
      response.status_code = 204
    return documentos