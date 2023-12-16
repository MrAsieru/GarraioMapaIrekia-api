from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os


class MongoManager:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{os.environ['MONGODB_API_USER']}:{os.environ['MONGODB_API_USER_PASSWORD']}@mongodb:27017/gtfs", tz_aware=True)
        self.db = self.client["gtfs"]

    async def close_database_connection(self):
        self.client.close()
    
    async def find(self, collection: str, *args, **kwargs) -> list:
        return await self.db[collection].find(*args, **kwargs).to_list(None)
    
    async def aggregate(self, collection, pipeline, *args, **kwargs) -> list:
        return await self.db[collection].aggregate(pipeline, *args, **kwargs).to_list(None)
    
    async def find_one(self, collection, filter: Optional[any] = None, *args, **kwargs) -> dict:
        return await self.db[collection].find_one(filter, *args, **kwargs)