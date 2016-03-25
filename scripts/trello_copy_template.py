# 5
import logging
logging.basicConfig(filename='trello_copy_template.log', level=logging.INFO)
from trello_models import TrelloCard, TrelloUserInfo
from trello import TrelloClient
from trello_utils import get_client, template_checklist_parser, template_checklist_setup, copy_template_card

from trello_prebuilt import PREBUILT
# from instance_settings import DEFAULT_USER

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):



class trello_copy_template(NebriOS):
    listens_to = ['trello_copy_template']

    def check(self):
        logging.info('start check')
        if self.default_user is None:
            self.default_user = shared.DEFAULT_USER
        if self.trello_copy_template == True:
            try:
                card = TrelloCard.get(
                    idCard=self.idCard,
                    is_template=True,
                    closed=False,
                    drip=self.drip,
                    user=self.default_user
                )
                logging.info('card found')
            except Exception as e:
                logging.error('Error in copy template')
                logging.error(str(e))
                self.card_get_error = str(e)
                return False
            if card:
                return True

        return False

    def action(self):
        self.trello_copy_template = 'RAN: {}'.format(datetime.now())
        logging.info('start action')

        client = get_client(self.default_user)
        logging.info('client found')
        card = TrelloCard.get(idCard=self.idCard, user=self.default_user)

        card = template_checklist_setup(card, client)
        self.template_idList = card.template_idList
        logging.info('template_list {}'.format(card.template_idList))
        # self.json_data = card.card_json
        # self.description = self.json_data.get('description')
        logging.info('card updated')


        out = copy_template_card(client, card)

        self.out = out.id

        # if new_card is not None:
        #     self.new_id = new_card.id

        logging.info('finished')


