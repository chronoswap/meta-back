import asyncio
import requests
from src_utils import *


class Listener:
    def __init__(self):
        self.w3 = getNode()
        self.contract = getContract(self.w3,
                                    ONE_THOUSAND_CARDS_INSTANCE["networks"][self.w3.net.version]["address"],
                                    ONE_THOUSAND_CARDS_INSTANCE["abi"])
        self.eggLaidFilter = self.contract.events.eggLaid.createFilter(fromBlock='latest')
        self.cardCreatedFilter = self.contract.events.cardCreated.createFilter(fromBlock='latest')
        self.loop = asyncio.get_event_loop()
        self.initialised = False
        try:
            self.loop.run_until_complete(asyncio.gather(self.eggLaidLoop(2),
                                                        self.cardCreatedLoop(2),
                                                        self.checkServer(10)))
        finally:
            self.loop.close()

    def startUp(self):
        print("Listener: startup")
        state = create_DB()
        eggEvents = list(fetchEvents(self.contract.events.eggLaid, from_block=0))
        cardEvents = list(fetchEvents(self.contract.events.cardCreated, from_block=0))
        if len(eggEvents) == state["result"]:
            return None
        for i in range(state["result"], len(eggEvents)):
            handleNewEgg(eggEvents[i])
        for cardEvent in cardEvents:
            handleNewEgg(cardEvent)
            handleNewCard(cardEvent)

    async def eggLaidLoop(self, poll_interval):
        while True:
            for event in self.eggLaidFilter.get_new_entries():
                print(event)
                handleNewEgg(event)
            await asyncio.sleep(poll_interval)

    async def cardCreatedLoop(self, poll_interval):
        while True:
            for event in self.cardCreatedFilter.get_new_entries():
                print(event)
                handleNewCard(event)
            await asyncio.sleep(poll_interval)

    async def checkServer(self, poll_interval):
        while True:
            try:
                if not self.initialised:
                    self.startUp()
                    self.initialised = True
            except requests.exceptions.ConnectionError:
                self.initialised = False
            await asyncio.sleep(poll_interval)


Listener()
