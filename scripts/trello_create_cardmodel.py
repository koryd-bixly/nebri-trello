from trello_template import TemplateCard

class trello_create_cardmodel(NebriOS):
    listens_to = ['create_model_card_id']

    def check(self):
        _, checkme = TemplateCard.get_or_create(
            cardid=self.create_model_card_id,
            custom_send=self.create_custom_send
        )
        return checkme

    def action(self):
        card = TemplateCard.get(cardid=self.create_model_card_id)

