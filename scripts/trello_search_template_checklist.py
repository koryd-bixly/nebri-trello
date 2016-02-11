import logging
logging.basicConfig(filename='trello_search_template_checklist.log', level=logging.INFO)

from trello_models import TrelloCard, TrelloUserInfo
from trello_utils import get_card_creator, get_client, template_checklist_parser
# 17


class trello_search_template_checklist(NebriOS):
    listens_to = ['trello_search_template_checklist_new']

    def check(self):
        logging.info('starting check')

        if self.trello_search_template_checklist == True:
            self.check_ok = self.get_or_check_cards(check_only=True)
            return self.check_ok
        return False

    def action(self):
        self.trello_search_template_checklist = 'RAN: {}'.format(datetime.now())

        logging.info('starting action')


        template_cards = self.get_or_check_cards(check_only=False)
        logging.info('card gotten')

        self.num_cards = len(template_cards)

        logging.info('starting for loop')
        for card in template_cards:
            card_items = template_checklist_parser(card)
            card.drip = card_items.get('drip')
            card.save()

        logging.info('action finished')


    def get_or_check_cards(self, check_only=True):

        # TODO put in exclusions
        all_cards = TrelloCard.filter(is_template=True)
        cards = []
        check_ok = False

        logging.info('getting all the cards.....')
        for card in all_cards:
            if card.idLabel is not None or card.idLabel != []:
                if card.idChecklists is not None or card.idChecklists !=[]:
                    card_json = card.card_json
                    if card_json is not None or card_json != '':
                        logging.info('searching card json')
                        labels = card_json.get('labels')
                        if labels is not None or labels != []:
                            for label in labels:
                                if label.get('name') == 'template checklist':
                                    logging.info('card found: {}'.format(card_json))
                                    if check_only:
                                        check_ok = True
                                        return check_ok
                                    else:
                                        logging.info('card added')
                                        cards.append(card)
        if check_only:
            return check_ok
        else:
            return list(set(cards))



