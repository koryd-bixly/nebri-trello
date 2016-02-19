from trello_models import Webhook, TrelloCard, TrelloUserInfo
from trello_utils import unarchive_card
import logging

class trello_notify_checklist_incomplete(NebriOS):

    listens_to = ['notify_checklist_incomplete']

    def check(self):
        return self.notify_checklist_incomplete == True

    def action(self):
        self.notify_checklist_incomplete = 'Ran'
        logging.debug(self.last_actor)
        hook = Webhook.get(model_id=self.card_data['idBoard'])
        card = TrelloCard.get(idCard=self.card_data['id'])
        logging.debug(hook.user)
        unarchived = unarchive_card(self.card_data['id'], hook.user)
        if unarchived == True:
            if len(self.card_data['idMembers']) == 0:
                trello_user = card.creator
                send_email('briem@bixly.com', """
                    Hello, A card has been archived that has an incomplete checklist. It has
                    been unarchived. Please take a moment to look into this matter. %s Thanks!
                    The Nebri Support Team This email should have been sent to %s.
                """ % (self.card_data['shortUrl'], trello_user.trello_username), "An Incomplete Card has been Archived")
            else:
                for id in self.card_data['idMembers']:
                    member = TrelloUserInfo.get(trello_id=id)
                    send_email('briem@bixly.com', """
                    Hello, A card has been archived that has an incomplete checklist. It has
                    been unarchived. Please take a moment to look into this matter. %s Thanks!
                    The Nebri Support Team This email should have been sent to %s.
                    """ % (self.card_data['shortUrl'], member.trello_username), "An Incomplete Card has been Archived")
        else:
            send_email('briem@bixly.com', """
            An error occurred... %s
            """ % unarchived, "An Error Occurred during Archiving")