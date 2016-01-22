import httplib2
import json
import logging
from urllib import urlencode

from trello import TrelloClient


logging.basicConfig(filename='trello.log',level=logging.DEBUG)


# Get key here: https://trello.com/app-key
# Add shared KVP 'TRELLO_KEY' with a value of the key
# Get token here, replacing API_KEY with the key you got above
# https://trello.com/1/authorize?key=ebf87e6bc0dc4ddc45bbd7e05c87f276&name=Nebri+Scriptrunner&expiration=never&response_type=token&scope=read,write
# Add shared KVP 'TRELLO_TOKEN' with a value of the token


class trello_fetch_cards(NebriOS):
    listens_to = ['trello_fetch_cards']
    
    TRELLO_API_SECRET = '9e504bd0328a7fb1e36d326699f797c4ccf660ea3a990eb5ac13d14a30d2257f'
    
    #####TRELLO_API_TOKEN = '6fb67eb6a2afdffd0506348b251541cb04cf1c11b5712632746fe0eb1ed073f3'
    #####TRELLO_API_KEY = 'ebf87e6bc0dc4ddc45bbd7e05c87f276'

    def check(self):
        return self.trello_fetch_cards == True

    def action(self):
        self.trello_fetch_cards = "RAN"
        
        TRELLO_API_KEY = shared.TRELLO_KEY
        TRELLO_API_TOKEN = shared.TRELLO_TOKEN
        
        client = TrelloClient(
            api_key=TRELLO_API_KEY,
            api_secret=self.TRELLO_API_SECRET,
            token=TRELLO_API_TOKEN
        )
        logging.debug('client')
        logging.debug(client)
        me = client.fetch_json('/members/me')
        member_boards_cache_key = 'TRELLO_CARDS_FOR_MEMBER_%s' % me['id']
        member_boards_cache = getattr(shared, member_boards_cache_key, {}) or {}
        
        fetch_cards_in_progress_cache_key = 'TRELLO_FETCH_CARDS_IN_PROGRESS_FOR_MEMBER_%s' % me['id']
        fetch_cards_in_progress_cache = getattr(shared, fetch_cards_in_progress_cache_key, False)
        
        if not fetch_cards_in_progress_cache:
            # Tell the world that we are fetching cards for this member
            setattr(shared, fetch_cards_in_progress_cache_key, True)

            boards = client.list_boards()
            for board in boards:
                cards = board.all_cards()
                cards_for_board_cache = member_boards_cache.get(board.id, {})
                cards_for_board_cache_ids = cards_for_board_cache.keys()
                
                for i, card in enumerate(cards):
                    logging.debug(card)
                    cards_for_board_cache.update({
                        card.id: client.fetch_json('/cards/' + card.id, query_params={
                            'actions': 'all',
                            'checklists': 'all',
                            'attachments': 'true'
                        })
                    })
    
                member_boards_cache[board.id] = cards_for_board_cache

            setattr(shared, member_boards_cache_key, member_boards_cache)
    
            # Done fetching
            setattr(shared, fetch_cards_in_progress_cache_key, False)