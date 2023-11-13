from enum import Enum
from typing import List
from pymongo import ReturnDocument
from bson import ObjectId
from utils import logger
from ..models import Request, requests_collection

class FilterState(int, Enum):
    false = 0
    all = 1
    true = 2

class RequestService:
    @staticmethod
    async def get_request(request_id: str) -> Request or None:
        request = await requests_collection.find_one({"_id": ObjectId(request_id)})
        return Request(**request) if request else None

    @staticmethod
    async def get_requests() -> List[Request]:
        requests_data = requests_collection.find()
        return [Request(**r) async for r in requests_data]

    @staticmethod
    async def get_requests(address_id: str = None, contact: bool = None, fulfilled: bool = None) -> List[Request]:
        query = {}
        if contact is not None:
            query['contact'] = contact
        if address_id:
            query['address'] = ObjectId(address_id)
        if fulfilled is not None:
            query['fulfilled'] = fulfilled

        requests_data = requests_collection.find(query)
        return [Request(**r) async for r in requests_data]
    
    @staticmethod
    async def get_requests_page(limit: int, skip=int, address_id: str = None, contact: FilterState = FilterState.all, fulfilled: FilterState = FilterState.all) -> List[Request]:
        query = {}
        if contact == FilterState.true:
            query['contact'] = True
        elif contact == FilterState.false:
            query['contact'] = False

        if fulfilled == FilterState.true:
            query['fulfilled'] = True
        elif fulfilled == FilterState.false:
            query['fulfilled'] = False

        if address_id:
            query['address'] = ObjectId(address_id)

        requests = requests_collection.find(query).sort({"_id": -1}).skip(skip).limit(limit)
        return [Request(**r) async for r in requests]

    @staticmethod
    async def create_request(address_id: str, shortAddress: str, sender: int, senderUsername: str, name: str, link: str, contact: bool) -> Request:
        request_data = {
            "address": ObjectId(address_id),
            "shortAddress": shortAddress,
            "sender": sender,
            "senderUsername": senderUsername,
            "name": name,
            "link": link,
            "contact": contact,
            'fulfilled': False
        }
        _id = await requests_collection.insert_one(request_data)
        request = await requests_collection.find_one({"_id": _id.inserted_id})
        return Request(**request)

    @staticmethod
    async def update_request(request_id: str, **kwargs) -> Request:
        updated_request = await requests_collection.find_one_and_update(
            {"_id": ObjectId(request_id)},
            {"$set": kwargs},
            return_document=ReturnDocument.AFTER
        )
        return Request(**updated_request)

    @staticmethod
    async def delete_request(request_id: str) -> None:
        await requests_collection.delete_one({"_id": ObjectId(request_id)})

    @staticmethod
    async def toggle_fulfilled(request_id: str) -> Request:
        request = await RequestService.get_request(request_id)
        if not request:
            raise ValueError("Invalid request_id")

        updated_request = await RequestService.update_request(request_id, fulfilled=not request.fulfilled, return_document=ReturnDocument.AFTER)
        return updated_request
