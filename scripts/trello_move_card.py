# v0.0.3
# requires: croniter,  pip install git+https://github.com/sarumont/py-trello

import logging
from croniter import croniter

from trello import TrelloClient

from trello_prebuilt import PREBUILT

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):


logging.basicConfig(filename='trello_move_card.log', level=logging.INFO)


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
        self.trello_move_card = 'Ran'
        logging.debug('start action')
        # try:
        #     logging.debug(parent.trello_api_key)
        #     logging.debug('parent found, it worked!!')
        # except:
        #     logging.debug('parent not found. it didnt work')
        if self.card_id == '':
            # TODO add check to see if this card is pending...
            pass

        client = TrelloClient(
            api_key=self.trello_api_key,
            api_secret=self.trello_api_secret,
            token=self.trello_token,
            token_secret=self.token_secret
        )

        logging.debug('client initialized')

        card = client.get_card(self.card_id)
        card_items = {
            k:v for (k, v) in [
            out.split('=') for out in card.description.split('\n')
            ]}
        skipdays = card_items.get('skip', '').split(',')

        day_of_week = datetime.now().strftime('%A').lower()

        description = card_items.get('description', '')

        board_name = card_items.get('board', '')
        list_name = card_items.get('list', '')
        logging.debug('board name: ' + board_name)
        logging.debug('list name: ' + list_name)

        # get correct board. This could be moved to its own function
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

        # get correct list. This could be moved to its own funciton
        list = card.get_list()
        for blist in board.open_lists():
                if blist.name == list_name:
                    list = blist
                    break

        # get correct time detla
        indelta = card_items.get('due', 'day')
        inschedule = card_items.get('schedule', '')

        # next check for cron type scheduler
        if inschedule:
            duedate = croniter(inschedule).get_next(datetime)
        else:
            delta = PREBUILT.get(indelta, timedelta(days=1))
            duedate = datetime.now() + delta

        if day_of_week not in skipdays:
            # card found. Now buid it...
            name = 'To Finish by: {}'.format(
                duedate.strftime('%m-%d-%y, %H:%M')
            )
            new = list.add_card(name, desc=description,
                          due=str(duedate), source=card.id)

            # put card to top of list
            new.set_pos('top')

            # remove template label, so it does not get run again...
            for label in new.labels:
                if label.name == 'template checklist':
                    new.remove_label(label)
                    break

            # TODO create model to save card details. Check this model to see if
            # current card is still pending.

        logging.debug(card.id)
        logging.debug(card.name)
        logging.debug(card.description)

        logging.debug('finished')