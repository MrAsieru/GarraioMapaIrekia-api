from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import db
from api.routers import agencias, feeds, lineas, paradas, posiciones, tiemporeal, viajes


app = FastAPI()

# Routers HTTP
app.include_router(feeds.router)
app.include_router(agencias.router)
app.include_router(lineas.router)
app.include_router(paradas.router)
app.include_router(viajes.router)
app.include_router(posiciones.router)

# Routers WebSocket
app.include_router(tiemporeal.router)


@app.on_event("startup")
async def startup_event():
  await db.connect_to_database()

@app.on_event("shutdown")
async def shutdown():
  await db.close_database_connection()

# CORS
#TODO: Quitar localhost
app.add_middleware(
  CORSMiddleware,
  allow_origins=['https://www.mrasieru.live', 'http://localhost:8100'],
  allow_credentials=False,
  allow_methods=['GET', 'POST'],
  allow_headers=['*'],
)