from trello_webhook import TrelloUserInfo


class trello_email_load_card(NebriOS):

    listens_to = ['load_trello_email_card']

    def check(self):
        return self.load_trello_email_card == True

    def action(self):
        self.load_trello_email_card = "Ran"
        # get all trello user info that are missing emails
        trello_users_to_update = TrelloUserInfo.filter(email='')
        self.users = [{'username': user.trello_username, 'email': ''} for user in trello_users_to_update]
        load_card('trello-emails')