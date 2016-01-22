import logging
import requests

logging.basicConfig(filename='trello_oauth_setup.log', level=logging.DEBUG)


class trello_oauth_setup(NebriOS):

    listens_to = ['trello_oauth_setup']
    required = [
        'trello_api_key',
        'trello_api_secret'
    ]

    def check(self):
        return self.trello_oauth_setup == True

    def action(self):
        self.trello_oauth_setup = 'Ran'

        # get proper callback urls
        if self.trello_oauth_callback is None:
            self.trello_oauth_callback = 'https://%s.nebrios.com/api/v1/trello_oauth_callback/member_callback' % self.instance_name




