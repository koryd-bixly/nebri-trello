from trello_models import TrelloCard

import logging

logging.basicConfig(filename='trello_poll_watched_boards.log', level=logging.INFO)

from trello import TrelloClient

class trello_poll_watched_boards(NebriOS):

    listens_to = ['trello_poll_watched_boards']

    def check(self):
        logging.info(self.last_actor)
        try:
            p = Process.objects.get(kind="trello_oauth_token", user=self.last_actor)
                                    # last_actor=self.last_actor)
        except Process.DoesNotExist as e:
            logging.info(e)
            return False
        self.trello_token = p.token
        self.trello_api_key = shared.trello_api_key
        required = self.trello_token and self.trello_api_key
        return self.trello_poll_watched_boards == True and required

    def action(self):
        # TODO add this to some general login script
        client = TrelloClient(
            self.trello_api_key,
            token=self.trello_token  # get
        )

        # TODO add in filter to watched boards
        # watched_boards = Boards.filter()
        watched_boards = client.list_boards()  # TEMP

        # setup query_params

        for idx, board in enumerate(watched_boards):
            # due in cards does not seem to be working properly...
            # cards =
            # TODO make a library from this...
            cards += client.fetch_json(
                'boards/{id}/cards/'.format(id=board.id),
                query_params=params
            )


    def process_board(self, boardid, client, params=None):

       cards = json_cards_from_board(boardid, client, params)

       for card in cards:
           TrelloClient.get_or_create(idcard=)


        # TODO make its own function.
        # lambda: TrelloCard.get_or_create(**card) for card in cards


    def json_cards_from_board(self, boardid, client, params=None):
        if params is None:
            params = dict(
                checklists='all'
            )
        yield client.fetch_json(
            'boards/{id}/cards/'.format(id=board.id),
            query_params=params
        )



        # shared.trello_cards = cards

        # TODO add this to a new script later...
        #
        # for card in cards:
        #     due = card.get('due', None)
        #     # convert string due to datetime
        #     try:
        #         duedate = datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ')
        #     except Exception as e:
        #         # if unable to process, then go to next card
        #         logging.info(
        #             'could not parse datetime on card: ' + card.get('id')
        #         )
        #         continue
        #
        #     now = datetime.now()
        #     oneday = now + timedelta(days=1)
        #     if duedate and now <= duedate <= oneday:
        #         checklists = card.get('checklists')
        #         warn = False
        #         for checklist in checklists:
        #             finished = all(
        #                 item.get('state') == 'complete'
        #                 for item in checklist.get('checkItems')
        #             )
        #             if not finished:
        #                 warn = True
        #                 break
        #         if warn:
        #             # check checklist
        #             send_mail('koryd@bixly.com', '''
        #             its not done yet''')
