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