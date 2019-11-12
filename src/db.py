'''
import os
import pickle
import shutil
import tempfile
from collections import Counter
from threading import Lock
'''
from collections import Counter
import redis


class DB:
	def __init__(self, db_url):
		self.conn = redis.from_url(db_url)
		self.conn.flushdb()

	def add_point(self, user):
		points = self.conn.get(user)
		points = points + 1 if points else 1
		self.conn.set(user, points)

	def remove_point(self, user):
		points = self.conn.get(user)
		if not points:
			self.conn.set(user, 0)
		else:
			self.conn.set(user, points - 1)

	def get_points(self, user=None, n=None):
		if user:
			return self.conn.get(user)

		keys = self.conn.scan(match='*')[1]
		if not keys:
			return {}

		results = Counter({key: self.conn.get(key) for key in keys})
		return results.most_common(n)




'''
class DB:
	def __init__(self, db_file):
		self.counter = Counter()
		self.db_file = db_file
		self.lock = Lock()

		if os.path.exists(self.db_file):
			self._load(self.db_file)

	def lock_db(f):
		def wrapper(self, *args, **kwargs):
			rv = None
			with self.lock:
				rv = f(self, *args, **kwargs)
			return rv
		return wrapper

	@lock_db
	def _load(self, database):
		with open(self.db_file, 'rb') as db:
			self.counter = pickle.load(db)

	@lock_db
	def save(self):
		if not os.path.exists(self.db_file):
			with open(self.db_file, 'wb') as f:
				pickle.dump(self.counter, f)
			return

		with tempfile.NamedTemporaryFile('wb') as temp:
			shutil.copyfile(self.db_file, temp.name)

			with open(self.db_file, 'wb') as f:
				try:
					pickle.dump(self.counter, f)
				except:
					shutil.copyfile(temp.name, self.db_file)

	def add_point(self, user):
		self.counter[user] += 1

	def remove_point(self, user):
		if self.counter[user] >= 1:
			self.counter[user] -= 1

	def get_points(self, user=None, n=None):
		if user:
			return self.counter[user]

		return self.counter.most_common(n)
'''