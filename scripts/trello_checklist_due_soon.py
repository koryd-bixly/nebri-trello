import logging
from collections import defaultdict

logging.basicConfig(filename='trello_checklist_due_soon.log', level=logging.DEBUG)

from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator
from trello import TrelloClient

class trello_checklist_due_soon(NebriOS):
    '''
    This will notify all members on a card that it a checklist is due soon.
    '''
    listens_to = ['trello_checklist_due_soon']

    def check(self):
        if self.trello_checklist_due_soon == True:
            now = datetime.now()
            soon = now + timedelta(hours=4)
            soondue_cards = []
            # get all cards with checklists
            cards = [
                card for card in TrelloCard.all() if card.idMembers and
                card.checklist_finished is False and card.duedate and
                now <= card.duedate <= soon
                ]
            self.soondue_cards = soondue_cards

            return True if len(self.soondue_cards) > 0 else False
        else:
            return False


    def action(self):

        member_list = []
        for card in self.soondue_cards:
            member_list = []
            for memberid in card.idMembers:
                try:
                    trello_member = TrelloUserInfo.filter(trello_id=memberid)
                    member_list.append(trello_member.email)
                except:
                    send_mail(self.last_actor,
                              '''could not find user: ''' + memberid)
            if member_list:
                send_mail(member_list, '''You need to finish this card''' +
                          card.shortUrl)

