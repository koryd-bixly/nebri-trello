# v4
from trello_template import TemplateCard

import logging

logging.basicConfig(filename='trello_create_cardmodel.log', level=logging.INFO)

class trello_create_cardmodel(NebriOS):
    listens_to = ['create_model_card_id']

    required = ['create_card_id']

    def check(self):
        # card_items = self.create_card_itmes
        try:
            self.test = self.create_card_items.get('custom_send', 'NOPE')
        except:
            pass
        _, checkme = TemplateCard.get_or_create(
            card_id=self.create_card_id,
            custom_send=self.create_custom_send
        )
        return checkme and self.create_model_card_id == True

    def action(self):
        card = TemplateCard.get(card_id=self.create_card_id)
        self.create_model_card_id = 'RAN ' + str(datetime.now())

        # move card right away.
        p = Process.objects.create()
        p.card_id = card.card_id
        p.trello_move_card = True
        p.save()

