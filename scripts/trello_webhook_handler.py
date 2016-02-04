from trello_models import TrelloWebhook, TrelloCard

class trello_webhook_handler(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['handle_trello_webhook']

    def check(self):
        return self.handle_trello_webhook == True

    def action(self):
        self.handle_trello_webhook = "Ran"
        self.logging.debug(self.raw_data)
        # check for existance of callback urls
        webhook = TrelloWebhook.get(trello_id=self.raw_data['action']['data']['id'])
        card = TrelloCard.get(id=self.raw_data['action']['data']['id'])

        if self.raw_data['action']['data']['type'] == 'updateCard' && self.raw_data['model']['closed'] == True:
            # card has been archived. check for rule prerequisites

