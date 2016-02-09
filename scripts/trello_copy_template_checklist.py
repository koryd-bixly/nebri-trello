import logging
logging.basicConfig(filename='trello_copy_template_checklist.log', level=logging.INFO)

from collections import defaultdict
from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator, get_client
from instance_settings import DEFAULT_USER
# 1 65654654465


class trello_copy_template_checklist(NebriOS):
    listens_to = ['trello_copy_template_checklist']

    def check(self):

        if self.trello_copy_template_checklist == True:
            pass
        return False

    def action(self):
        pass

    def get_or_check_cards(self, check_only=True):

        all_cards = TrelloCard.filter()
        cards = []
        check_ok = False

        for card in all_cards:
            if card.idLabel is not None or card.idLabel ~= []:
                if card.idChecklists is not None or card.idChecklists ~=[]:
                    if 'template_id' in card.idLabel:
                        if check_ok:
                            check_ok = True
                            return check_ok
                        else:
                            cards.append(card)
        if check_only:
            return check_ok
        else:
            return cards



