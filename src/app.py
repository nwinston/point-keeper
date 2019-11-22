import os
import re
import sched
import datetime
import threading

from slackeventsapi import SlackEventAdapter
from db import DB
from bot import Bot
from timer import Timer

point_regex = re.compile('\+1\s*<@([A-Z0-9]*)>$')

secret = os.environ.get('SLACK_SIGNING_SECRET', default=None)
event_adapter = SlackEventAdapter(secret, endpoint='/slack/events')

db_url = os.environ.get('REDIS_STORE_URL', default="redis://")
db = DB(db_url)

bot_token = os.environ.get('BOT_TOKEN')
bot = Bot(bot_token)


def post_points(channel, user=None, n=None):
    points = db.get_points(user, n)
    bot.post_points_table(points, channel, user, n)


@event_adapter.on('reaction_added')
def on_message(payload):
    print('reaction added')

    event = payload['event']
    if event['name'] != 'thumbsup':
        return

    reactee_id = event['item_user']

    channel = event['item']['channel']
    timestamp = event['item']['ts']
    msg_id = DB.create_msg_id(channel, timestamp)

    db.add_point(reactee_id)

    reply_thread = db.get_reply_thread(msg_id)
    if not reply_thread:
        reply = bot.post_point_recorded_message(channel)
        reply_ts = reply['event']['ts']
        reply_thread = DB.create_msg_id(channel, reply_ts)

    db.add_reply_thread(msg_id, reply_thread)


def monthly_update():
    date = datetime.date.today()
    hour = (int(datetime.datetime.utcnow().strftime("%H")) - 5) % 24  # hardcoding to EST
    day = date.day
    print('day: {}; hour: {}'.format(day, hour))
    if day == 21 and hour == 20:
        post_points('general')


if __name__ == '__main__':
    port = os.environ.get('PORT', 3000)


    def start():
        event_adapter.start(host='0.0.0.0', port=port)


    threading.Thread(target=start).start()

    timer = Timer(monthly_update, 60 * 60 * 30.5)
    timer.start()
