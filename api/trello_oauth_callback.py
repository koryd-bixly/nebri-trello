import logging

logging.basicConfig(filename='oauth_token.log', level=logging.DEBUG)

def oauth_token(request):
    logging.debug(str(request.FORM))
    if request.FORM:
        user = request.user
        try:
            p = Process.objects.get(user=request.user, kind="trello_oauth_token")
            p.token = request.FORM.trello_token
            p.save()
        except:
            p = Process.objects.create()
            p.user=request.user
            p.kind="trello_oauth_token"
            p.token=request.FORM.trello_token
            p.trello_watch_boards_for_user = True
            p.save()