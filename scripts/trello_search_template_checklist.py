import logging
logging.basicConfig(filename='trello_search_template_checklist.log', level=logging.INFO)

from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator, get_client, template_checklist_parser
from instance_settings import DEFAULT_USER
# 17


class trello_search_template_checklist_new(NebriOS):
    listens_to = ['trello_search_template_checklist']

    def check(self):
        logging.info('starting check')

        if type(self.trello_search_template_checklist) == str:
            if not self.trello_search_template_checklist.startswith('RAN'):
                self.drip = self.trello_search_template_checklist
                return True
        return False

    def action(self):
        self.trello_search_template_checklist = 'RAN: {}'.format(datetime.now())

        template_cards = TrelloCard.filter(is_template=True, closed=False, drip=self.drip)
        logging.info('starting action')
        logging.info('card gotten')

        self.num_cards = len(template_cards)

        logging.info('starting for loop')
        for card in template_cards:

            if self.DEFAULT_USER is None:
                self.DEFAULT_USER = DEFAULT_USER

            p = Process.objects.create()
            p.idCard = card.idCard
            p.trello_copy_template = True
            p.default_user = self.DEFAULT_USER
            p.save()

        logging.info('action finished')