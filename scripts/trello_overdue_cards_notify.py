import logging
logging.basicConfig(filename='trello_overdue_cards_notify.log', level=logging.DEBUG)

from trello_models import TrelloCard


class trello_overdue_cards_notify(NebriOS):

    listens_to = ['trello_overdue_cards_notify']

    def check(self):
        # look for overdue cards within the last day...
        if self.trello_overdue_cards_notify == True:
            self.overdue_cards = TrelloCard.filter(overdue_notice_sent=False)

            return True if len(self.overdue_cards) > 0 else False
        return False

    def action(self):
        self.trello_overdue_cards_notify = 'RAN: ' + str(datetime.now())
        newlist = []
        for card in self.overdue_cards:
            if card.duedate:
                newlist.append(card)

        self.numoverdue = len(newlist)


