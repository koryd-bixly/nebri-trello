from trello_models import TrelloCard, Webhook, TrelloUserInfo
from instance_settings import INSTANCE_HTTPS_URL
import logging

logging.basicConfig(filename='trello_utils.log', level=logging.DEBUG)


def boardid_to_cardmodels(idboard, client):
    # pass a board id to get all the card models created or updated.
    cards = json_cards_from_board(idboard, client)
    members = json_members_from_board(idboard, client)
    hooked_ids = [
        h.get('idModel') for h in
        client.fetch_json('/members/me/tokens?webhooks=true')
        if h.get('idModel')
        ]

    for card in cards:
        card_json_to_model(card)
        create_webhook(card, client, hooked_ids=hooked_ids)

    for member in members:
        member_json_to_model(member)


def json_members_from_board(boardid, client):
    return client.fetch_json(
        'boards/{id}/members/'.format(id=boardid)
    )


def json_cards_from_board(boardid, client, params=None):
    # generator for cards
    if params is None:
        params = dict(
            checklists='all'
        )
    return client.fetch_json(
        'boards/{id}/cards/'.format(id=boardid),
        query_params=params
    )


def card_json_to_model(card):

    logging.info('card list is next: ')
    logging.info(str(card))
    card_obj, new = TrelloCard.get_or_create(idCard=card.get('id'))

    # update card

    # check webhook json response
    card_obj.idBoard = card.get('idBoard')
    card_obj.idMembers = card.get('idMembers')
    card_obj.idLabels = card.get('idLabels')
    card_obj.idChecklists = card.get('idChecklists')
    card_obj.idList = card.get('idLists')
    card_obj.checklists = card.get('checklists')
    card_obj.due = card.get('due')
    card_obj.name = card.get('name')
    card_obj.card_json = card
    card_obj.save()

    return card_obj, new


def member_json_to_model(member):
    member_obj, new = TrelloUserInfo.get_or_create(trello_id=member.get('id'))

    member_obj.trello_username = member.get('username')
    member_obj.trello_fullname = member.get('fullName')
    member_obj.save()

    return member_obj, new


def create_webhook(card, client, hooked_ids=None):
    if hooked_ids is None:
        hooked_ids = [h.get('idModel') for h in client.fetch_json('/members/me/tokens?webhooks=true') if h.get('idModel')]
    if card.get('id') not in hooked_ids:
        card_name = card.get('name').decode("utf-8", "replace")
        hook = {
            'desc': 'Webhook for card %s' %  card_name,
            'callback_url': '%s/api/v1/trello_webhook/callback?id=%s' %(INSTANCE_HTTPS_URL, card.get('id')),
            'id_model': card.get('id'),
            'type_model': 'card'
        }

        webhook = client.create_hook(hook['callback_url'], hook['id_model'], desc=hook['desc'])
        if webhook:  # returns false if it doesn't work
            new_hook = Webhook(
                description=hook['desc'],
                callback=hook['callback_url'],
                model_id=hook['id_model'],
                model_type=hook['type_model'],
                trello_id=webhook.id
            )
            new_hook.save()
            hooked_ids.append(card.get('id'))


def get_card_creator(idcard, client, params=None):
    # gets the idmemberCreator needed EVERYWHERE and should be returned already.
    if params is None:
        param = dict(fields='idMemberCreator')

    try:
        response = client.fetch_json(
            'cards/{id}/actions'.format(id=idcard),
            query_params=params
        )
    except Exception as e:
        logging.error(str(e))
        creator = None
    else:
        creator = response.get('idMemberCreator')

    return creator

