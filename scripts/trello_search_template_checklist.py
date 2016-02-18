import logging
logging.basicConfig(filename='trello_search_template_checklist.log', level=logging.INFO)

from trello_models import TrelloCard, TrelloUserInfo
from instance_settings import DEFAULT_USER
# 25


class trello_search_template_checklist(NebriOS):
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

        if self.default_user is None:
                self.default_user = DEFAULT_USER

        template_cards = TrelloCard.filter(is_template=True, closed=False, drip=self.drip, user=self.default_user)
        logging.info('starting action')
        logging.info('card gotten')

        self.num_cards = len(template_cards)

        card_ids = []

        logging.info('starting for loop')
        for card in template_cards:
            logging.info('card id: {}'.format(card.idCard))

            if card.idCard in card_ids:
                continue

            p = Process.objects.create()
            p.idCard = card.idCard
            p.drip = self.drip
            p.trello_copy_template = True
            p.default_user = self.DEFAULT_USER
            p.save()

            card_ids.append(card.idCard)

        logging.info('action finished')