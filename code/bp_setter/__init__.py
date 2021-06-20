from flask import Blueprint, request
from json.decoder import JSONDecodeError
from requests import post
from src_utils import *
from .endpoints import *

setterBlueprint = Blueprint('setterBlueprint', __name__)


@setterBlueprint.route(GET_CRATE, methods=['POST'])
def layEgg(gen, cardId):
    return lay_Egg(gen, cardId, fromEndpoint=True)


@setterBlueprint.route(OPEN_CRATE, methods=['POST'])
def hatchEgg(gen, cardId):
    try:
        data = json.loads(request.data.decode("UTF-8"))
    except JSONDecodeError:
        return {"result": "not a valid JSON object"}, 200, RESPONSE_HEADERS
    return hatch_Egg(gen, cardId, data, fromEndpoint=True)
