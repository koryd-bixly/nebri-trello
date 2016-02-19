from trello_utils import boardid_to_cardmodels

class trello_do_card_import(NebriOS):

    listens_to = ['trello_import_cards']


    def check(self):
        return self.trello_import_cards == True

    def action(self):
        self.trello_import_cards = "Ran"
        boardid_to_cardmodels(self.boardId, user=self.user)
