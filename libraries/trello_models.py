from nebriosmodels import NebriOSField, NebriOSModel

class TrelloCard(NebriOSModel):

    idcard = NebriOSField(required=True)
    idBoard = NebriOSField(required=True)
    idMembers = NebriOSField() # possible reference to
    idLabels = NebriOSField()
    idChecklists = NebriOSField()
    idList = NebriOSField()

    checklists = NebriOSField()
    due = NebriOSField()
    name = NebriOSField()

    card_json = NebriOSField(required=True)
