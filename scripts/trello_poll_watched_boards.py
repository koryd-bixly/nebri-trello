import logging

from trello import TrelloClient

class trello_poll_watched_boards(NebriOS):

    schedule = '0 */2 * * *'

    def action(self):
        # TODO add this to some general login script
        client = TrelloClient(
            shared.TRELLO_API_KEY,
            shared.TRELLO_API_SECRET,
            token=token  # get
        )

        # TODO add in filter to watched boards
        # watched_boards = Boards.filter()
        watched_boards = client.list_boards()  # TEMP

        # setup query_params
        params = dict(
            checklists='all'
        )

        for board in watched_boards:
            # due in cards does not seem to be working properly...
            # cards =
            cards = client.fetch_json(
                'boards/{}/cards/'.format(board.id),
                query_params=params
            )
            for card in board.open_cards():
                due = card.get('due', None)
                # convert string due to datetime
                try:
                    duedate = datetime.strptime(due, '%Y-%m-%dT%H:%M:%S.%fZ')
                except Exception as e:
                    # if unable to process, then go to next card
                    logging.info(
                        'could not parse datetime on card: ' + card.get('id')
                    )
                    continue

                now = datetime.now()
                oneday = now + timedelta(days=1)
                checklists = card.get('checklists')
                for checklist in checklists:
                    finished = all(
                        item.get('state') == 'complete'
                        for item in checklist.get('checkItems')
                    )

                if duedate and checklists and now <= duedate <= oneday:
                    # checks if all items in checklist are finished
                    finished = all([item.get('checked', False) for item in
                                checklist.items for checklist in checklists])
                    if not finished:
                        # check checklist
                        send_mail('koryd@bixly.com', '''
                        its not done yet''')



