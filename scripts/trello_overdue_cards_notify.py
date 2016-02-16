import logging
logging.basicConfig(filename='trello_overdue_cards_notify.log', level=logging.INFO)

from collections import defaultdict
from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator, get_client
from instance_settings import DEFAULT_USER
# 2


class trello_overdue_cards_notify(NebriOS):
    '''
    This script looks for all overdue cards and notifies the creator that
    they are overdue. If a creator is not found, it warns the default user.
    cards are marked as the warning as been sent so they will not be renotified
    later.
    '''

    listens_to = ['trello_overdue_cards_notify']

    def check(self):
        # look for overdue cards within the last day...
        if self.default_user is None:
            self.default_user = DEFAULT_USER
        logging.info('Starting Check')

        if self.trello_overdue_cards_notify == True:
            self.testcheck = self.get_or_check_cards(check_only=True)
            return self.testcheck
        return False

    def action(self):
        logging.info('Starting Action')
        self.trello_overdue_cards_notify = 'RAN: ' + str(datetime.now())

        overdue_cards = self.get_or_check_cards(check_only=False)
        self.due_cards_len = len(overdue_cards)

        logging.info('getting client')
        client = get_client(self.default_user)
        logging.info('Client found')
        logging.info('client type: {}'.format(type(client)))
        notify_users = defaultdict(list)
        logging.info('starting loop of overdue_cards')
        for card in overdue_cards:
            if card.idMemberCreator is None or card.idMemberCreator is False:
                logging.info('getting card creator: {}'.format(card.idCard))
                # get card creator if not set in model
                creator = get_card_creator(card.idCard, client)
                logging.info('Creator is: {}'.format(creator))
                if creator is None:
                    continue
                card.idMemberCreator = creator
                card.save()
            notify_users[card.idMemberCreator].append(card.shortUrl)

        for user in notify_users:
            try:
                trello_user = TrelloUserInfo.get(trello_id=user)
                if trello_user.email == '':
                    to = self.default_user
                else:
                    to = trello_user.email
                send_email(to, '{id}  the following cards are '
                                              'overdue:\n{tlist}'.format(
                    id=trello_user.trello_fullname,
                    tlist='\n'.join(notify_users.get(user))
                ))
            except Exception as e:
                # if the user is not found, then let the last actor know
                logging.error(str(e))
                send_email(self.default_user, 'could not find user: {}'.format(user))

        # Assuming no issues, disable cards
        for card in overdue_cards:
            card.overdue_notice_sent = True
            card.save()

        logging.info('Script Finished...')

    def get_or_check_cards(self, check_only=True):
        now = datetime.now().to_utc()
        now_seconds = int(now.strftime('%s'))
        logging.info(' Now: {now}, seconds: {s}'.format(
            now=now,
            s=now_seconds
        ))
        all_overdue_cards = TrelloCard.filter(
            due_epoch__lte=now_seconds,
            overdue_notice_sent=False,
            user=self.default_user
        )
        if check_only:
            return len(all_overdue_cards) > 0
        else:
            return all_overdue_cards

