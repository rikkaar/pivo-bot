from os import getenv
from pymongo import ReturnDocument
from utils import logger
from ..models import Address, addresses_collection
from ..models import Config, config_collection
from bson import ObjectId


class AddressesService():
    async def get_address(_id: str) -> Address or None:
        address = await addresses_collection.find_one({"_id": ObjectId(_id)})
        logger.info(address)
        return Address(**address) if address else None

    async def get_addresses() -> list[Address]:
        addresses = addresses_collection.find()
        # return addresses
        return [Address(**a) async for a in addresses]

    async def create_address(address: str, lon: float, lat: float) -> Address:
        address_data = {'address': address,
                        'lon': lon, 'lat': lat}
        inserter_address = await addresses_collection.insert_one(address_data)
        await AddressesService.generateMapConfig()
        return inserter_address

    async def update_address(_id: str, **kwargs) -> Address:
        updated_address = await addresses_collection.find_one_and_update(
            {'_id': ObjectId(_id)},
            {'$set': kwargs},
            return_document=ReturnDocument.AFTER
        )
        return Address(**updated_address) if updated_address else None

    async def delete_address(_id: str):
        await addresses_collection.delete_one({'_id': ObjectId(_id)})
        await AddressesService.generateMapConfig()
    

    # Какая идея? телегу утраивает и ссылка к API и Id фотографии с серверов Телеги.
    # В конфиге у нас хранится актуальная версия карты и может она быть либо тем, либо другим
    # Когда происходит взаимодействие с адресами, мы меняем Id на Url
    # А при вызове команды получить карту мы всегда будем потом отправленное фото обратно загружать в переменную
    # То есть у нас будет +1 запрос, но зато актуальная инфа
    # В функции получения карты не будет ветвления

    async def getMapConfig() -> Config or None:
        # Потом достать отсюда config.map
        config = await config_collection.find_one()
        return Config(**config)
        return [Config(**a) async for a in config]

    async def updateMapConfig(file_id: str) -> None:
        await config_collection.update_one({}, {"$set": {'map': file_id}})

    async def generateMapConfig() -> Config:
        addresses = await AddressesService.get_addresses()
        pt_param = []
        for i, address in enumerate(addresses, start=1):
            # API яндекс карт почему-то использует обратные координаты, сначала Долгота, потом Широта...
            pt_param.append(f'{address.lon},{address.lat},pm2blm{i}')
        url = getenv("MAP_LINK") + "&pt=" + '~'.join(pt_param)

        config = await config_collection.find_one_and_update({}, {"$set": {'map': url}}, return_document=ReturnDocument.AFTER)
        return Config(**config)
    
    async def generateConfig():
        await config_collection.insert_one({}) 
