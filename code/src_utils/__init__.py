import sqlite3
import random
import functools
import requests
from .constants import *
from flask import request
from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3.middleware import geth_poa_middleware
from requests.exceptions import ConnectionError


##################
# Web3 functions #
##################
def getNode():
    _w3 = Web3(Web3.HTTPProvider(NODE_RPC))
    _w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    connected = False
    while not connected:
        try:
            _w3.eth.get_block('latest')
            connected = True
        except ConnectionError:
            pass
    return Web3(Web3.HTTPProvider(NODE_RPC))


def getContract(w3, address, abi):
    return w3.eth.contract(w3.toChecksumAddress(address), abi=abi)


def updateContract():
    with open(os.path.join(os.path.dirname(__file__), ONE_THOUSAND_CARDS_CONTRACT_PATH), 'r') as contract:
        ONE_THOUSAND_CARDS_INSTANCE = json.loads(contract.read())
        contract.close()


###############################
# JSON information validators #
###############################
def jsonValidator(data):
    result = True
    # First level
    result = result and False if "title" not in data.keys() else True
    result = result and False if type(data["title"]) != str else True
    result = result and False if "type" not in data.keys() else True
    result = result and False if type(data["type"]) != str else True
    result = result and False if "properties" not in data.keys() else True
    result = result and False if type(data["properties"]) != dict else True
    # Second level
    auxData = data["properties"]
    result = result and False if "name" not in auxData.keys() else True
    result = result and False if type(auxData["name"]) != str else True
    result = result and False if "decimals" not in auxData.keys() else True
    result = result and False if type(auxData["decimals"]) != int else True
    result = result and False if "description" not in auxData.keys() else True
    result = result and False if type(auxData["description"]) != str else True
    result = result and False if "image" not in auxData.keys() else True
    result = result and False if type(auxData["image"]) != str else True
    result = result and False if "properties" not in auxData.keys() else True
    result = result and False if type(auxData["properties"]) != dict else True
    # Third level
    auxData = data["properties"]["properties"]
    result = result and False if "up" not in auxData.keys() else True
    result = result and False if type(auxData["up"]) != int else True
    result = result and False if "down" not in auxData.keys() else True
    result = result and False if type(auxData["down"]) != int else True
    result = result and False if "left" not in auxData.keys() else True
    result = result and False if type(auxData["left"]) != int else True
    result = result and False if "right" not in auxData.keys() else True
    result = result and False if type(auxData["right"]) != int else True
    result = result and False if "hash" not in auxData.keys() else True
    result = result and False if type(auxData["hash"]) != float else True
    return result


def jsonValidatorAirdrop(data):
    result = True
    # First level
    result = result and False if "title" not in data.keys() else True
    result = result and False if type(data["title"]) != str else True
    result = result and False if "type" not in data.keys() else True
    result = result and False if type(data["type"]) != str else True
    result = result and False if "properties" not in data.keys() else True
    result = result and False if type(data["properties"]) != dict else True
    # Second level
    auxData = data["properties"]
    result = result and False if "name" not in auxData.keys() else True
    result = result and False if type(auxData["name"]) != str else True
    result = result and False if "decimals" not in auxData.keys() else True
    result = result and False if type(auxData["decimals"]) != int else True
    result = result and False if "description" not in auxData.keys() else True
    result = result and False if type(auxData["description"]) != str else True
    result = result and False if "image" not in auxData.keys() else True
    result = result and False if type(auxData["image"]) != str else True
    result = result and False if "properties" not in auxData.keys() else True
    result = result and False if type(auxData["properties"]) != dict else True
    # Third level
    auxData = data["properties"]["properties"]
    result = result and False if "up" not in auxData.keys() else True
    result = result and False if type(auxData["up"]) != int else True
    result = result and False if "down" not in auxData.keys() else True
    result = result and False if type(auxData["down"]) != int else True
    result = result and False if "left" not in auxData.keys() else True
    result = result and False if type(auxData["left"]) != int else True
    result = result and False if "right" not in auxData.keys() else True
    result = result and False if type(auxData["right"]) != int else True
    result = result and False if "hash" not in auxData.keys() else True
    result = result and False if type(auxData["hash"]) != float else True
    return result


################
# DB utilities #
################
def create_DB(fromEndpoint=False):
    try:
        connection, cursor = openConnection()
        cursor.execute('''
                    create table airdrop (id integer primary key,
                    airdropId string,
                    hash text default "");
                    ''')
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute('''
            create table nft (id integer primary key,
            generation string, cardId string,
            hash text default "", isEgg boolean, 
            airdropId integer default 0,
            FOREIGN KEY (airdropId) REFERENCES airdrop (id));
            ''')
        closeConnection(connection)
        json.loads(requests.post(URL + JSON_TO_IPFS, headers=HEADERS, json=FIRST_GEN_EGG_DATA).text)
        json.loads(requests.post(URL + JSON_TO_IPFS, headers=HEADERS, json=SECOND_GEN_EGG_DATA).text)
        json.loads(requests.post(URL + JSON_TO_IPFS, headers=HEADERS, json=THIRD_GEN_EGG_DATA).text)
        json.loads(requests.post(URL + JSON_TO_IPFS, headers=HEADERS, json=FOURTH_GEN_EGG_DATA).text)
    except sqlite3.OperationalError:
        connection, cursor = openConnection()
        cursor.execute('''
            select * from nft;
            ''')
        result = cursor.fetchall()
        result = [res[2] for res in result]
        closeConnection(connection)
        if fromEndpoint:
            return {"result": len(result)}, 200, RESPONSE_HEADERS
        else:
            return {"result": len(result)}
    if fromEndpoint:
        return {"result": 0}, 200, RESPONSE_HEADERS
    else:
        return {"result": 0}


def openConnection():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    return connection, cursor


def closeConnection(connection):
    connection.commit()
    connection.close()


##########################
# Event Listener helpers #
##########################
def fetchEvents(event, argument_filters=None, from_block=None, to_block="latest", address=None, topics=None):

    abi = event._get_event_abi()
    abi_codec = event.web3.codec

    # Set up any indexed event filters if needed
    argument_filters = dict()
    _filters = dict(**argument_filters)

    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=event.address,
        argument_filters=_filters,
        fromBlock=from_block,
        toBlock=to_block,
        address=address,
        topics=topics,
    )

    # Call node over JSON-RPC API
    logs = event.web3.eth.getLogs(event_filter_params)

    # Convert raw binary event data to easily manipulable Python objects
    for entry in logs:
        data = get_event_data(abi_codec, abi, entry)
        yield data


####################
# Crates and cards #
####################
def getStatsTable():
    table = {}
    for gen in range(1, 5):
        stats = {}
        for st in range(1, 10):
            stat = {"1": (100 - gen) / 9}
            for day in range(2, 10):
                if day > st:
                    stat[str(day)] = stat[str(day - 1)] * 0.9
                else:
                    stat[str(day)] = (100.0 - gen - sum([stats[str(l)][str(day)] for l in range(1, day)])) / (10 - day)
            stats[str(st)] = stat
        table[str(gen)] = stats
    return table


def getFinalStats(event):
    hatchTime = event['args']['hatchTime'] // DAY_TIMESTAMP
    table = getStatsTable()
    daysStat = [1, 1, 1, 1]
    for i in range(hatchTime):
        ok = False
        infiniteBreaker = 0
        while not ok and infiniteBreaker < 100:
            infiniteBreaker += 1
            day = random.randint(0, 3)
            if daysStat[day] < 9:
                daysStat[day] += 1
                ok = True
    stats = []
    for i, day in enumerate(daysStat):
        prob = []
        for stat in table[str(event['args']['gen'])].keys():
            prob.append(table[str(event['args']['gen'])][stat][str(day)])
        prob.append(event['args']['gen'])
        stats.append(random.choices(range(1, 11), prob)[0])
    stats.append((1000 * (2**(event['args']['gen']-1))) + (hatchTime * (1000 * (2**(event['args']['gen']-1))) / 32))
    return stats


def handleNewEgg(event):
    lay_Egg(GEN_NUMBER_MAPPING[event['args']['gen']], str(event['args']['id']))


def handleNewCard(event):
    stats = getFinalStats(event)
    metaData = {
        "title": GEN_NAME_MAPPING[event['args']['gen']],
        "type": "card",
        "properties": {
            "name": GEN_NAME_MAPPING[event['args']['gen']],
            "id": event['args']['id'],
            "decimals": 0,
            "description": GEN_DESCRIPTION_MAPPING[event['args']['gen']],
            "image": "",
            "properties": {
                "up": stats[0],
                "down": stats[1],
                "left": stats[2],
                "right": stats[3],
                "hash": stats[4]
            }
        }
    }
    hatch_Egg(GEN_NUMBER_MAPPING[event['args']['gen']], str(event['args']['id']), metaData)


def lay_Egg(gen, cardId, fromEndpoint=False):
    print("laid egg " + cardId)
    connection, cursor = openConnection()
    cursor.execute('select hash from nft where cardId == ?', (cardId,))
    if cursor.fetchone():
        closeConnection(connection)
        if fromEndpoint:
            return "La carta con id {} ya existe".format(cardId), 400, RESPONSE_HEADERS
        else:
            return "La carta con id {} ya existe".format(cardId)
    if gen in GEN_EGG_HASH_MAPPING.keys():
        eggHash = GEN_EGG_HASH_MAPPING[gen]
    else:
        if fromEndpoint:
            return "Generaci�n incorrecta", 400, RESPONSE_HEADERS
        else:
            return "Generaci�n incorrecta"
    cursor.execute('insert into nft (generation, cardId, hash, isEgg) values (?, ?, ?, ?);', (gen, cardId.rjust(64, '0'), eggHash, True))
    closeConnection(connection)
    if fromEndpoint:
        return "A�adida carta con Id " + cardId, 200, RESPONSE_HEADERS
    else:
        return "A�adida carta con Id " + cardId


def hatch_Egg(gen, cardId, data, fromEndpoint=False):
    print("hatch egg " + str(cardId))
    if not jsonValidator(data):
        if fromEndpoint:
            return {"result": "incorrect data"}, 400, RESPONSE_HEADERS
        else:
            return {"result": "incorrect data"}
    connection, cursor = openConnection()
    cursor.execute('select isEgg from nft where cardId == {}'.format(cardId))
    if cursor.fetchone()[0] == 0:
        closeConnection(connection)
        if fromEndpoint:
            return {"result": "incorrect NFT id"}, 400, RESPONSE_HEADERS
        else:
            return {"result": "incorrect NFT id"}
    if gen in GEN_META_TEMPLATE_MAPPING.keys():
        metaData = GEN_META_TEMPLATE_MAPPING[gen]
    else:
        if fromEndpoint:
            return {"result": "incorrect generation"}, 400, RESPONSE_HEADERS
        else:
            return {"result": "incorrect generation"}
    metaData["pinataContent"] = data
    eggPin = json.loads(requests.post(URL + JSON_TO_IPFS, headers=HEADERS, json=metaData).text)
    cursor.execute('update nft set hash = ?, isEgg = ? where cardId == ? and generation == ?;', (eggPin["IpfsHash"], False, cardId, gen))
    closeConnection(connection)
    if fromEndpoint:
        return {"result": "crate opened! Your new card is available at id: {}".format(cardId)}, 200, RESPONSE_HEADERS
    else:
        return {"result": "crate opened! Your new card is available at id: {}".format(cardId)}


############
# Airdrops #
############
def checkAirdrop(airdropId):
    connection, cursor = openConnection()
    cursor.execute('select hash from airdrop where airdropId == {}'.format(airdropId))
    if cursor.fetchone()[0] == 0:
        closeConnection(connection)
        return False
    return True


def set_Airdrop(data, airdropId, fromEndpoint=False):
    # 1: get card values from request (it will be the same structure than the card)
    if not jsonValidatorAirdrop(data):
        if fromEndpoint:
            return {"result": "incorrect data"}, 400, RESPONSE_HEADERS
        else:
            return {"result": "incorrect data"}

    # 2: get card ids from airdrop (in contract)
    # 3: load data into Pinata
    # 4: save data on the DB


################
# Auth Wrapper #
################
def isItMe(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        data = dict(request.args)
        if data and "key" in data.keys():
            if data["key"] != META_BACK_SECRET:
                return {"result": "Not authorised"}, 401, RESPONSE_HEADERS
            else:
                return func(*args, **kwargs)
        else:
            return {"result": "Bad request"}, 400, RESPONSE_HEADERS
    return secure_function
