from pydantic import BaseModel
from datetime import datetime


class FeedInfoModel(BaseModel):
  nombreEditor: str
  urlEditor: str
  idioma: str
  idiomaPredeterminado: str | None = None
  fechaInicio: datetime | None = None
  fechaFin: datetime | None = None
  version: str | None = None
  email: str | None = None
  urlContacto: str | None = None


class FeedAtribucionModel(BaseModel):
  idAtribucion: str | None = None
  idAgencia: str | None = None
  idLinea: str | None = None
  idViaje: str | None = None
  nombreOrganizacion: str
  esProductor: bool | None = None
  esOperador: bool | None = None
  esAutoridad: bool | None = None
  url: str | None = None
  email: str | None = None
  telefono: str | None = None


class FeedModel(BaseModel):
  idFeed: str
  info: FeedInfoModel | None = None
  atribuciones: FeedAtribucionModel | None = None
  tiempoReal: list[str] | None = None