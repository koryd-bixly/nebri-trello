import logging
from collections import defaultdict
# 8
logging.basicConfig(filename='trello_checklist_due_soon.log', level=logging.INFO)

from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator
from trello import TrelloClient

class trello_checklist_due_soon(NebriOS):
    '''
    This will notify all members on a card that it a checklist is due soon.
    '''
    listens_to = ['trello_checklist_due_soon']

    def check(self):
        logging.info('THIS IS A TEST')
        run = False
        if self.trello_checklist_due_soon == True:
            now = datetime.now() - timedelta(days=4)
            soon = now + timedelta(hours=24)
            all_cards = TrelloCard.filter()

            # See if there are any cards that have checklists
            self.num_cards = len(all_cards)
            logging.info('number of cards: {}'.format(self.num_cards))
            for card in all_cards:
                if card.idMembers is not None and \
                                card.checklist_finished is not None and \
                                card.duedate is not None:
                    logging.info('card date: {}'.format(card.due))
                    logging.info('checklsit finished: {}'.format(card.checklist_finished))

                    if now <= card.duedate <= soon and card.checklist_finished is False:
                        run = True
                        break

            return False
        else:
            return False


    def action(self):
        self.trello_checklist_due_soon = 'RAN: ' + str(datetime.now())
        logging.info('running action: ' + str(datetime.now()))

        now = datetime.now() - timedelta(days=4)
        soon = now + timedelta(hours=24)
        soondue_cards = []
        all_cards = TrelloCard.filter()
        for card in all_cards:
                if card.idMembers is not None and \
                                card.checklist_finished is not None and \
                                card.duedate is not None:

                    if now <= card.duedate <= soon and card.checklist_finished is False:
                        logging.info('card date: {}'.format(card.due))
                        soondue_cards.append(card)

        user_not_found = []
        logging.info('soon due cards: {}'.format(len(soondue_cards)))
        for card in soondue_cards:
            logging.info('card members: {}'.format(card.idMembers))
            member_list = []
            for memberid in card.idMembers:
                try:
                    trello_member = TrelloUserInfo.get(trello_id=memberid)
                    logging.info('trello_member: {}'.format(trello_member))
                except Exception as e:
                        logging.error(str(e))
                        send_email(self.last_actor,
                                  '''could not find user: ''' + memberid)
                if trello_member == '' or trello_member is None:
                    logging.info('user not found: {}'.format(memberid))
                    if memberid not in user_not_found:
                        user_not_found.append(memberid)
                        send_email(self.last_actor,
                                   '''could not find user: ''' + memberid)
                        continue
                    if trello_member.email is None or trello_member.email == '':
                        user_not_found.append(memberid)
                        send_email(self.last_actor,
                                   '''could not find user: ''' + memberid)
                        continue
                member_list.append(trello_member.email)
            logging.info('member list: {}'.format(member_list))
            if member_list:
                send_email(
                    self.last_actor,
                    '''You need to finish this card ''' + str(card.shortUrl),
                    'Unfinished checklist (PID:{})'.format(self.PROCESS_ID)
                )

        logging.info('Action Finished...')


    def get_cards(self, check_only=True):
        
