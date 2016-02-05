from trello_models import Webhook, TrelloCard, TrelloUserInfo
from trello_utils import unarchive_card

class trello_handle_unapproved_archived(NebriOS):
    import logging

    logging.basicConfig(filename='trello_webhook_handler.log', level=logging.DEBUG)

    listens_to = ['handle_unapproved_archived']

    def check(self):
        return self.handle_unapproved_archived == True

    def action(self):
        self.handle_unapproved_archived = 'Ran'
        self.logging.debug('inside handle_unapproved_archived')
        self.logging.debug(self.hook_data)
        self.logging.debug(self.card_data)
        self.logging.debug(self.comment_data)
        self.logging.debug(self.board_admins)

        card = TrelloCard.get(idCard=self.card_data['id'])
        unarchived = unarchive_card(self.card_data['id'], self.last_actor)
        if unarchived == True:
            trello_user = TrelloUserInfo.get(trello_id=card.idMemberCreator)
            send_email(trello_user.email, """
            Hello, A card has been archived which was not approved by a board admin. It has
            been unarchived. Please take a moment to look into this matter. %s Thanks!
            The Nebri Support Team
            """ % self.card_data.shortUrl, "An Unapproved Card has been Archived")
        else:
            self.logging.debug(unarchived)