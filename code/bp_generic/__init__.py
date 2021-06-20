from flask import Blueprint
from src_utils import *
from .endpoints import *

genericBlueprint = Blueprint('genericBlueprint', __name__)


@genericBlueprint.route(PING)
def testServer():
    updateContract()
    return {'status': True}, 200, RESPONSE_HEADERS
