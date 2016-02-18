from trello_utils import setup_webhooks, delete_hooks

class trello_do_webhook_setup(NebriOS):

    listens_to = ['trello_watch_boards_for_user']


    def check(self):
        return self.trello_watch_boards_for_user == True

    def action(self):
        self.trello_watch_boards_for_user = "Ran"
        try:
            delete_hooks(self.user)
            setup_webhooks(self.user)
        except Exception as e:
            self.error = str(e)
        load_card('trello-webhook-setup-complete')