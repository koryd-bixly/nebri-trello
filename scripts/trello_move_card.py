# v0.0.2

import logging

from trello import TrelloClient

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):


logging.basicConfig(filename='trello_move_card.log', level=logging.INFO)


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
        # try:
        #     logging.debug(parent.trello_api_key)
        #     logging.debug('parent found, it worked!!')
        # except:
        #     logging.debug('parent not found. it didnt work')

        client = TrelloClient(
            api_key=self.trello_api_key,
            api_secret=self.trello_api_secret,
            token=self.trello_token,
            token_secret=self.token_secret
        )

        logging.debug('client initialized')

        card = client.get_card(self.card_id)
        cardinfo = card.name.split('_')
        card_items = {
            k:v for (k, v) in [
            out.split('=') for out in card.description.split('\n')
            ]}
        skipdays = card_items.get('skip', '').split(',')

        day_of_week = datetime.now().strftime('%A').lower()

        description = card_items.get('description', '')

        board_name = card_items.get('board', '')
        logging.debug('board name: ' + board_name)

        # get correct board.
        board = card.board
        if board_name:
            # TODO, store this in a model
            all_boards = client.fetch_json('/members/me/boards/',
                                           query_params={'fields': "name, id"})
            for b in all_boards:
                if b.get('name') == board_name:
                    board = client.get_board(b['id'])
                    logging.debug('board id: ' + str(board))
                    break

        if cardinfo.pop(0).lower() == 'deliver' and day_of_week not in skipdays:
            list_name = '_'.join(cardinfo)
            logging.debug(list_name)
            for list in board.open_lists():
                if list.name == list_name:
                    # card found. Now buid it...
                    duedate = datetime.now() + timedelta(days=1)
                    name = 'To Finish by: {}'.format(
                        duedate.strftime('%m-%d-%y, %H:%M')
                    )
                    list.add_card(name, desc=description,
                                  due=str(duedate), source=card.id)
                    # TODO what if list is never found??

        logging.debug(card.id)
        logging.debug(card.name)
        logging.debug(card.description)

        logging.debug('finished')