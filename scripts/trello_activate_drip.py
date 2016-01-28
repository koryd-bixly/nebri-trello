from trello_template import TemplateCard

logging.basicConfig(filename='trello_move_card.log', level=logging.INFO)

class trello_activate_drip(NebriOS):

    listens_to = ['custom_send']

    def check(self):
        items = TemplateCard.filter(custom_send=self.custom_send)
        return True if items else False

    def action(self):
        for card in items:
            p = Process.objects.create()
            p.card_id = card.id
            p.trello_move_card = True
            p.custom_send = self.custom_send
            p.save()
