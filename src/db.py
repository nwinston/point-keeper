from collections import Counter
import redis


REPLIES = 'replies'
USERS = 'users'


class DB:
	def __init__(self, db_url):
		self.conn = redis.from_url(db_url, decode_responses=True)

	def add_point(self, user_id):
		points = self.conn.hget(USERS, user_id)
		points = points + 1 if points else 1
		self.conn.hset(USERS, user_id, points)

	def remove_point(self, user_id):
		points = self.conn.hget(USERS, user_id)
		points = points - 1 if points else 0
		self.conn.hset(USERS, user_id, points)

	def get_points(self, user_id=None, n=None):
		if user_id:
			return self.conn.hget(USERS, user_id)

		points = self.conn.hgetall(USERS)
		results = Counter(points)
		return results.most_common(n)

	def get_reply_thread(self, msg_id):
		return self.conn.pipeline().hget(REPLIES, msg_id)

	def add_reply_thread(self, initial_msg_id, reply_id):
		self.conn.hset(REPLIES, initial_msg_id, reply_id)

	@staticmethod
	def create_msg_id(channel, timestamp):
		return '{}:{}'.format(channel, timestamp)
