from trello_webhook import TrelloUserInfo, Webhook


class trello_webhook_handler(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['handle_trello_webhook']

    def check(self):
        return self.handle_trello_webhook == True

    def action(self):
        self.handle_trello_webhook = "Ran"
        # check for existance of callback urls
        webhook = TrelloUserInfo.filter(email='')
        self.users = [{'username': user.trello_username, 'email': ''} for user in trello_users_to_update]
        load_card('trello-emails')