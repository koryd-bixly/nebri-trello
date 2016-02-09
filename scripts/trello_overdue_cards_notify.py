import logging
from collections import defaultdict
# 2

logging.basicConfig(filename='trello_overdue_cards_notify.log', level=logging.DEBUG)

from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator, get_client
from trello import TrelloClient
# 1


class trello_overdue_cards_notify(NebriOS):
    '''
    This script looks for all overdue cards and notifies the creator that
    they are overdue. If a creator is not found, it warns the last actor.
    cards are marked as the warning as been sent so they will not be renotified
    later.
    '''

    listens_to = ['trello_overdue_cards_notify']

    def check(self):
        # look for overdue cards within the last day...
        self.last_actor = 'koryd@bixly.com'
        now = datetime.now()
        run = False
        if self.trello_overdue_cards_notify == True:
            all_overdue_cards = TrelloCard.filter(overdue_notice_sent=False)
            for card in all_overdue_cards:
                if card.duedate is not None:
                    if card.duedate < now:
                        # there is at least one card that we can use
                        run = True
                        break

            return run
        return False

    def action(self):
        self.trello_overdue_cards_notify = 'RAN: ' + str(datetime.now())
        now = datetime.now()

        overdue_cards = []
        all_overdue_cards = TrelloCard.filter(overdue_notice_sent=False)
        for card in all_overdue_cards:
            if card.duedate is not None:
                if card.duedate < now:
                    overdue_cards.append(card)

            client = get_client(self.last_actor)
            notify_users = defaultdict(list)
            for card in overdue_cards:
                if card.idMemberCreator is None:
                    # get card creator if not set in model
                    creator = get_card_creator(card.idCard, client)
                    card.idMemberCreator = creator
                    card.save()
                notify_users[card.idMemberCreator].append(card.shortUrl)
                # may want to move this to the loop below
                card.overdue_notice_sent = True
                card.save()

            for user in notify_users:
                try:
                    trello_user = TrelloUserInfo.get(trello_id=user)
                    send_email(trello_user.email, '''the following cards are overdue:
                    ''' + '\n'.join(notify_users.get(user)))
                except Exception as e:
                    # if the user is not found, then let the last actor know
                    send_email(self.last_actor, '''could not find user: ''' + user)





