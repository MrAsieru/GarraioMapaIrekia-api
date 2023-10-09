from pydantic import BaseModel
from bson import ObjectId


class StopModel(BaseModel):
  stop_id: str
  code: str | None = None
  name: str | None = None
  desc: str | None = None
  coords_lat: float | None = None
  coords_lon: float | None = None
  zone_id: str | None = None
  url: str | None = None
  location_type: int | None = None
  parent_station: str | None = None
  timezone: str | None = None
  wheelchair_boarding: int | None = None
  level_id: str | None = None
  platform_code: str | None = None

  class Config:
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    schema_extra = {
    }