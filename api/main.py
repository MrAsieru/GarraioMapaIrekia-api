import os
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from bson import ObjectId
from typing import List
import motor.motor_asyncio


app = FastAPI()
# client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{os.environ['MONGODB_API_USER']}:{os.environ['MONGODB_API_USER_PASSWORD']}@127.0.0.1:27017/{os.environ['MONGODB_INITDB_DATABASE']}")
# db = client[os.environ['MONGODB_INITDB_DATABASE']]
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://apiUser:apiUser@192.168.1.10:27017/it0")
db = client["it0"]


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


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


class NameModel(BaseModel):
    short: str | None = None
    long: str | None = None

    class Config:
        arbitrary_types_allowed = True


class ColorModel(BaseModel):
    color: str | None = None
    text: str | None = None

    class Config:
        arbitrary_types_allowed = True


class RouteModel(BaseModel):
    route_id: str
    agency: AgencyModel | None = None
    name: NameModel
    desc: str | None = None
    type: int | None = None
    url: str | None = None
    color: ColorModel | None = None
    sort_order: int | None = None
    network_id: str | None = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
        }


class CoordsModel(BaseModel):
    lat: float
    lon: float

    class Config:
        arbitrary_types_allowed = True


class StopModel(BaseModel):
    stop_id: str
    code: str | None = None
    name: str | None = None
    desc: str | None = None
    coords: CoordsModel | None = None
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


@app.get("/agencies", response_description="Obtener todas las agencias", response_model=List[AgencyModel])
async def get_agencies():
    agencias = await db["agencies"].find().to_list(1000)
    return agencias
    
@app.get("/agencies/{id}", response_description="Obtener agencia por agency_id", response_model=AgencyModel)
async def get_agency_id(id: str):
    agencia = await db["agencies"].find_one({"agency_id": id})
    return agencia

@app.get("/routes", response_description="Obtener todas las rutas", response_model=List[RouteModel])
async def get_routes():
    rutas = await db["routes"].aggregate([
        {
            "$lookup": {
                "from": "agencies",
                "localField": "agency",
                "foreignField": "_id",
                "as": "agency"
            }
        },
        {
            "$unwind": "$agency"
        }]).to_list(1000)
    return rutas

@app.get("/routes/{id}", response_description="Obtener ruta por route_id", response_model=RouteModel)
async def get_route_id(id: str):
    ruta = await db["routes"].aggregate([
        {
            "$match": {
                "route_id": id
            }
        },
        {
            "$lookup": {
                "from": "agencies",
                "localField": "agency",
                "foreignField": "_id",
                "as": "agency"
            }
        },
        {
            "$unwind": "$agency"
        }]).to_list(1)
    return ruta[0]

@app.get("/stops", response_description="Obtener todas las paradas", response_model=List[StopModel])
async def get_stops():
    paradas = await db["stops"].find().to_list(1000)
    return paradas

@app.get("/stops/{id}", response_description="Obtener parada por stop_id", response_model=StopModel)
async def get_stop_id(id: str):
    parada = await db["stops"].find_one({"stop_id": id})
    return parada