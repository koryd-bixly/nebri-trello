from nebriosmodels import NebriOSField, NebriOSModel

class TrelloCard(NebriOSModel):

    id = NebriOSField(required=True)
    idBoard = NebriOSField(required=True)
    idMembers = NebriOSField() # possible reference to
    idLabels = NebriOSField()
    idChecklists = NebriOSField()
    idList = NebriOSField()

    checklists = NebriOSField()
    due = NebriOSField()
    name = NebriOSField()

    card_json = NebriOSField(required=True)


class TrelloWebhook(NebriOSModel):
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
