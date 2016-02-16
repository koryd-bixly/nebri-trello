from trello_models import TrelloCard, Webhook, TrelloUserInfo
from instance_settings import INSTANCE_HTTPS_URL
from trello import TrelloClient
import iso8601
import logging

logging.basicConfig(filename='trello_utils.log', level=logging.DEBUG)


def boardid_to_cardmodels(idboard, client=None, user=None):
    # pass a board id to get all the card models created or updated.
    cards = json_cards_from_board(idboard, client)
    members = json_members_from_board(idboard, client)

    for card in cards:
        card_json_to_model(card, user)

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


def card_json_to_model(card, user):
    epoch = '1970-01-01T12:00:00.00+0000'
    pepoch = iso8601.parse_date(epoch)

    logging.info('card list is next: ')
    logging.info(str(card))
    new = False
    # card_obj, new = TrelloCard.get_or_create(idCard=card.get('id'))
    try:
        card_obj = TrelloCard.get(idCard=card.get('id'), user=user)
    except Process.DoesNotExist:
        logging.debug('create new.....')
        card_obj = TrelloCard(idCard=card.get('id'), user=user)
        card_obj.save()
        new = True
    except Exception as e:
        logging.debug(str(e))
        if len(TrelloCard.filter(idCard=card.get('id'))) > 1:
            card_obj = TrelloCard.filter(idCard=card.get('id'), user=user)[-1]
            TrelloCard.filter(idCard=card.get('id'), user=user).delete()
            card_obj.save()

    # update card

    # check webhook json response
    card_obj.idBoard = card.get('idBoard')
    card_obj.idMembers = card.get('idMembers')
    card_obj.idLabels = card.get('idLabels')
    card_obj.idChecklists = card.get('idChecklists')
    card_obj.idList = card.get('idList')
    card_obj.checklists = card.get('checklists')
    card_obj.due = card.get('due')
    card_obj.due_epoch = None
    card_obj.due_datetime = None
    card_obj.name = card.get('name')
    card_obj.shortUrl = card.get('shortUrl')
    card_obj.card_json = card
    card_obj.closed = card.get('closed', False)
    card_obj.is_template = False
    card_obj.template_idBoard = None
    card_obj.template_idList = None
    card_obj.drip = None

    logging.info(str(card_obj.due))

    if card_obj.due is not None or card_obj.due != '':
        try:
            # Timezone was set to UTC in the instance. This will make sure that
            # UTC is always broght in
            duedate = iso8601.parse_date(card_obj.due)
        except Exception as e:
            logging.error('TrelloCard date error: ' + str(e))
        else:
            # card_obj.due_epoch = (duedate - epoch).total_seconds()
            card_obj.due_epoch = int(duedate.strftime('%s'))
            card_obj.due_datetime = duedate

    labels = card.get('labels', [])
    if labels != []:
        for label in labels:
            name = label.get('name')
            if name == 'template checklist':
                card_obj.is_template = True
                card_items = template_checklist_parser(card_obj)
                card_obj.drip = card_items.get('drip')

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


def create_webhook(idboard, client, user):
    board = client.fetch_json('/boards/%s' % idboard)
    hook = {
        'desc': 'Webhook for board %s' %  board.get('name'),
        'callback_url': '%s/api/v1/trello_webhook/callback?user=%s&id=%s' %(INSTANCE_HTTPS_URL, user, idboard),
        'id_model': idboard,
        'type_model': 'board'
    }
    new_hook = Webhook(
        user=user,
        description=hook['desc'],
        callback=hook['callback_url'],
        model_id=hook['id_model'],
        model_type=hook['type_model']
    )
    new_hook.save()
    logging.info(new_hook)
    webhook = client.create_hook(hook['callback_url'], hook['id_model'], desc=hook['desc'])
    logging.info(webhook)
    if webhook is False:
        # an error occurred during webhook creation. let's try manual creation.
        data = {'callbackURL': hook['callback_url'], 'idModel': hook['id_model'],
                'description': hook['desc']}
        webhook = client.fetch_json('/webhooks', http_method='POST', post_args=data)
        logging.info(webhook)
        new_hook.trello_id = webhook['id']
    else:
        new_hook.trello_id = webhook.id
    new_hook.save()


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
    except Exception as e:
        logging.debug('ERROR: %s' %str(e))
        load_card('trello-token-save')
        raise Exception('Token does not exist. Please supply one on the Trello OAuth Token Creation card or run trello_webhook_setup.')
    return ""


def get_client(user):
    token = _get_trello_token(user)
    try:
        return TrelloClient(api_key=shared.TRELLO_API_KEY, api_secret=shared.TRELLO_API_SECRET, token=token)
    except Exception as e:
        logging.debug(str(e))
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
        params = dict(filter='createCard')
    try:
        response = client.fetch_json(
            'cards/{id}/actions'.format(id=idcard),
            query_params=params
        )
    except Exception as e:
        logging.error(str(e))
        creator = None
    else:
        if len(response) == 0:
            return None
        creator = response[-1].get('idMemberCreator')

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
        logging.info('get client')
        client = get_client(user)
        hook_apps = client.fetch_json('/members/me/tokens?webhooks=true')
        nebri_hooks = [hook for hook in hook_apps if hook['identifier'] == 'nebrios'][0]
        logging.info(nebri_hooks)
        hooked_ids = [
            hook.get('idModel') for hook in
            nebri_hooks['webhooks']
            if hook.get('idModel')
            ]
        logging.info(hooked_ids)
        for board in client.list_boards():
            logging.info('handling board %s' % board.id)
            if board.id not in hooked_ids:
                logging.info('create webhook for board')
                create_webhook(board.id, client, user)
            logging.info('begin parsing card info')
            boardid_to_cardmodels(board.id, client, user)
        p = Process.objects.create()
        p.load_trello_email_card = True
        p.save()
    except Exception as e:
        logging.debug(str(e))


def template_checklist_parser(card):
    json_data = card.card_json
    description = json_data.get('desc')
    out_data = None
    now = datetime.now()
    PREBUILT = dict(
        hour=timedelta(hours=1),
        day=timedelta(days=1),
        week=timedelta(weeks=1),
        month=timedelta(days=30),
        quarter=timedelta(weeks=16),
        year=timedelta(days=365)
    )
    if description:
        card_items = {
                k:v for (k, v) in [
                out.split('=') for out in description.split('\n')
                ]}
        due = card_items.get('due', 'day')
        if due.isdigit():
            try:
                intdays = int(due)
            except:
                intdays = 1
            due_next = now + timedelta(days=intdays)
        else:
            due_next = now + PREBUILT.get(card_items.get('due', 'day'))
        out_data = dict(
            description=card_items.get('description', ''),
            board_name=card_items.get('board'),
            list_name=card_items.get('list'),
            drip=card_items.get('drip', None),
            due=card_items.get('due', 'day'),
            due_next=due_next
        )
    return out_data

def template_checklist_setup(card, client):
    card_items = template_checklist_parser(card)
    if card_items is None:
        return card

    if card.template_idList is not None and card.template_idBoard is not None:
        return card
    board_name = card_items.get('board_name')
    list_name = card_items.get('list_name')

    if board_name is not None and list_name is not None:

        all_boards = client.fetch_json('/members/me/boards/',
                                       query_params={'fields': "name, id"})
        board = None
        for b in all_boards:
            if b.get('name') == card_items.get('board_name'):
                board = client.get_board(b.get('id'))
                card.template_idBoard = b.get('id')
                logging.debug('board id: ' + str(board))
                break

        # get correct list.
        if board is not None:
            for blist in board.open_lists():
                if blist.name == list_name:
                    card.template_idList = blist.id
                    break

    if card.template_idBoard is None or card.template_idList is None:
        card.template_idBoard = card.idBoard
        card.template_idList = card.idList

    card.save()

    return card


def copy_template_card(client, card, name=None, card_items=None):
        """Add a card to this list

        :name: name for the card
        :desc: the description of the card
        :labels: a list of label IDs to be added
        :due: due date for the card
        :source: card ID from which to clone from
        :return: the card
        """


        if card_items is None:
            card_items = template_checklist_parser(card)
            if card_items is None:
                return None

        if name is None:
            name = 'Finish By: {}'.format(card_items.get('due_next', ''))

        description = card_items.get('description', '')
        due = str(card_items.get('due_next', ''))
        labels = ''

        board = client.get_board(card.template_idBoard)
        clist = board.get_list(card.template_idList)
        new = clist.add_card(name, desc=description, labels=[],
                            due=due, source=card.idCard)

        new.set_pos('top')

        for label in new.labels:
                if label.name == 'template checklist':
                    new.remove_label(label)
                    break

        return new
