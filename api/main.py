from datetime import datetime, time
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
import pytz
import requests
import asyncio

from api.models.agencia import AgenciaModel, AgenciaLineasModel
from api.models.feed import FeedModel
from api.models.posicion import PosicionesModel, PosicionesRequestModel
from api.models.linea import LineaModel, RespuestaPatronLineaModel
from api.models.parada import ViajeParadaModel, ParadaModel


app = FastAPI()
if not os.environ.get('MONGODB_API_USER') is None:
  db_client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{os.environ['MONGODB_API_USER']}:{os.environ['MONGODB_API_USER_PASSWORD']}@mongodb:27017/{os.environ['MONGODB_INITDB_DATABASE']}", tz_aware=True)
  db = db_client[os.environ['MONGODB_INITDB_DATABASE']]
else:
  #TODO: Quitar
  db_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://apiUser:apiUser@192.168.1.10:27017/gtfs", tz_aware=True)
  db = db_client["gtfs"]


# CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=False,
  allow_methods=['*'],
  allow_headers=['*'],
)

# Feeds con tiempo real
@app.get("/feeds/tiempoReal", response_description="Obtener feeds con tiempo real", response_model=List[FeedModel], response_model_exclude_none=True)
async def get_feeds_tr():
  feeds = await db["feeds"].find({"tiempoReal": {"$exists": True}}, projection={"idFeed": 1, "tiempoReal": 1}).to_list(1000)
  return feeds


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

@app.get("/agencias/{id}/lineas", response_description="Obtener lineas de idAgencia", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_agency_lines(id: str):
  lineas = await db["agencias"].aggregate([
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
    }]).to_list(1000)
  return lineas

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
  ruta = await db["lineas"].find_one(
    {
      "_id": id
    },
    {
      "_id": 0,
      "viajes": 0,
      "paradas": 0,
      "patrones": 0
    })
  return ruta

@app.get("/lineas/{id}/paradas", response_description="Obtener paradas de idLinea", response_model=List[ParadaModel], response_model_exclude_none=True)
async def get_route_stops(id: str):
  paradas = await db["lineas"].aggregate([
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
    }]).to_list(1000)
  return paradas

@app.get("/lineas/{id}/patrones", response_description="Obtener patrones de idLinea", response_model=List[RespuestaPatronLineaModel], response_model_exclude_none=True)
async def get_route_patterns(id: str):
  patrones = await db["lineas"].aggregate([
    {
      '$match': {
        '_id': 'Bizkaibus_651'
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
  ]).to_list(1000)
  return patrones

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

@app.get("/paradas/{id}/lineas", response_description="Obtener lineas de idParada", response_model=List[LineaModel], response_model_exclude_none=True)
async def get_stop_lines_colors(id: str):
  lineas = await db["paradas"].aggregate([
    {
        '$match': {
            '_id': id
        }
    }, {
        '$lookup': {
            'from': 'lineas', 
            'localField': 'lineas', 
            'foreignField': '_id', 
            'as': 'lineas'
        }
    }, {
        '$project': {
            'lineas': 1
        }
    }, {
        '$unwind': '$lineas'
    }, {
        '$replaceRoot': {
            'newRoot': '$lineas'
        }
    }, {
        '$project': {
            'viajes': 0, 
            'paradas': 0
        }
    }
  ]).to_list(1000)
  return lineas

@app.get("/paradas/{id}/horarios", response_description="Obtener horarios de idParada", response_model=List[ViajeParadaModel], response_model_exclude_none=True)
async def get_stop_schedules(id: str, desde: datetime = datetime.utcnow(), hasta: datetime = None):
  # Change desde to UTC
  desde = desde.astimezone(pytz.utc)
  if hasta is None:
    hasta = desde + timedelta(hours=2)
  hasta = hasta.astimezone(pytz.utc)
  print(f"Fecha: {desde}, hasta: {hasta}")
  print(f"{desde.replace(hour=23, minute=59, second=59)}, {hasta.replace(hour=0, minute=0, second=0)}")

  def aggregate_horarios(fDesde: datetime, fHasta: datetime):
    return [
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
                  'date': fDesde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'month': {
                '$month': {
                  'date': fDesde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'day': {
                '$dayOfMonth': {
                  'date': fDesde, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }
            }
          },
          'hastaFechaLocal': {
            '$dateFromParts': {
              'year': {
                '$year': {
                  'date': fHasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'month': {
                '$month': {
                  'date': fHasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }, 
              'day': {
                '$dayOfMonth': {
                  'date': fHasta, 
                  'timezone': '$agencia.zonaHoraria'
                }
              }
            }
          },
          'desdeHoraLocal': {
            '$dateToString': {
              'date': fDesde, 
              'format': '%H:%M:%S', 
              'timezone': '$agencia.zonaHoraria'
            }
          },
          'hastaHoraLocal': {
            '$dateToString': {
              'date': fHasta, 
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
                          'date': fDesde, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'month': {
                        '$month': {
                          'date': fDesde, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'day': {
                        '$dayOfMonth': {
                          'date': fDesde, 
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
                          'date': fHasta, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'month': {
                        '$month': {
                          'date': fHasta, 
                          'timezone': '$zonaHoraria'
                        }
                      }, 
                      'day': {
                        '$dayOfMonth': {
                          'date': fHasta, 
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
    ]

  documentos = await db["paradas"].aggregate(aggregate_horarios(desde, hasta)).to_list(1000)    
  return documentos

@app.get("/paradas/{id}/agencias", response_description="Obtener agencias de idParada", response_model=List[AgenciaModel], response_model_exclude_none=True)
async def get_stop_agencies(id: str):
  documentos = await db["paradas"].aggregate([
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
  ]).to_list(1000)
  return documentos

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
  return documentos[0]


websocket_clients = []
lista_feeds = {} # {idFeed: {suscripciones: [websocket], tiempoReal: [{url: str, data: bytes|None, modificado: str|None}]}}


async def descargar_tiempo_real(fuente_tr: dict) -> (dict, str):
  print(f"Fetching real-time data from {fuente_tr['url']}")
  try:
    # Establecer cabeceras para evitar descargar datos si no han sido modificados
    headers = {}
    if fuente_tr["modificado"] is not None:
      headers["If-Modified-Since"] = fuente_tr["modificado"]
    
    # Descargar datos
    response = requests.get(fuente_tr["url"], headers=headers)
    response.raise_for_status()
    print("Data fetched successfully")

    if response.status_code == 304:
      # Si los datos no han sido modificados, devolver None
      print("Datos no modificados")
      return None, None
    else:
      ultima_modificacion = response.headers["Last-Modified"] if "Last-Modified" in response.headers else datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
      return response.content, ultima_modificacion
  except requests.exceptions.RequestException as e:
    print(f"Error fetching real-time data: {e}")
    return None


async def actualizar_tiempo_real(idFeed: str):
  print(f"Updating feed {idFeed}")

  # Actualizar solamente feeds con suscriptores
  if len(lista_feeds[idFeed]["suscripciones"]) > 0:
    actualizar = False
    # Recorrer todas las fuentes de tiempo real del feed
    for fuente_tr in lista_feeds[idFeed]["tiempoReal"]:
      new_data, modificado = await descargar_tiempo_real(fuente_tr)

      # Si se obtuvieron datos nuevos, actualizarlos
      if new_data is not None:
        fuente_tr["data"] = new_data
        fuente_tr["modificado"] = modificado
        actualizar = True

    if actualizar:
      for client in lista_feeds[idFeed]["suscripciones"]:
        await enviar_datos(client, idFeed)


async def repeticion():
  while True:
    print("Updating real-time data")
    for idFeed in lista_feeds.keys():
      await actualizar_tiempo_real(idFeed)
    await asyncio.sleep(15)


async def enviar_datos(websocket: WebSocket, idFeed: str):
  global lista_feeds
  print(f"Sending {idFeed} data to client {websocket}")
  # Formato de mensaje binario: [Longitud idFeed (2 Bytes)][idFeed (x Bytes)][Protobuf (y Bytes)]
  # Calcular y codificar longitud del idFeed
  idFeedLen = len(idFeed).to_bytes(2, byteorder="big")

  # Agrupar datos existentes
  datos = b""
  for fuente_tr in lista_feeds[idFeed]["tiempoReal"]:
    if fuente_tr["data"] is not None:
      datos += fuente_tr["data"]

  # Crear mensaje y enviarlo
  await websocket.send_bytes(idFeedLen + idFeed.encode(encoding="utf-8") + datos)


async def agregar_suscripciones(feeds_cliente: list[str], websocket: WebSocket):
  global lista_feeds
  print("Suscribiendo websocket")
  # Recibir ids de feeds que contengan datos en tiempoReal, donde tiempoReal si existe es una url
  feeds_nuevos = list(set(feeds_cliente) - set(lista_feeds.keys()))

  if len(feeds_nuevos) > 0:
    feeds_validos = await db["feeds"].find({"_id": {"$in": feeds_nuevos}, "tiempoReal": {"$exists": True}}, projection={"_id": 1, "tiempoReal": 1}).to_list(1000)
    
    # Crear diccionario con _id como key
    feeds_validos_dict = {feed["_id"]: feed for feed in feeds_validos}
  
  # Feeds a los que se quiere suscribir el cliente y forman parte del sistema
  feeds_cliente = list(set(feeds_cliente) - set([feed for feed in feeds_nuevos if feed not in feeds_validos_dict.keys()]))

  # Recorrer feeds validos (que tengan datos en tiempo real)
  for feed in feeds_cliente:
    # Si el feed no existe en feeds_rt, crearlo
    creado = False
    if feed not in lista_feeds.keys():
      creado = True
      lista_feeds[feed] = {"suscripciones": [], "tiempoReal": []}
      # Obtener url de feed desde feeds_validos siendo feed igual a _id

      for url in feeds_validos_dict[feed]["tiempoReal"]:
        lista_feeds[feed]["tiempoReal"].append({"url": url, "data": None, "modificado": None})
    
    # Añadir websocket a la lista de suscripciones del feed
    lista_feeds[feed]["suscripciones"].append(websocket)

    # Si el feed es nuevo, descargar datos
    if creado:
      await actualizar_tiempo_real(feed)
    else:
      await enviar_datos(websocket, feed)
  print([f"{f} - {len(lista_feeds[f]['suscripciones'])} suscriptores\n" for f in lista_feeds.keys()])


async def eliminar_suscripciones(feeds_cliente: list[str], websocket: WebSocket):
  print(f"Eliminando suscripciones {websocket}")
  for feed in feeds_cliente:
    if feed in lista_feeds.keys():
      l = len(lista_feeds[feed]["suscripciones"])
      try:
        lista_feeds[feed]["suscripciones"].remove(websocket)
      except ValueError:
        pass
      if len(lista_feeds[feed]["suscripciones"]) == 0:
        del lista_feeds[feed]
  print([f"{f} - {len(lista_feeds[f]['suscripciones'])} suscriptores\n" for f in lista_feeds.keys()])


async def actualizar_suscripciones(feeds_actuales: list[str], feeds_nuevos: list[str], websocket: WebSocket):
  # Obtener feeds a eliminar y feeds a agregar, no hacer nada con los que ya estan
  feeds_eliminar = list(set(feeds_actuales) - set(feeds_nuevos))
  feeds_agregar = list(set(feeds_nuevos) - set(feeds_actuales))

  if len(feeds_eliminar) > 0:
    await eliminar_suscripciones(feeds_eliminar, websocket)

  if len(feeds_agregar) > 0:
    await agregar_suscripciones(feeds_agregar, websocket)


@app.websocket("/tiempoReal")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  print("Websocket accepted")
  feeds_cliente = []
  try:
    # Mantener websocket abierto
    while True:
      # Recibir lista de feeds
      feeds_cliente_nuevos = await websocket.receive_json()
      await actualizar_suscripciones(feeds_cliente, feeds_cliente_nuevos, websocket)
      feeds_cliente = feeds_cliente_nuevos
  except WebSocketDisconnect:
    await eliminar_suscripciones(feeds_cliente, websocket)


asyncio.create_task(repeticion())