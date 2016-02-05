from trello_models import Webhook, TrelloCard

class trello_handle_unapproved_archived(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['handle_unapproved_archived']

    def check(self):
        return self.handle_unapproved_archived == True

    def action(self):
        self.handle_unapproved_archived = 'Ran'
        self.logging.debug('inside handle_unapproved_archived')
        self.logging.debug(self.hook_data)
        self.logging.debug(self.card_data)
        self.logging.debug(self.comment_data)
        self.logging.debug(self.board_admins)