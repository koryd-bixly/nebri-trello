# v0.0.10
# requires: croniter,  pip install git+https://github.com/sarumont/py-trello

import logging
logging.basicConfig(filename='trello_move_card.log', level=logging.INFO)
from trello_models import TrelloCard, TrelloUserInfo
from trello import TrelloClient
from trello_utils import get_card_creator, get_client, template_checklist_parser

from trello_prebuilt import PREBUILT

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):



class trello_move_card(NebriOS):
    listens_to = ['trello_move_card']

    def check(self):
        logging.debug('starting check')
        return False
        if not self.trello_move_card.startswith('RAN'):
            return True

    def action(self):
        self.trello_move_card = 'RAN :' + str(datetime.now())
        logging.debug('start action')

        template_cards = TrelloCard.filter(drip=self.trello_move_card)
        self.number_template_cards = len(template_cards)

        logging.info('getting client')
        client = get_client(self.last_actor)
        logging.info('Client found')
        logging.info('client type: {}'.format(type(client)))

        logging.debug('client initialized')

        for tcard in template_cards:
            card_items = template_checklist_parser(tcard)
            card = client.get_card(tcard.idCard)

            # get correct board. This could be moved to its own function
            board = card.board
            board_name = card_items.get('board')
            list_name = card_items.get('list_name')
            if board_name is not None:
                # TODO, store this in a model
                all_boards = client.fetch_json('/members/me/boards/',
                                               query_params={'fields': "name, id"})
                for b in all_boards:
                    if b.get('name') == card_items.get('board'):
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

            # next check for cron type scheduler
            delta = PREBUILT.get(indelta, timedelta(days=1))
            duedate = datetime.now() + delta

            # card found. Now buid it...
            name = 'To Finish by: {}'.format(
                duedate.strftime('%m-%d-%y, %H:%M')
            )
            description = card_items.get('description', 'Please Finish')
            new = list.add_card(name, desc=description, labels=[],
                          due=str(duedate), source=card.id)

            # put card to top of list
            new.set_pos('top')

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
