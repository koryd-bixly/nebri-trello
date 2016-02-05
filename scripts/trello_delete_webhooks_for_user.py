from trello_utils import delete_hooks


class trello_delete_webhooks_for_user(NebriOS):
    
    listens_to = ['trello_delete_webhooks_for_user']

    def check(self):   
        return self.trello_delete_webhooks_for_user == True
    
    def action(self):
        if self.hook_id:
            deleted = delete_hooks(self.last_actor, self.hook_id)
        else:
            deleted = delete_hooks(self.last_actor)

        self.trello_delete_webhooks_for_user = deleted