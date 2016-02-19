from trello_models import Webhook

class trello_handle_setup_complete(NebriOS):

    listens_to = ['cards_imported']

    def check(self):
        return len(Webhook.filter(cards_imported=False)) == 0

    def action(self):
        load_card('trello-webhook-setup-complete')
        p = Process.objects.create()
        p.load_trello_email_card = True
        p.save()