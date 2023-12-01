from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from api.db import db

from typing import List
import asyncio
import aiohttp
from datetime import datetime

from api.models.feed import FeedModel


router = APIRouter(prefix="/tiempoReal")


websocket_clients = []
lista_feeds = {} # {idFeed: {suscripciones: [websocket], tiempoReal: [{url: str, data: bytes|None, modificado: str|None, etag: str|None}]}}



async def descargar_tiempo_real(fuente_tr: dict) -> (dict, str):
  try:
    # Establecer cabeceras para evitar descargar datos si no han sido modificados
    headers = {}
    if fuente_tr["modificado"] is not None:
      headers["If-Modified-Since"] = fuente_tr["modificado"]
    if fuente_tr["etag"] is not None:
      headers["If-None-Match"] = fuente_tr["etag"]
    
    # Descargar datos
    async with aiohttp.ClientSession() as session:
      async with session.get(fuente_tr["url"], headers=headers) as response:
        if response.status == 304:
          # Si los datos no han sido modificados, devolver None
          return None, None, None
        else:
          ultima_modificacion = response.headers.get("Last-Modified", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
          etag = response.headers.get("ETag", None)
          content = await response.read()
          return content, ultima_modificacion, etag
  except aiohttp.ClientError as e:
    print(f"Error obteniendo datos: {e}")
    return None, None, None


async def actualizar_tiempo_real(idFeed: str):
  # Actualizar solamente feeds con suscriptores
  if len(lista_feeds[idFeed]["suscripciones"]) > 0:
    actualizar = False
    # Recorrer todas las fuentes de tiempo real del feed
    for fuente_tr in lista_feeds[idFeed]["tiempoReal"]:
      new_data, modificado, etag = await descargar_tiempo_real(fuente_tr)

      # Si se obtuvieron datos nuevos, actualizarlos
      if new_data is not None:
        fuente_tr["data"] = new_data
        fuente_tr["modificado"] = modificado
        fuente_tr["etag"] = etag
        actualizar = True

    if actualizar:
      for client in list(lista_feeds[idFeed]["suscripciones"]):
        await enviar_datos(client, idFeed)


async def repeticion():
  while True:
    print("Comprobando cambios de tiempo real")
    for idFeed in list(lista_feeds.keys()):
      await actualizar_tiempo_real(idFeed)
    await asyncio.sleep(15)


async def enviar_datos(websocket: WebSocket, idFeed: str):
  global lista_feeds
  print(f"Enviando datos de {idFeed} al cliente {websocket}")
  # Formato de mensaje binario: [Longitud idFeed (2 Bytes)][idFeed (x Bytes)][Protobuf (y Bytes)]
  # Calcular y codificar longitud del idFeed
  idFeedLen = len(idFeed).to_bytes(2, byteorder="big")

  # Agrupar datos existentes
  datos = b""
  for fuente_tr in list(lista_feeds[idFeed]["tiempoReal"]):
    if fuente_tr["data"] is not None:
      datos += fuente_tr["data"]

  # Crear mensaje y enviarlo
  if websocket.client_state == WebSocketState.CONNECTED:
    await websocket.send_bytes(idFeedLen + idFeed.encode(encoding="utf-8") + datos)


async def agregar_suscripciones(feeds_cliente: list[str], websocket: WebSocket):
  global lista_feeds
  # Recibir ids de feeds que contengan datos en tiempoReal, donde tiempoReal si existe es una url
  feeds_nuevos = list(set(feeds_cliente) - set(lista_feeds.keys()))

  if len(feeds_nuevos) > 0:
    feeds_validos = await db.find("feeds", {"_id": {"$in": feeds_nuevos}, "tiempoReal": {"$exists": True}}, projection={"_id": 1, "tiempoReal": 1})
    
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
        lista_feeds[feed]["tiempoReal"].append({"url": url, "data": None, "modificado": None, "etag": None})
    
    # Añadir websocket a la lista de suscripciones del feed
    lista_feeds[feed]["suscripciones"].append(websocket)

    # Si el feed es nuevo, descargar datos
    if creado:
      await actualizar_tiempo_real(feed)
    else:
      await enviar_datos(websocket, feed)
  print([f"{f} - {len(lista_feeds[f]['suscripciones'])} suscriptores\n" for f in list(lista_feeds.keys())])


async def eliminar_suscripciones(feeds_cliente: list[str], websocket: WebSocket):
  for feed in feeds_cliente:
    if feed in lista_feeds.keys():
      l = len(lista_feeds[feed]["suscripciones"])
      try:
        lista_feeds[feed]["suscripciones"].remove(websocket)
      except ValueError:
        pass
  print([f"{f} - {len(lista_feeds[f]['suscripciones'])} suscriptores\n" for f in lista_feeds.keys()])


async def actualizar_suscripciones(feeds_actuales: list[str], feeds_nuevos: list[str], websocket: WebSocket):
  # Obtener feeds a eliminar y feeds a agregar, no hacer nada con los que ya estan
  feeds_eliminar = list(set(feeds_actuales) - set(feeds_nuevos))
  feeds_agregar = list(set(feeds_nuevos) - set(feeds_actuales))

  if len(feeds_eliminar) > 0:
    await eliminar_suscripciones(feeds_eliminar, websocket)

  if len(feeds_agregar) > 0:
    await agregar_suscripciones(feeds_agregar, websocket)


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  print("Conexión websocket aceptada")
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