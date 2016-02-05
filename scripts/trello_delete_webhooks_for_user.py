import logging

from trello import TrelloClient


logging.basicConfig(filename='trello_webhook_module.log', level=logging.DEBUG)


class trello_delete_webhooks_for_user(NebriOS):
    
    listens_to = ['trello_delete_webhooks_for_user']

    def check(self):   
        return trello_delete_webhooks_for_user == True
    
    def action(self):
        self.trello_delete_webhooks_for_user = "Ran"
        logging.debug('Doing trello_delete_webhooks_for_user action...')

        client = self.get_client()

        hooks = client.list_hooks()
        
        for hook in hooks:
            logging.debug('Deleting Webhook %s' % hook.id)
            client.fetch_json(
                '/webhooks/%s' % hook.id,
                http_method='DELETE'
            )
        
    def get_client(self):
        return TrelloClient(
            api_key=shared.TRELLO_API_KEY,
            api_secret=shared.TRELLO_API_SECRET,
            token=self.trello_token
        )
    
    def get_me(self):
        client = self.get_client()
        
        return client.fetch_json('/members/me')

    def verify_user(self):
        verified = False
        # Try authenticating with the credentials provided
        # We should not get an authorization error
        
        try:
            self.get_me()
            verified = True
        except Exception:
            # We failed to authenticate with the provided credentials
            pass
        
        return verified