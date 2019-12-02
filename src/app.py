import os
import re
import sched
import datetime
from dateutil.relativedelta import relativedelta
import threading

from slackeventsapi import SlackEventAdapter
from db import DB
from bot import Bot
from timer import Timer

secret = os.environ.get('SLACK_SIGNING_SECRET', default=None)
event_adapter = SlackEventAdapter(secret, endpoint='/slack/events')

db_url = os.environ.get('REDIS_STORE_URL', default="redis://")
db = DB(db_url)

bot_token = os.environ.get('BOT_TOKEN')
bot = Bot(bot_token)

update_day = int(os.environ.get('UPDATE_DAY', 1))
update_hour = int(os.environ.get('UPDATE_HOUR', 9))

print('Posting points at day {} hour {}'.format(update_day, update_hour))

THUMBS_UP = '+1'

def post_points(channel, user=None, n=None):
    points = db.get_points(user, n)
    print('Posting points table:\n {}'.format(points))
    
    if not points:
        return
    
    last_month = datetime.date.today() - relativedelta(months=1)
    date_str = format(last_month, '%B %Y')
    message = 'Point totals for {}:\n'.format(date_str)
    message += '\n'.join([f'<@{r[0]}>: {r[1]}' for r in points])
    
    bot.post_message(channel, message)


@event_adapter.on('reaction_added')
def on_reaction_added(payload):
    event = payload['event']
    reaction = event['reaction']

    print('reaction added: {}'.format(reaction))
    if THUMBS_UP not in reaction: # handle different skin tone +1's
        return

    reactee_id = event['item_user']
    db.add_point(reactee_id)
    
    if not os.environ.get('SEND_MESSAGE', False):
        return
    
    channel = event['item']['channel']
    timestamp = event['item']['ts']
    msg_id = DB.create_msg_id(channel, timestamp)

    reply_thread = db.get_reply_thread(msg_id)
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
    if THUMBS_UP not in event['reaction']:
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
    print('update, day {} hour {}'.format(day, hour))
    if day == update_day and hour == update_hour:
        post_points('general')
        db.clear()


if __name__ == '__main__':
    update_check_interval = int(os.environ.get('UPDATE_CHECK_INTERVAL', 60 * 60))
    timer = Timer(monthly_update, update_check_interval)
    timer.start()

    port = os.environ.get('PORT', 3000)
    event_adapter.start(host='0.0.0.0', port=port)
