import logging
from nebriosmodels import NebriOSField, NebriOSModel

logging.basicConfig(filename='trello_models.log', level=logging.DEBUG)


class TrelloCard(NebriOSModel):

    idCard = NebriOSField(required=True)
    idBoard = NebriOSField()
    idMembers = NebriOSField() # possible reference to
    idLabels = NebriOSField()
    idChecklists = NebriOSField()
    idList = NebriOSField()
    idMemberCreator = NebriOSField(default=False)
    closed = NebriOSField(default=False)

    is_template = NebriOSField(default=False)
    template_idBoard = NebriOSField()
    template_idList = NebriOSField()

    checklists = NebriOSField()
    due = NebriOSField()
    due_epoch = NebriOSField()
    due_datetime = NebriOSField()

    name = NebriOSField()
    shortUrl = NebriOSField(default='')
    drip = NebriOSField()

    overdue_notice_sent = NebriOSField(required=True, default=False)
    card_json = NebriOSField()

    @property
    def checklist_finished(self):
        if self.checklists:
            all_finished = True
            for checklist in self.checklists:
                finished = all(
                    item.get('state') == 'complete'
                    for item in checklist.get('checkItems')
                )
                if not finished:
                    all_finished = False
                    break
            return all_finished
        else:
            return None


class Webhook(NebriOSModel):
    user = NebriOSField(required=True)
    description = NebriOSField(required=True)
    callback = NebriOSField(required=True)
    model_id = NebriOSField(required=True)
    model_type = NebriOSField(required=True)
    trello_id = NebriOSField(required=True, default='')


class TrelloUserInfo(NebriOSModel):
    email = NebriOSField(required=True, default='')
    trello_id = NebriOSField(required=True)
    trello_username = NebriOSField(required=True)
    trello_fullname = NebriOSField(required=True)
