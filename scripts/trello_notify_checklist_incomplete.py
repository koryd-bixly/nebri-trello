from trello_models import Webhook, TrelloCard, TrelloUserInfo
from trello_utils import unarchive_card, get_card_creator

class trello_notify_checklist_incomplete(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['notify_checklist_incomplete']

    def check(self):
        return self.notify_checklist_incomplete == True

    def action(self):
        self.notify_checklist_incomplete = 'Ran'
        # self.logging.debug('inside notify_checklist_incomplete')
        # self.logging.debug(self.hook_data)
        # self.logging.debug(self.card_data)
        # self.logging.debug(self.comment_data)
        # self.logging.debug(self.board_admins)

        if len(self.card_data['idMembers']) == 0:
            creator_id = get_card_creator(self.card_data['id'], params={'last_actor': self.last_actor})
            trello_user = TrelloUserInfo.get(trello_id=card.idMemberCreator)
            send_email(trello_user.email, """
            Hello, A card has been archived which was not approved by a board admin. It has
            been unarchived. Please take a moment to look into this matter. %s Thanks!
            The Nebri Support Team
            """ % self.card_data.shortUrl, "An Unapproved Card has been Archived")
        else:
            for member in self.card_data['idMembers']:
                trello_user = TrelloUserInfo.get(trello_id=member)
                send_email(trello_user.email, """
                Hello, A card has been archived that has an incomplete checklist. It has
                been unarchived. Please take a moment to look into this matter. %s Thanks!
                The Nebri Support Team
                """ % self.card_data.shortUrl, "An Incomplete Card has been Archived")

        # card = TrelloCard.get(idCard=self.card_data['id'])
        # unarchived = unarchive_card(self.card_data['id'], self.last_actor)
        # if unarchived == True:
        #
        # else:
        #     self.logging.debug(unarchived)