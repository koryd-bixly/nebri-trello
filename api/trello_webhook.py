import pytz
import traceback
import json
from trello import TrelloClient

from trello_models import Webhook, TrelloUserInfo, TrelloCard
from trello_utils import card_json_to_model, setup_webhooks, get_client, get_card_creator

import logging
logging.basicConfig(filename='lololololololol.log', level=logging.DEBUG)


# logging.basicConfig(filename='trello_webhook_module.log', level=logging.DEBUG)

ACTIONS_FOR_CACHING = ['addAttachmentToCard', 'addChecklistToCard', 'addLabelToCard', 'convertToCardFromCheckItem',
                       'createCard', 'createCheckItem', 'deleteAttachmentFromCard', 'deleteCheckItem',
                       'removeChecklistFromCard', 'removeLabelFromCard', 'updateCard', 'updateCheckItemStateOnCard',
                       'updateChecklist', 'deleteCard']
DONE_LIST_NAME = "Done"


def oauth_token(request):
    logging.debug('oauth_token start')
    try:
        if request.FORM:
            user = request.user
            logging.debug('wat')
            try:
                logging.debug('try')
                p = Process.objects.get(user=request.user, kind="trello_oauth_token")
                p.token = request.FORM.trello_token
                p.trello_watch_boards_for_user = True
                p.save()
                logging.debug('saved')
            except:
                logging.debug('except')
                p = Process.objects.create()
                p.user = request.user
                p.kind = "trello_oauth_token"
                p.token = request.FORM.trello_token
                p.trello_watch_boards_for_user = True
                p.save()
                logging.debug('saved except')
    except Exception as e:
        logging.debug(str(e))
    return '200 OK'
    
    
def setup(request):
    try:
        if request.FORM:
            user = request.user
            shared.TRELLO_API_KEY = request.FORM.trello_api_key
            shared.TRELLO_API_SECRET = request.FORM.trello_api_secret
            shared.DEFAULT_USER = request.FORM.default_user
            p = Process.objects.create()
            p.trello_webhook_setup = True
            p.last_actor = request.FORM.default_user
            p.save()
    except Exception as e:
        logging.debug(str(e))
    return '200 OK'


def callback(request):
    logging.debug('webhook received!')
    logging.debug('what in the world')
    try:
        webhook = Webhook.get(model_id=request.GET['id'])
    except Exception as e:
        logging.info('ERROR: %s' % (str(e)))
    user = request.GET['user']
    client = get_client(user)
    logging.debug(client)
    comment_data = None
    card_json = None
    if request.BODY == '':
        # this is a test webhook for setup. return ok.
        return '200 OK'
    if 'card' in request.BODY['action']['data']:
        logging.debug('update or create card!')
        card_json = client.fetch_json('cards/%s?checklists=all&' % request.BODY['action']['data']['card']['id'])
        try:
            card, new = card_json_to_model(card_json, user)
            logging.debug(card.creator)
            logging.info('Card creator: {}'.format(card.creator))
            if card.creator is None or card.creator is False:
                card_creator, date_str = get_card_creator(card.idCard, client)
                creator = TrelloUserInfo(trello_id=card_creator)
                card.creator = creator
                card.created = date_str
                card.save()
            logging.info('Card creator after call: {}'.format(card.creator))
        except Exception as e:
            logging.error('callback error: {}'.format(str(e)))
            logging.debug(str(e))
        comment_data = client.fetch_json('cards/%s?actions=commentCard' % request.BODY['action']['data']['card']['id'])
        logging.debug(comment_data)
        board_admins = [admin.get('username') for admin in client.fetch_json('boards/%s/members/admins' % request.BODY['action']['data']['board']['id']) if admin.get('username')]
        logging.debug(board_admins)
        p = Process.objects.create()
        p.hook_data = request.BODY
        p.card_data = card_json
        p.comment_data = comment_data
        p.board_admins = board_admins
        p.handle_trello_webhook = True
        p.default_user = user
        p.save()
        logging.debug(p)
    return '200 OK'
    
    
def update_users(request):
    try:
        users_to_update = request.FORM.users_to_update
        for user in users_to_update:
            member = TrelloUserInfo.get(trello_id=user['id'])
            member.email = user['email']
            member.save()
    except Exception as e:
        logging.error(str(e))
    return '200 OK'
