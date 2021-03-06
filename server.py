import rethinkdb as r
from twisted.internet.defer import succeed
from twisted.web.static import File
from klein import run, route

from conf import (
    HOST,
    PORT
)

c = r.connect(host=HOST, port=PORT)


def get_template(messages):
    with open('chat.html') as html:
        data = html.read().replace('\n', '').strip()
    return data % messages


def format_message(row):
    return '<p>%s <b>%s</b>: %s</p>' % (
        row.get('time').strftime('%H:%M:%S'),
        row.get('user'),
        row.get('message')
    )


def get_all_messages():
    messages = r.db('chat').table('log').order_by(index=r.asc('time')).run(c)
    return [format_message(m) for m in messages]


def send_message(user, message):
    return r.db('chat').table('log').insert(
        [{'user': user, 'message': message, 'time': r.now()}]
    ).run(c)


# Routes:
@route('/static/', branch=True)
def static(request):
    return File("./static")


@route('/', methods=['POST'])
def get_post_data(request):
    user = request.args.get('username')[0]
    message = request.args.get('message')[0]
    if user and message:
        print '%s: %s' % (user, message)
        send_message(user, message)
    request.redirect('/')
    return succeed(None)


@route('/')
def chat(request):
    return get_template('\n'.join(get_all_messages()))

run("localhost", 8000)
