from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse
from urllib.parse import urlencode
import webbrowser

import threading

CLIENT_ID = '02d91716c7f5406faa8dae38f7945112' # My client id

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

if __name__ == '__main__':
	httpd = init (handler_class = ReqHandler)
	thread = threading.Thread(target = httpd.handle_request)
	# thread.daemon = True
	try:
		thread.start()
	except Exception as e:
		print(e)

	url = 'https://accounts.spotify.com/authorize'
	params = {
		'client_id': CLIENT_ID,
		'response_type': 'token',
		'redirect_uri': 'http://localhost:9399/callback',
		'scope': 'user-library-read',
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

	token = params['access_token'][0]
	token_type = params['token_type'][0]
	expires = params['expires_in'][0]

	print("Final Token:")
	print (token)

	new_url = 'https://api.spotify.com/v1/me/tracks'

	thread.join()