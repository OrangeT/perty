#!/usr/bin/env python3

# https://www.learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/

# We're going to need to do full client authentication.

from config import load_config
from twitch_auth import oauth
import display
import socketserver
import time
import emoji
import regex

def split_count(text):

    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
            emoji_list.append(word)
    
    return emoji_list

cfg = load_config()
token = oauth() # Get user token

import socket
sock = socket.socket()
 
sock.connect((cfg['twitch']['server'], cfg['twitch']['port']))
 
sock.send(f"PASS oauth:{token}\n".encode('utf-8'))
sock.send(f"NICK {cfg['twitch']['name']}\n".encode('utf-8'))
sock.send(f"JOIN {cfg['twitch']['channel']}\n".encode('utf-8'))

cur_emoji = "😊"

while True:
    resp = sock.recv(2048).decode('utf-8')
    print (resp) # Just print whatever we get
    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))
 
    if "/NAMES" in resp:
        sock.send("PRIVMSG #betsyandsamantha :PERTY CONNECTED\n".encode('utf-8'))

    if resp:
        emojis = split_count(resp)
        if any(emojis):
            cur_emoji = emojis[-1]

    display.display_emoji(cur_emoji)
    time.sleep(1)
