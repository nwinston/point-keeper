from collections import Counter
import redis


class DB:
	def __init__(self, db_url):
		self.conn = redis.from_url(db_url)

	def add_point(self, user):
		points = self.conn.get(user)
		points = points + 1 if points else 1
		print('post points: {}'.format(points))
		self.conn.set(user, points)

	def remove_point(self, user):
		points = self.conn.get(user)
		points = points - 1 if points else 0
		self.conn.set(user, points)

	def get_points(self, user=None, n=None):
		if user:
			return self.conn.get(user)

		keys = self.conn.scan(match='*')[1]
		if not keys:
			return {}

		results = Counter({key: self.conn.get(key) for key in keys})
		return results.most_common(n)
