from trello_models import Webhook, TrelloCard, TrelloUserInfo
from trello_utils import unarchive_card

class trello_handle_unapproved_archived(NebriOS):

    listens_to = ['handle_unapproved_archived']

    def check(self):
        return self.handle_unapproved_archived == True

    def action(self):
        self.handle_unapproved_archived = 'Ran'
        hook = Webhook.get(model_id=self.card_data['idBoard'])
        try:
            card = TrelloCard.get(idCard=self.card_data['id'], user=self.default_user)
        except Process.DoesNotExist:
            return

        unarchived = unarchive_card(self.card_data['id'], hook.user)
        if unarchived == True:
            trello_user = card.creator
            to = trello_user.email if trello_user.email != '' else 'briem@bixly.com'
            send_email(to, """
            Hello, A card has been archived which was not approved by a board admin. It has
            been unarchived. Please take a moment to look into this matter. %s Thanks!
            The Nebri Support Team This email should have been sent to %s.
            """ % (self.card_data['shortUrl'], trello_user.trello_username), "An Unapproved Card has been Archived")
        else:
            send_email('briem@bixly.com', """
            An error occurred... %s
            """ % unarchived, "An Error Occurred during Archiving")