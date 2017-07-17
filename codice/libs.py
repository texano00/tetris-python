import base64
import json

class message(object):
	def __init__(self, data):
		self.data = data

	def encode(self):
		return base64.b64encode(json.dumps(self.data)) + "\n\r"

	def decode(self):
		return json.loads(base64.b64decode(self.data))
