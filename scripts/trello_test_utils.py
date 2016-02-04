# this is just to test some utils i made....
#sdaflkasdfklj

from trello_utils import boardid_to_cardmodels, json_cards_from_board, card_json_to_model
from trello import TrelloClient
import logging

logging.basicConfig(filename='trello_test_utils.log', level=logging.INFO)

class trello_test_utils(NebriOS):
    listens_to = ['trello_test_utils']

    def check(self):
        return self.trello_test_utils == True

    def action(self):
        logging.info('Starting action')
        self.trello_test_utils = "Ran"
        
        client = TrelloClient(
            api_key='59cab9be3e086800c9b14fd8ce0ef0a3',
            api_secret='9e504bd0328a7fb1e36d326699f797c4ccf660ea3a990eb5ac13d14a30d2257f',
            token='9b100f103c1955301e56c0a3767dc9644aa006db2b93e2ee23c03cb8ffaf8bc3',
            token_secret='67f8b1a25d40c4c07db9b9da8c60ca4c'
            )
            
        boards = client.list_boards()
        boardid_to_cardmodels(boards[-1].id, client)
        # cards = json_cards_from_board(boards[-1].id, client)
        # for idx, card in enumerate(cards):
        #     if idx > 10:
        #         break
        #
        #     cardout, _ = card_json_to_model(card)
        #     logging.info('here is this cards info')
        #     logging.info(str(cardout.duedate))
        #     logging.info(str(cardout.checklist_finished))
            
#        for b in boards[-1]:
#            boardid_to_cardmodels(b.id, client)
            
        
