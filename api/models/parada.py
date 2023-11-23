import datetime
from pydantic import BaseModel
from bson import ObjectId


class NivelParadaModel(BaseModel):
  idNivel: str
  indice: float
  nombre: str | None = None

class ParadaModel(BaseModel):
  idParada: str
  codigo: str | None = None
  nombre: str | None = None
  nombreTts: str | None = None
  descripcion: str | None = None
  posicionLatitud: float | None = None
  posicionLongitud: float | None = None
  idZona: str | None = None
  url: str | None = None
  tipo: int | None = None
  paradaPadre: str | None = None
  zonaHoraria: str | None = None
  accesibilidad: int | None = None
  idNivel: str | None = None
  codigoPlataforma: str | None = None
  lineas: list[str] | None = None
  viajes: list[str] | None = None
  areas: list[str] | None = None
  nivel: NivelParadaModel | None = None
  agencias: list[str] | None = None

class FrecuenciasViajeModel(BaseModel):
  horaInicio: str
  horaFin: str
  margen: int
  exacto: bool | None = None

class HorarioModel(BaseModel):
  idParada: str
  horaLlegada: str | None = None
  horaSalida: str | None = None
  orden: int
  letrero: str | None = None
  tipoRecogida: int | None = None
  tipoBajada: int | None = None
  recogidaContinua: bool | None = None
  bajadaContinua: bool | None = None
  distanciaRecorrida: float | None = None
  exacto: bool | None = None

class HorarioParadaModel(BaseModel):
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
  horario: HorarioModel
  paradas: list[str] | None = None
  frecuencias: list[FrecuenciasViajeModel] | None = None
  fechas: list[datetime.datetime] | None = None
  zonaHoraria: str