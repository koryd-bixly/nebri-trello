import logging

from trello import TrelloClient

class trello_poll_watched_boards(NebriOS):

    schedule = '0 0 * * *'

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

        for board in watched_boards:
            # due in cards does not seem to be working properly...
            # cards =
            for card in board.open_cards():
                card.fetch() # extra api call...
                duedate = card.due_date()
                now = datetime.now()
                oneday = now + timedelta(days=1)
                checklists = card.checklists
                if duedate and checklists and now <= duedate <= oneday:
                    # checks if all items in checklist are finished
                    finished = all([item.get('checked', False) for item in
                                checklist.items for checklist in checklists])
                    if not finished:
                        # check checklist
                        send_mail('koryd@bixly.com', '''
                        its not done yet''')



