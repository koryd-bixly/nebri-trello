from trello_models import TrelloUserInfo

class trello_load_user_emails_card(NebriOS):

    listens_to = ['load_trello_email_card']


    def check(self):
        return self.load_trello_email_card == True

    def action(self):
        self.load_trello_email_card = "Ran"
        self.users_to_update = [{'fullname': user.trello_fullname, 'email':'' } for user in TrelloUserInfo.filter(email='')]
        load_card('trello-emails')