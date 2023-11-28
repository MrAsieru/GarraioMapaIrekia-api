import datetime
from pydantic import BaseModel

from api.models.parada import ParadaModel


class HorarioViajeModel(BaseModel):
  idParada: str
  horaLlegada: str | None = None
  horaSalida: str | None = None
  orden: int
  letrero: str | None = None
  tipoRecogida: int | None = None
  tipoBajada: int | None = None
  recogidaContinua: int | None = None
  bajadaContinua: int | None = None
  distanciaRecorrida: float | None = None
  exacto: bool | None = None

class FrecuenciasViajeModel(BaseModel):
  horaInicio: str
  horaFin: str
  margen: int
  exacto: bool | None = None

class ViajeModel(BaseModel):
  idAgencia: str
  idViaje: str
  idLinea: str
  idServicio: str
  letrero: str | None = None
  nombre: str | None = None
  direccion: int | None = None
  idBloque: str | None = None
  idRecorrido: str | None = None
  accesibilidad: int | None = None
  bicicletas: int | None = None
  horarios: list[HorarioViajeModel] | None = None
  paradas: list[str] | None = None
  frecuencias: list[FrecuenciasViajeModel] | None = None
  fechas: list[datetime.datetime] | None = None
  bbox: list[float]