# Twitch OAuth Handling

from config import load_config
import yaml
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

    print(f'Please open your browser at {redirect_uri}')

    # Keep listening until we handle a post request
    while HandleRequests.keep_running:
         httpd.handle_request()

def read_code():
    global access_token
    global refresh_token

    if exists("code.yml"):
        print("Reading Twitch tokens")
        with open("code.yml", "r") as ymlfile:
            code = yaml.safe_load(ymlfile)
            access_token = code['access_token']
            refresh_token = code['refresh_token']
            return True

    return False

def write_code():
    global access_token
    global refresh_token


    with open("code.yml", "w") as ymlfile:
        print("Writing Twitch tokens")
        yaml.dump({
            'access_token': access_token,
            'refresh_token': refresh_token
        }, ymlfile)

def validate():

    print("Validating Twitch tokens...", end='')
    url = 'https://id.twitch.tv/oauth2/validate'
    r = requests.get(url, headers={'Authorization': f'Oauth {access_token}'})
    if r.status_code == 200:
        print("valid")
        return True
    elif r.status_code == 401:
        print("invalid")
        return False
    else:
        raise Exception(f'Unrecognised status code on validate {r.status_code}')

def get_tokens():
    print("Fetching Twitch tokens")
    global access_token
    global refresh_token

    url = 'https://id.twitch.tv/oauth2/token'
    request_payload = {
        "client_id": cfg['twitch']['client_id'],
        "client_secret": cfg['twitch']['client_secret'],
        'redirect_uri': redirect_uri
    }
    if code:
        request_payload['grant_type'] = 'authorization_code'
        request_payload['code'] = code
    if refresh_token:
        request_payload['grant_type'] = 'refresh_token'
        request_payload['refresh_token'] = refresh_token

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
    if read_code(): # Code exists
        if not validate():
            get_tokens()
    else:
        auth_code_flow() # User login auth
        get_tokens()
    write_code()

    return access_token
