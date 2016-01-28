# v0.0.4

import logging

from trello import TrelloClient

# def create_oauth_token(expiration=None, scope=None, key=None, secret=None, name=None, output=True):


logging.basicConfig(filename='trello_search_templates.log', level=logging.DEBUG)


# Get key here: https://trello.com/app-key
# Add shared KVP 'TRELLO_KEY' with a value of the key
# Get token here, replacing API_KEY with the key you got above
# https://trello.com/1/authorize?key=ebf87e6bc0dc4ddc45bbd7e05c87f276&name=Nebri+Scriptrunner&expiration=never&response_type=token&scope=read,write
# Add shared KVP 'TRELLO_TOKEN' with a value of the token


class trello_search_templates(NebriOS):
    # TODO change to schedule
    listens_to = ['trello_search_templates']

    # required = [
    #     'trello_api_key',
    #     'trello_api_secret',
    #     'trello_token',
    #     'token_secret'
    # ]

    def check(self):
        return self.trello_search_templates == True

    def action(self):
        self.trello_search_templates = 'RAN' + str(datetime.now())

        client = TrelloClient(
            api_key=shared.trello_api_key,
            api_secret=shared.trello_api_secret,
            token=shared.trello_token,
            token_secret=shared.token_secret
        )

        boards = client.list_boards()
        for board in boards:
            # see if the template id is in the board.
            found = any(
                shared.template_label_id == la.id for la in board.get_labels(
                    limit=500
                )
            )
            # if template id is not found, keep looking in the next board.
            if not found:
                continue
            cards = board.open_cards()
            for card in cards:
                clabels = card.list_labels

                if clabels and\
                        any(shared.template_label_id == la.id for la in clabels):
                    logging.debug('card found: ' + card.name)
                    logging.debug('card id: ' + card.id)

                    # This could be much niceer with a model...
                    # p = Process.objects.create()
                    # p.card_id = card.id
                    # p.trello_move_card = True
                    # p.save()

                    card_items = {
                        k:v for (k, v) in [
                        out.split('=') for out in card.description.split('\n')
                        ]}



                    p = Process.objects.create()
                    p.create_card_id = card.id
                    p.create_model_card_id = True
                    p.create_custom_send = card_items.get('custom_send', '')
                    p.create_card_items = card_items
                    p.save()

        logging.debug('finished')


