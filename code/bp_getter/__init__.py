from flask import Blueprint
from requests import get
from src_utils import *
from .endpoints import *

getterBlueprint = Blueprint('getterBlueprint', __name__)


@getterBlueprint.route(GET_DATA)
def getData(gen):
    connection, cursor = openConnection()
    cursor.execute('select * from nft where generation = ?;', (gen,))
    result = cursor.fetchall()
    closeConnection(connection)
    result = [res[2] for res in result]
    return {"result": len(result)}, 200, RESPONSE_HEADERS


@getterBlueprint.route(GET_NFT)
def getFirstGenCard(nftId):
    connection, cursor = openConnection()
    cursor.execute('select hash from nft where cardId == {};'.format(nftId))
    result = cursor.fetchone()
    closeConnection(connection)
    if not result:
        return {'status': 'non existing'}, 200, RESPONSE_HEADERS
    getPin = json.loads(get(GET_URL + result[0]).text)
    return getPin, 200, RESPONSE_HEADERS
