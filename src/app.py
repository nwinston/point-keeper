import os
import re
import sched
import datetime
import threading

from slackeventsapi import SlackEventAdapter

import tasks
from db import DB
from timer import Timer

point_regex = re.compile('\+1\s*<@([A-Z0-9]*)>$')

secret = os.environ.get('SLACK_SIGNING_SECRET', default=None)
event_adapter = SlackEventAdapter(secret, endpoint='/slack/events')

db_url = os.environ.get('REDIS_STORE_URL', default="redis://")
db = DB(db_url)


def submit_post_points(channel, user=None, n=None):
	points = db.get_points(user, n)
	tasks.post_points.delay(points, channel, user, n)


def handle_message(text, channel):
	if text == 'points':
		submit_post_points(channel)
		return

	match = point_regex.match(text)
	if not match:
		return

	user = match.group(1)
	db.add_point(user)
	tasks.point_recorded.delay(channel)


@event_adapter.on('message')
def on_message(event):
	message = event['event']

	if message.get('subtype'):
		return

	text = str(message.get('text'))
	channel = message.get('channel')

	handle_message(text, channel)


def monthly_update():
	date = datetime.date.today()
	hour = (int(datetime.datetime.utcnow().strftime("%H")) - 5) % 24 #hardcoding to east coast
	day = date.day
	print('day: {}; hour: {}'.format(day, hour))
	if day == 21 and hour == 20:
		submit_post_points('general')


if __name__ == '__main__':
	port = os.environ.get('PORT', 3000)

	def start():
		event_adapter.start(host='0.0.0.0', port=port)
	threading.Thread(target=start).start()

	timer = Timer(monthly_update, 60 * 60 * 30.5)
	timer.start()
