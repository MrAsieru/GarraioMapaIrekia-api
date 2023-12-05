from pydantic import BaseModel
from datetime import datetime

class PosicionesRequestModel(BaseModel):
  fecha: str
  agencias: list[str]

class PosicionViajeModel(BaseModel):
  idViaje: str
  idLinea: str
  tipo: int | None = None #TODO: Quitar None
  posiciones: str

class PosicionAgenciaModel(BaseModel):
  idAgencia: str
  viajes: list[PosicionViajeModel]

class PosicionesModel(BaseModel):
  fecha: datetime
  agencias: list[PosicionAgenciaModel]
