from pydantic import BaseModel
from bson import ObjectId
from typing import List


class AgencyModel(BaseModel):
  agency_id: str | None = None
  name: str
  url: str
  timezone: str
  lang: str | None = None
  phone: str | None = None
  fare_url: str | None = None
  email: str | None = None

  class Config:
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    schema_extra = {
    }

from api.models.route import RouteModel

class AgencyRoutesModel(AgencyModel):
  routes: List[RouteModel]

  class Config:
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    schema_extra = {
    }