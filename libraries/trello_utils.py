from trello_models import TrelloCard, Webhook, TrelloUserInfo
from instance_settings import INSTANCE_HTTPS_URL
from trello import TrelloClient
import logging

logging.basicConfig(filename='trello_utils.log', level=logging.DEBUG)


def boardid_to_cardmodels(idboard, client=None, user=None):
    # pass a board id to get all the card models created or updated.
    cards = json_cards_from_board(idboard, client)
    members = json_members_from_board(idboard, client)
    hooked_ids = [
        h.get('idModel') for h in
        client.fetch_json('/members/me/tokens?webhooks=true')
        if h.get('idModel')
        ]

    create_webhook(idboard, client, hooked_ids=hooked_ids)

    for card in cards:
        card_json_to_model(card)

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
    card_obj.shortUrl = card.get('shortUrl')
    card_obj.card_json = card
    card_obj.save()

    return card_obj, new


def member_json_to_model(member):
    try:
        member_obj = TrelloUserInfo.get(trello_id=member.get('id'))
    except Process.DoesNotExist:
        logging.debug('create new.....')
        member_obj = TrelloUserInfo(trello_id=member.get('id'))
    except Exception as e:
        logging.debug(str(e))
        if len(TrelloUserInfo.filter(trello_id=member.get('id'))) > 1:
            member_obj = TrelloUserInfo.filter(trello_id=member.get('id'))[-1]
            TrelloUserInfo.filter(trello_id=member.get('id')).delete()

    member_obj.trello_username = member.get('username')
    member_obj.trello_fullname = member.get('fullName')
    member_obj.save()

    return member_obj


def create_webhook(idboard, client, hooked_ids=None):
    if hooked_ids is None:
        hooked_ids = [h.get('idModel') for h in client.fetch_json('/members/me/tokens?webhooks=true') if h.get('idModel')]

    if idboard not in hooked_ids:
        board = client.fetch_json('/boards/%s' % idboard)
        hook = {
            'desc': 'Webhook for card %s' %  board.get('name'),
            'callback_url': '%s/api/v1/trello_webhook/callback?id=%s' %(INSTANCE_HTTPS_URL, idboard),
            'id_model': idboard,
            'type_model': 'board'
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
            hooked_ids.append(idboard)


def unarchive_card(card_id, last_actor):
    client = get_client(last_actor)
    if client != None:
        trello_card = client.get_card(card_id)
        try:
            trello_card.set_closed(False)
            return True
        except Exception as e:
            return 'error: %s' % str(e)


def _get_trello_token(user):
    try:
        return Process.objects.get(kind="trello_oauth_token", user=user).token
    except:
        load_card('trello-token-save')
        raise Exception('Token does not exist. Please supply one on the Trello OAuth Token Creation card or run trello_webhook_setup.')
    return ""


def get_client(user):
    token = _get_trello_token(user)
    try:
        return TrelloClient(api_key=shared.TRELLO_API_KEY, api_secret=shared.TRELLO_API_SECRET, token=token)
    except:
        raise Exception('API key or secret is missing. Please supply values in shared KVPs.')
    return None


def get_card_creator(idcard, client=None, params=None):
    # gets the idmemberCreator needed EVERYWHERE and should be returned already.
    if client is None:
        try:
            client = get_client(params['last_actor'])
            params = None
        except Exception as e:
            raise Exception('Could not get client: %s' % str(e))
    if params is None:
        params = dict(fields='idMemberCreator')
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


def delete_hooks(user, hook_id=None):
    try:
        client = get_client(user)
        if hook_id is None:
            # we delete them  all!
            hooked_ids = [h.get('idModel') for h in client.fetch_json('/members/me/tokens?webhooks=true') if h.get('idModel')]
            logging.debug('delete all the hooks!')
            for hook in hooked_ids:
                try:
                    client.fetch_json(
                        '/webhooks/%s' % hook,
                        http_method='DELETE'
                    )
                except Exception as e:
                    logging.debug(str(e))
                    return str(e)
        else:
            logging.debug('delete just one hook')
            try:
                client.fetch_json(
                    '/webhooks/%s' % hook_id,
                    http_method='DELETE'
                )
            except Exception as e:
                logging.error(str(e))
                return str(e)

        hooked_ids = [h.get('idModel') for h in client.fetch_json('/members/me/tokens?webhooks=true') if h.get('idModel')]
        webhooks = Webhook.filter()
        for hook in webhooks:
            if hook.trello_id not in hooked_ids:
                hook.delete()
        return True
    except Exception as e:
        return str(e)


def setup_webhooks(user):
    try:
        client = get_client(user)
        for board in client.list_boards():
            boardid_to_cardmodels(board.id, client)
        p = Process.objects.create()
        p.load_trello_email_card = True
        p.save()
    except Exception as e:
        logging.debug(str(e))