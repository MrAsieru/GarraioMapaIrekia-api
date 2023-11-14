from pydantic import BaseModel


class AgenciaModel(BaseModel):
  idAgencia: str
  nombre: str
  url: str
  zonaHoraria: str
  idioma: str | None = None
  telefono: str | None = None
  urlTarifa: str | None = None
  email: str | None = None
  lineas: list[str] | None = None

from api.models.linea import LineaModel

class AgenciaLineasModel(AgenciaModel):
  lineas: list[LineaModel]