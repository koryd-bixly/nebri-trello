from trello_models import Webhook, TrelloCard

class trello_webhook_handler(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['handle_trello_webhook']

    def check(self):
        return self.handle_trello_webhook == True

    def action(self):
        self.handle_trello_webhook = "Ran"
        # self.logging.debug('inside trello_webhook_handler')
        # self.logging.debug(self.hook_data)
        # self.logging.debug(self.card_data)
        # self.logging.debug(self.comment_data)
        # self.logging.debug(self.board_admins)

        card = TrelloCard.get(idcard=self.card_data.get('id'))
        # self.logging.debug(card)

        if self.hook_data['action']['data']['type'] == 'updateCard' && self.hook_data['model']['closed'] == True:
            # card has been archived. check for rule prerequisites
            # let's check checklists first
            if card.checklist_finished == False:
                self.notify_checklist_incomplete = True
                self.save()

            # next let's check for approved status
            approved_commenter = {}
            for action in self.comment_data['actions']:
                if action['data']['text'] == 'approved':
                    approved_commenter = action['memberCreator']
                    break
            if approved_commenter['username'] not in self.board_admins:
                self.handle_unapproved_archived = True
                self.save()
