import os
import functools
import re

from slackeventsapi import SlackEventAdapter

import tasks
from timer import Timer
from db import DB

point_regex = re.compile('\+1\s*<@([A-Z0-9]*)>$')

db_file = os.environ.get('DATABASE_FILE', 'points.pickle')
db = DB(db_file)

secret = os.environ['SLACK_SIGNING_SECRET']
event_adapter = SlackEventAdapter(secret, endpoint='/slack/events')


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
	tasks.point_added.delay(user, channel)


@event_adapter.on('message')
def on_message(event):
	message = event['event']

	if message.get('subtype'):
		return

	text = message.get('text')
	channel = message.get('channel')

	handle_message(text, channel)


if __name__ == '__main__':
	port = os.environ.get('PORT', 3000)
	event_adapter.start(host='0.0.0.0', port=port)

	db_interval = os.environ.get('DB_WRITE_INTERVAL', 500)
	timer = Timer(db.save, db_interval)
	timer.start()