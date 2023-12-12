from pydantic import BaseModel
from bson import ObjectId

from api.models.agencia import AgenciaModel


class PatronLineaModel(BaseModel):
  de: str
  a: str
  direccion: str | None = None
  letrero: str | None = None
  numViajes: int
  paradas: list[str]

class LineaModel(BaseModel):
  idLinea: str
  idAgencia: str
  agencia: AgenciaModel | None = None
  nombreCorto: str | None = None
  nombreLargo: str | None = None
  descripcion: str | None = None
  tipo: int | None = None
  url: str | None = None
  color: str | None = None
  colorTexto: str | None = None
  orden: int | None = None
  recogidaContinua: int | None = None
  bajadaContinua: int | None = None
  idRed: str | None = None
  paradas: list[str] | None = None
  viajes: list[str] | None = None
  bbox: list[float]
  patrones: list[PatronLineaModel] | None = None