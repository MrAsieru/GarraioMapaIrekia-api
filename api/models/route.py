from pydantic import BaseModel
from bson import ObjectId

from api.models.agency import AgencyModel


class RouteModel(BaseModel):
  route_id: str
  agency_id: str
  agency: AgencyModel | None = None
  short_name: str | None = None
  long_name: str | None = None
  desc: str | None = None
  type: int | None = None
  url: str | None = None
  color: str | None = None
  text_color: str | None = None
  sort_order: int | None = None
  network_id: str | None = None

  class Config:
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    schema_extra = {
    }