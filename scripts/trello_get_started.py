class trello_get_started(NebriOS):
    listens_to = ['setup_trello']

    def check(self):
        return self.setup_trello == True

    def action(self):
        self.trello_api_key = shared.TRELLO_API_KEY
        self.trello_api_secret = shared.TRELLO_API_SECRET
        self.default_user = shared.DEFAULT_USER
        load_card('trello-get-started')
