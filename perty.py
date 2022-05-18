# https://www.learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/

# We're going to need to do full client authentication.

from config import load_config
from twitch_auth import oauth
import socketserver

cfg = load_config()
token = oauth() # Get user token

import socket
sock = socket.socket()
 
sock.connect((cfg['twitch']['server'], cfg['twitch']['port']))
 
sock.send(f"PASS oauth:{token}\n".encode('utf-8'))
sock.send(f"NICK {cfg['twitch']['name']}\n".encode('utf-8'))
sock.send(f"JOIN {cfg['twitch']['channel']}\n".encode('utf-8'))
 
while True:
    resp = sock.recv(2048).decode('utf-8')
    print (resp) # Just print whatever we get
    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))
 
    if "/NAMES" in resp:
        sock.send("PRIVMSG #betsyandsamantha :PERTY CONNECTED\n".encode('utf-8'))
 
