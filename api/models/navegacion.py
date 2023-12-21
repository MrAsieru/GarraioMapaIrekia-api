from pydantic import BaseModel


class CoordenadasModel(BaseModel):
  # WGS84
  lat: float
  lon: float

class NavegacionRequestModel(BaseModel):
  fecha: str | None = None # YYYY-MM-DD
  hora: str | None = None # HH:MM:SS
  origen: CoordenadasModel
  destino: CoordenadasModel
  accesibleSillaDeRuedas: bool | None = None
  respuestaMaxItinerarios: int | None = None
  cursorPagina: str | None = None
  llegada: bool | None = None
  locale: str | None = None

class AutocompletadoModel(BaseModel):
  lat: float
  lng: float
  description: str
  id: str