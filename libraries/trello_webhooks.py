from nebriosmodels import NebriOSField, NebriOSModel, NebriOSReference, NebriOSReferenceList
from trello_webhook import _get_client


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
