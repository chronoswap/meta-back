from flask import Blueprint
from src_utils import *
from .endpoints import *

manageBlueprint = Blueprint('manageBlueprint', __name__)


@manageBlueprint.route(CREATE)
def createDB():
    return create_DB(fromEndpoint=True)
