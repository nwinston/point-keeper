from __future__ import absolute_import

from functools import partial
from celery import Celery
from bot import Bot
from db import DB

import os

app = Celery('tasks', broker=os.environ.get(
	'REDIS_URL', 'redis://h:pdb6d8dec288332837a6f7a3d9b3b3cde548d676d2576cc2f1477a1da70a598fd@ec2-3-233-76-9.compute-1.amazonaws.com:12089')
)

bot_token = os.environ.get('BOT_TOKEN')
bot = Bot(bot_token)


@app.task
def point_added(user, channel):
	bot.post_point_added_message(channel)

@app.task
def post_points(points, channel, user=None, n=None):	
	bot.post_points_table(points, channel, user, n)


if __name__ == '__main__':
	app.start()