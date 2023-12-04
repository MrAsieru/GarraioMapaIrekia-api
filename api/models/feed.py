from pydantic import BaseModel
from datetime import datetime

from api.models.agencia import AgenciaModel


class FeedFuenteModel(BaseModel):
  tipo: str
  atribucion: str
  urlAtribucion: str
  url: str | None = None
  conjuntoDatoId: int | None = None

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


class FeedAtribucionNombreModel(BaseModel):
  id: str
  nombre: str | None = None
  nombreCorto: str | None = None
  nombreLargo: str | None = None


class FeedModel(BaseModel):
  idFeed: str
  nombre: str
  fuentes: list[FeedFuenteModel] | None = None
  info: FeedInfoModel | None = None
  atribuciones: list[FeedAtribucionModel] | None = None
  tiempoReal: list[str] | None = None
  agencias: list[FeedAtribucionNombreModel] | None = None
  lineas: list[FeedAtribucionNombreModel] | None = None
  viajes: list[FeedAtribucionNombreModel] | None = None