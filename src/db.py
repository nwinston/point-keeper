from collections import Counter
import redis


REPLIES = 'replies'
USERS = 'users'


class DB:
	def __init__(self, db_url):
		self.conn = redis.from_url(db_url, decode_responses=True)

	def add_point(self, user_id):
		points = self.conn.hget(USERS, user_id)
		if not points:
			points = 0
		points += 1
  
		self.conn.hset(USERS, user_id, points)

	def remove_point(self, user_id):
		points = self.conn.hget(USERS, user_id)
		if not points:
			points = 0

		points = max(points - 1, 0)
		self.conn.hset(USERS, user_id, points)

	def get_points(self, user_id=None, n=None):
		if user_id:
			return self.conn.hget(USERS, user_id)

		points = self.conn.hgetall(USERS)
		results = Counter(points)
		return results.most_common(n)

	def get_reply_thread(self, msg_id):
		print('fetching reply thread: {}'.format(msg_id))
		print(self.conn.hgetall(REPLIES))
		return self.conn.hget(REPLIES, msg_id)

	def add_reply_thread(self, initial_msg_id, reply_id):
		print('adding reply thread: {}'.format(initial_msg_id, reply_id))
		self.conn.hset(REPLIES, initial_msg_id, reply_id)

		print(self.conn.hgetall(REPLIES))
  
	def clear(self):
		self.conn.flushdb()

	@staticmethod
	def create_msg_id(channel, timestamp):
		return '{}:{}'.format(channel, timestamp)

	@staticmethod
	def split_msg_id(msg_id):
		return tuple(msg_id.split(':'))
