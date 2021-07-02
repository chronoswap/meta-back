from flask import Blueprint
from json.decoder import JSONDecodeError
from src_utils import *
from .endpoints import *

setterBlueprint = Blueprint('setterBlueprint', __name__)


@setterBlueprint.route(LAY_CRATE, methods=['POST'])
def layCrate(gen, cardId):
    return lay_Egg(gen, cardId, fromEndpoint=True)


@setterBlueprint.route(OPEN_CRATE, methods=['POST'])
def openCrate(gen, cardId):
    try:
        data = json.loads(request.data.decode("UTF-8"))
    except JSONDecodeError:
        return {"result": "not a valid JSON object"}, 400, RESPONSE_HEADERS
    return hatch_Egg(gen, cardId, data, fromEndpoint=True)


@setterBlueprint.route(SET_AIRDROP, methods=['POST'])
@isItMe
def setAirdrop(airdropId):
    if not checkAirdrop(airdropId):
        return {"result": "incorrect Airdrop id"}, 400, RESPONSE_HEADERS
    try:
        data = json.loads(request.data.decode("UTF-8"))
    except JSONDecodeError:
        return {"result": "not a valid JSON object"}, 400, RESPONSE_HEADERS
    return set_Airdrop(data, airdropId, fromEndpoint=True)
