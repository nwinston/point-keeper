import slack

class Bot:
	def __init__(self, api_token):
		self.client = slack.WebClient(api_token)

	def post_point_recorded_message(self, channel):
		self.client.chat_postMessage(
			channel=channel, 
			text='Point recorded in database'
		)

	def post_points_table(self, points, channel, user=None, n=None):
		if points:
			pretty_str = '\n'.join([f'<@{r[0]}>: {r[1]}' for r in points])
		else:
			pretty_str = 'Points database empty'

		self.client.chat_postMessage(
			channel=channel,
			text=pretty_str
		)