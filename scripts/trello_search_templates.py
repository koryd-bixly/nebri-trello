# v0.0.1

import logging

from trello import TrelloClient

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):


logging.basicConfig(filename='trello_search_templates.log', level=logging.DEBUG)


# Get key here: https://trello.com/app-key
# Add shared KVP 'TRELLO_KEY' with a value of the key
# Get token here, replacing API_KEY with the key you got above
# https://trello.com/1/authorize?key=ebf87e6bc0dc4ddc45bbd7e05c87f276&name=Nebri+Scriptrunner&expiration=never&response_type=token&scope=read,write
# Add shared KVP 'TRELLO_TOKEN' with a value of the token


class trello_search_templates(NebriOS):
    # TODO change to schedule
    listens_to = ['trello_search_templates']

    required = [
        'trello_api_key',
        'trello_api_secret',
        'trello_token',
        'token_secret'
    ]

    def check(self):
        return self.trello_search_templates == True

    def action(self):
        self.trello_search_templates = 'RAN'

        client = TrelloClient(
            api_key=self.trello_api_key,
            api_secret=self.trello_api_secret,
            token=self.trello_token,
            token_secret=self.token_secret
        )

        boards = client.list_boards()
        for board in boards:
            cards = board.open_cards()
            for card in cards:
                if card.name.startswith('deliver'):
                    logging.debug('card found: ' + card.name)
                    logging.debug('card id: ' + card.id)
                    # do something to run this card...

                    # This could be much niceer with a model...
                    p = Process.objects.create()
                    p.card_id = card.id
                    p.trello_move_card = True
                    p.trello_api_key = self.trello_api_key
                    p.trello_api_secret = self.trello_api_secret
                    p.trello_token = self.trello_token
                    p.token_secret = self.token_secret
                    p.save()

        logging.debug('finished')


