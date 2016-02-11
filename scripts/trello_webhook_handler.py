from trello_models import Webhook, TrelloCard
import logging
logging.basicConfig(filename='trello_models.log', level=logging.DEBUG)

class trello_webhook_handler(NebriOS):

    listens_to = ['handle_trello_webhook']

    def check(self):
        return self.handle_trello_webhook == True

    def action(self):
        self.handle_trello_webhook = "Ran"
        logging.debug('handle new trello webhook')
        if self.hook_data['action']['type'] == 'updateCard' and self.hook_data['action']['data']['card'].get('closed', False):
            # card has been archived. check for rule prerequisites
            logging.debug('this card was archived!')
            card = TrelloCard.get(idCard=self.card_data.get('id'))
            logging.debug(card)
            logging.debug(card.checklist_finished)
            # let's check checklists first
            if card.checklist_finished == False:
                self.notify_checklist_incomplete = True

            # next let's check for approved status
            approved_commenter = None
            for action in self.comment_data['actions']:
                if action['data']['text'] == 'approved':
                    approved_commenter = action['memberCreator']
                    break
            if approved_commenter is None or \
               approved_commenter['username'] not in self.board_admins:
                self.handle_unapproved_archived = True
