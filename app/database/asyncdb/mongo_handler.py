from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Dict, Optional
from pymongo import ASCENDING, DESCENDING


class MongoDbHandler:
    def __init__(self, collection: AsyncIOMotorCollection):
        if not isinstance(collection, AsyncIOMotorCollection):
            raise TypeError("collection must be an instance of AsyncIOMotorCollection")
        self.collection = collection

    def _check_dict(self, param, is_filter=False):
        if not isinstance(param, dict):
            msg = "Filter must be a dict" if is_filter else "Input must be a dict"
            raise TypeError(msg)

    def dict_instance_checker(self, parameter: dict, _is_filter: bool = False):
        if not isinstance(parameter, dict):
            message = "input should be instance of dict"
            if _is_filter:
                message = "where condition should of dict"
            raise TypeError(message)

    def _check_list(self, param):
        if not isinstance(param, list):
            raise TypeError("Input must be a list")

    async def find(self, query: dict, projection: dict = {"_id": 0}, sort: Optional[dict] = None) -> List[dict]:
        self._check_dict(query)
        cursor = self.collection.find(query, projection)
        if sort:
            cursor = cursor.sort(sort.get("sort_key"), sort.get("sort_value", ASCENDING))
        return await cursor.to_list(length=None)

    async def find_one(self, query: dict, projection: dict = {"_id": 0}) -> Optional[dict]:
        self._check_dict(query)
        return await self.collection.find_one(query, projection)

    async def insert_one(self, data: dict):
        self._check_dict(data)
        return await self.collection.insert_one(data)

    async def update_one(self, filter: dict, data: dict, upsert: bool = False, array_filters: list = None):
        if not filter:
            raise AttributeError

        self._check_dict(data)
        self._check_dict(filter, is_filter=True)
        if array_filters:
            update_params = {"upsert": upsert}
            update_params["array_filters"] = array_filters
            return await self.collection.update_one(filter, data, **update_params)

        return await self.collection.update_one(filter, data, upsert=upsert)

    async def delete_one(self, filter: dict):
        self._check_dict(filter)
        return await self.collection.delete_one(filter)

    async def find_one_and_delete(self, filter: dict):
        self._check_dict(filter)
        return await self.collection.find_one_and_delete(filter)
    
    async def find_one_and_update(self, filter: dict, update: dict,projection: dict = {"_id": 0}):
        self._check_dict(filter, is_filter=True)
        self._check_dict(update)
        return await self.collection.find_one_and_update(filter, update,projection)
