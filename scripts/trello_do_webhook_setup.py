from trello_utils import setup_webhooks

class trello_do_webhook_setup(NebriOS):

    listens_to = ['trello_watch_boards_for_user']


    def check(self):
        return self.trello_watch_boards_for_user == True

    def action(self):
        self.trello_watch_boards_for_user = "Ran"
        load_card('trello-please-wait')
        setup_webhooks(self.user)