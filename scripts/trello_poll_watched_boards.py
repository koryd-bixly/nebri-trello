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
            # TODO make a library from this...
            cards = client.fetch_json(
                'boards/{id}/cards/'.format(id=board.id),
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
                if duedate and now <= duedate <= oneday:
                    checklists = card.get('checklists')
                    warn = False
                    for checklist in checklists:
                        finished = all(
                            item.get('state') == 'complete'
                            for item in checklist.get('checkItems')
                        )
                        if not finished:
                            warn = True
                            break
                    if warn:
                        # check checklist
                        send_mail('koryd@bixly.com', '''
                        its not done yet''')



