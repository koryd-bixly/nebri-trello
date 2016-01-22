# v0.0.2

import logging

from trello import TrelloClient

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):


logging.basicConfig(filename='trello_move_card.log', level=logging.DEBUG)


# Get key here: https://trello.com/app-key
# Add shared KVP 'TRELLO_KEY' with a value of the key
# Get token here, replacing API_KEY with the key you got above
# https://trello.com/1/authorize?key=ebf87e6bc0dc4ddc45bbd7e05c87f276&name=Nebri+Scriptrunner&expiration=never&response_type=token&scope=read,write
# Add shared KVP 'TRELLO_TOKEN' with a value of the token


class trello_move_card(NebriOS):
    listens_to = ['trello_move_card']

    required = [
        'card_id',
        'trello_api_key',
        'trello_api_secret',
        'trello_token',
        'token_secret'
    ]

    def check(self):
        logging.debug('starting check')
        return self.trello_move_card == True

    def action(self):
        logging.debug('start action')
        try:
            logging.debug(parent.trello_api_key)
        except:
            pass

        client = TrelloClient(
            api_key=self.trello_api_key,
            api_secret=self.trello_api_secret,
            token=self.trello_token,
            token_secret=self.token_secret
        )

        card = client.get_card(self.card_id)
        cardinfo = card.name.split('_')
        if cardinfo.pop(0).lower() == 'deliver':
            list_name = '_'.join(cardinfo)
            logging.debug(list_name)
            board = card.board
            for list in board.open_lists():
                if list.name == list_name:
                    # card found. Now buid it...
                    duedate = datetime.now() + timedelta(days=1)
                    name = 'To Finish by: {}'.format(
                        duedate.strftime('%m-%d-%y, %H:%M')
                    )
                    list.add_card(name, due=str(duedate), source=card.id)


        logging.debug(card.id)
        logging.debug(card.name)
        logging.debug(card.description)

        logging.debug('finished')