from __future__ import absolute_import

from celery import Celery
from bot import Bot

import os


broker_url = os.environ['REDIS_BROKER_URL']
app = Celery('tasks', broker=broker_url
)

bot_token = os.environ.get('BOT_TOKEN')
bot = Bot(bot_token)


@app.task
def point_added(channel):
	bot.post_point_added_message(channel)


@app.task
def post_points(points, channel, user=None, n=None):	
	bot.post_points_table(points, channel, user, n)


if __name__ == '__main__':
	app.start()