# Twitch OAuth Handling

from config import load_config
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import ssl
import requests
from os.path import exists

code = None
access_token = None
refresh_token = None

cfg = load_config()
redirect_uri = f'https://{cfg["server"]["host"]}:{cfg["server"]["port"]}/'

class HandleRequests(BaseHTTPRequestHandler):

    keep_running = True

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global code

        self._set_headers()

        path = urlparse(self.path)
        # print(f"Incoming request {path}")

        if not path.query:
            request_payload = { 
                    "client_id": cfg['twitch']['client_id'],
                    "force_verify": 'false',
                    "redirect_uri": redirect_uri,
                    "response_type": 'code',
                    "scope": 'chat:edit chat:read'
                    }
            encoded_payload = urlencode(request_payload)
            url = 'https://id.twitch.tv/oauth2/authorize?' + encoded_payload
            self.wfile.write(f'<html><head><body><a href="{url}">Click here to auth with Twitch</a></body></head>'.encode('utf-8'))
        else:
            code = parse_qs(path.query)['code'][0]
            print(f'Code: {code}')
            HandleRequests.keep_running = False

# Authorisation Code Flow
# Launch HTTP Server, listen for request, direct user to Twitch,
# listen for response.
def auth_code_flow():

    httpd = HTTPServer((cfg['server']['host'], cfg['server']['port']), HandleRequests)
    httpd.socket = ssl.wrap_socket (httpd.socket, 
        keyfile="key.pem", 
        certfile='cert.pem', server_side=True)

    # Keep listening until we handle a post request
    while HandleRequests.keep_running:
         httpd.handle_request()

def read_code():
    global code
    if exists("code.txt"):
        with open("code.txt", "r") as f:
            code = f.read()

def write_code(code):
    with open("code.txt", "w") as f:
            f.write(code)
            f.close()

def get_code():
    if not code:
        auth_code_flow()

def get_tokens():
    global access_token
    global refresh_token

    url = 'https://id.twitch.tv/oauth2/token'
    request_payload = {
        "client_id": cfg['twitch']['client_id'],
        "client_secret": cfg['twitch']['client_secret'],
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }

    r = requests.post(url, data=request_payload).json()
    try:
        access_token = r['access_token']
        refresh_token = r['refresh_token']
        print(f'Access token: {access_token}')
        print(f'Refresh token: {refresh_token}')
    except:
        print("Unexpected response on redeeming auth code:")
        print(r)

def oauth():
    # read_code()
    get_code()
    # write_code(code)
    get_tokens()
    return access_token
