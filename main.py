from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request as request
import urllib.parse as urlparse
from urllib.parse import urlencode
import webbrowser

import threading
import random
import string
import sys
import pickle

import time
import json

NUM_OF_TRACKS = 200

class Token:
	def __init__(self, token, token_type, expires):
		self.token = token
		self.token_type = token_type
		self.expires = int(time.time()) + int(expires)

	def writeToken(self, file='token.pkl'):
		with open(file, 'wb') as output:
			pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

	def __str__(self):
		return ','.join([self.token_type, str(self.expires)])

	@staticmethod
	def readToken(file='token.pkl'):
		try: 
			with open(file, 'rb') as input:
				token = pickle.load(input)
				if token is not None:
					if int(time.time()) > token.expires:
						print ("Expired token")
						token = getToken()
				return token
		except Exception:
			return None

def getClientId(file='clientid'):
	try:
		with open (file) as f:
			return str(f.read()).strip()
	except Exception:
		print("You have to add a client ID in the file 'clientid' in this folder to get any data from spotify")
		print("Please refer the readme.md")
		sys.exit()

class ReqHandler(BaseHTTPRequestHandler):
	"""docstring for ReqHandler"""
	def do_GET(self):
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()
		
		if not hasattr(self, 'serve_cache'):
			f = open ('serve.html')
			self.serve_cache = bytes(f.read(), 'UTF-8')
			f.close()

		self.wfile.write(self.serve_cache)

def init(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
	server_address = ('', 9399)
	return server_class(server_address, handler_class)

def genRandomString(N=64, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.SystemRandom().choice(chars) for _ in range(N))

def getToken():
	httpd = init(handler_class=ReqHandler)
	thread = threading.Thread(target=httpd.handle_request)
	# thread.daemon = True
	try:
		thread.start()
	except Exception as e:
		print(e)

	CLIENT_ID = getClientId()
	state = genRandomString()
	url = 'https://accounts.spotify.com/authorize'
	params = {
		'client_id': CLIENT_ID,
		'response_type': 'token',
		'redirect_uri': 'http://localhost:9399/callback',
		'scope': 'user-library-read',
		'state': state,
	}

	url_parts = list(urlparse.urlparse(url))
	url_parts[4] = urlencode(params)

	url = urlparse.urlunparse(url_parts)
	print(url)
	print("If this doesn't open in a browser, copy this url and open in browser")
	print("After loading...")
	print("Click the Token button to copy the token")
	print("And paste it here")
	webbrowser.open_new(url)

	query = urlparse.urlparse(input()).fragment
	params = urlparse.parse_qs(query)

	token = Token(token=params['access_token'][0],
               token_type=params['token_type'][0],
               expires=params['expires_in'][0])

	_state = params['state'][0]

	token.writeToken()

	if _state != state:
		print(sys.stderr, "Invalid token")
		sys.exit()

	thread.join()
	return token

if __name__ == '__main__':
	TRACK_NUM = int(NUM_OF_TRACKS/50)
	token = Token.readToken()
	if token is None: 
		token = getToken()

	print("Final Token:")
	print (token)

	new_url = 'https://api.spotify.com/v1/me/tracks?offset=0&limit=50'

	items = []
	for _ in range(TRACK_NUM):
		req = request.Request(url=new_url)
		req.add_header('Authorization', token.token_type + ' ' + token.token)

		with request.urlopen(req) as f:
			resp = f.read().decode('utf-8')
			resp = json.loads(resp)
		new_url = resp['next']
		items.extend(resp['items']) 

	with open('all_data.json', 'w') as g:
		json.dump(items, g)


	# print(resp)

