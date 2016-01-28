# v1
from trello_template import TemplateCard
import logging

logging.basicConfig(filename='trello_activate_drip.log', level=logging.INFO)

class trello_activate_drip(NebriOS):

    listens_to = ['custom_send']

    def check(self):
        logging.debug('check')
        items = TemplateCard.filter(custom_send=self.custom_send)
        return True if items else False

    def action(self):
        # not sure if i can pass items from check to action...
        items = TemplateCard.filter(custom_send=self.custom_send)
        self.custom_send = 'RAN ' + str(datetime.now())
        for card in items:
            p = Process.objects.create()
            p.card_id = card.card_id
            p.trello_move_card = True
            p.save()
