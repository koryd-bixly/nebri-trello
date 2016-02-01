from trello import TrelloClient


class trello_webhook_setup(NebriOS):
    import logging

    logging.basicConfig(filename='Trello_webhook_setup.log', level=logging.DEBUG)

    listens_to = ['trello_webhook_setup']


    # Note: This script is used to set up the trello webhook system.
    # If shared.TRELLO_API_KEY and shared.TRELLO_API_SECRET are not created,
    # you should supply them like so:
    # trello_webhook_setup := True
    # trello_api_key := <api_key>
    # trello_api_secret := <api_secret>
    # instance_name := <instance_name>
    # past_due_notify_address := <past_due_notify_address>
    # completed_notify_address := <completed_notify_address>

    def check(self):
        return self.trello_webhook_setup == True

    def action(self):
        self.trello_webhook_setup = "Ran"
        # check for existance of callback urls
        if shared.TRELLO_WEBHOOK_MEMBER_CALLBACK_URL is None:
            shared.TRELLO_WEBHOOK_MEMBER_CALLBACK_URL = 'https://%s.nebrios.com/api/v1/trello_webhook/member_callback' % self.instance_name
        if shared.TRELLO_WEBHOOK_BOARD_CALLBACK_URL is None:
            shared.TRELLO_WEBHOOK_BOARD_CALLBACK_URL = 'https://%s.nebrios.com/api/v1/trello_webhook/board_callback' % self.instance_name
        # check for existance of trello api key/secret
        if shared.TRELLO_API_KEY is None:
            if self.trello_api_key is not None:
                shared.TRELLO_API_KEY = self.trello_api_key
            else:
                self.logging.debug('No API key found')
                raise Exception('Trello API key does not exist. Please supply one.')
        else:
            self.trello_api_key = shared.TRELLO_API_KEY
        if not shared.TRELLO_API_SECRET:
            if self.trello_api_secret is not None:
                shared.TRELLO_API_SECRET = self.trello_api_secret
            else:
                self.logging.debug('No API Secret found')
                raise Exception('Trello API secret does not exist. Please supply one.')
        shared.PAST_DUE_NOTIFY_ADDRESS = self.past_due_notify_address
        shared.COMPLETED_NOTIFY_ADDRESS = self.completed_notify_address

        # next let's see if the current user has a token already
        token = None
        try:
            p = Process.objects.get(user=self.last_actor, kind="trello_oauth_token")
            token = p.token
            self.logging.debug('token updated')
        except:
            # no token yet, let's load the card.
            self.logging.debug('Need to reauth for token.')
            load_card('trello-token-save')

        client = TrelloClient(shared.TRELLO_API_KEY, shared.TRELLO_API_SECRET, token=token)
        hooked_ids = [h.id_model for h in client.list_hooks()]
        self.logging.debug(hooked_ids)
        lists = []
        cards = []
        boards = []
        for board in client.list_boards():
            boards.append({'id': board.id, 'name': board.name, 'hooked': True if board.id in hooked_ids else False})
            for list in board.all_lists():
                lists.append({'id': list.id, 'name': list.name, 'hooked': True if list.id in hooked_ids else False})
            for card in board.all_cards():
                cards.append({'id': card.id, 'name': card.name, 'hooked': True if card.id in hooked_ids else False})
        # self.lists = lists
        # self.cards = cards
        self.boards = boards
        self.logging.debug('load settings card')
        load_card('trello-webhook-settings')