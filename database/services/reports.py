from enum import Enum
from typing import List
from pymongo import ReturnDocument
from bson import ObjectId
from utils import logger
from ..models import Report, reports_collection

class FilterState(int, Enum):
    false = 0
    all = 1
    true = 2

class ReportService:
    @staticmethod
    async def get_report(_id: str) -> Report or None:
        report = await reports_collection.find_one({"_id": ObjectId(_id)})
        return Report(**report) if report else None

    @staticmethod
    async def get_reports(address_id: str = None, contact: bool = None, fulfilled: bool = None) -> List[Report]:
        query = {}
        if contact is not None:
            query['contact'] = contact
        if address_id:
            query['address'] = ObjectId(address_id)
        if fulfilled is not None:
            query['fulfilled'] = fulfilled

        reports = reports_collection.find(query).sort({"_id": -1})
        return [Report(**r) async for r in reports]
    
    @staticmethod
    async def get_reports_page(limit: int, skip=int, address_id: str = None, contact: FilterState = FilterState.all, fulfilled: FilterState = FilterState.all) -> List[Report]:
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

        logger.info(query)

        reports = reports_collection.find(query).sort({"_id": -1}).skip(skip).limit(limit)
        return [Report(**r) async for r in reports]

    @staticmethod
    async def create_report(address: str, shortAddress: str, sender: int, senderUsername: str, message: str, contact: bool) -> Report:
        report_data = {
            "address": ObjectId(address),
            "shortAddress": shortAddress,
            "sender": sender,
            "senderUsername": senderUsername,
            'message': message,
            "contact": contact,
            'fulfilled': False
        }
        _id = await reports_collection.insert_one(report_data)
        report = await reports_collection.find_one({"_id": _id.inserted_id})
        return Report(**report)

    @staticmethod
    async def update_report(_id: str, **kwargs) -> Report:
        updated_report = await reports_collection.find_one_and_update(
            {'_id': ObjectId(_id)},
            {'$set': kwargs},
            return_document=ReturnDocument.AFTER
        )
        return Report(**updated_report)

    @staticmethod
    async def delete_report(_id: str) -> None:
        await reports_collection.delete_one({'_id': ObjectId(_id)})

    @staticmethod
    async def toggle_fulfilled(report_id: str) -> Report:
        report = await ReportService.get_report(report_id)
        if not report:
            raise ValueError("Invalid request_id")

        updated_report = await ReportService.update_report(report_id, fulfilled=not report.fulfilled, return_document=ReturnDocument.AFTER)
        return updated_report
