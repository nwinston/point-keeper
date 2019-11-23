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


THUMBS_UP = '+1'

def post_points(channel, user=None, n=None):
    points = db.get_points(user, n)
    bot.post_points_table(points, channel, user, n)


@event_adapter.on('reaction_added')
def on_reaction_added(payload):
    event = payload['event']
    reaction = event['reaction']

    print('reaction added: {}'.format(reaction))
    if reaction != THUMBS_UP:
        return

    reactee_id = event['item_user']
    db.add_point(reactee_id)

    channel = event['item']['channel']
    timestamp = event['item']['ts']
    msg_id = DB.create_msg_id(channel, timestamp)

    reply_thread = db.get_reply_thread(msg_id)
    print('reply_thread 1: {}'.format(reply_thread))
    if not reply_thread:
        reply = bot.post_point_recorded_message(channel)
        reply_ts = reply['ts']
        reply_thread = DB.create_msg_id(channel, reply_ts)
        db.add_reply_thread(msg_id, reply_thread)
        return

    channel, reply_ts = DB.split_msg_id(reply_thread)
    bot.post_point_recorded_message(channel, reply_ts)


@event_adapter.on('reaction_removed')
def on_reaction_removed(payload):
    event = payload['event']
    if event['reaction'] != THUMBS_UP:
        return

    reactee_id = event['item_user']
    db.remove_point(reactee_id)


@event_adapter.on('message')
def on_message(payload):
    print('on message')


def monthly_update():
    date = datetime.date.today()
    hour = (int(datetime.datetime.utcnow().strftime("%H")) - 5) % 24  # hardcoding to EST
    day = date.day
    print('day: {}; hour: {}'.format(day, hour))
    if day == 23 and (hour == 11 or hour == 12):
        post_points('general')


if __name__ == '__main__':
    timer = Timer(monthly_update, 60)
    timer.start()

    port = os.environ.get('PORT', 3000)
    event_adapter.start(host='0.0.0.0', port=port)
