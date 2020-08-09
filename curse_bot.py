import base64
import json

import socketio
from flask import Flask, abort, request, jsonify, g, url_for, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit, send, leave_room, ConnectionRefusedError
import requests

# initialization
token = ""
discussion_id = "5f304643817db13f7309317c"
sio = socketio.Client()
curse_set = {"fuck", "shit", "asshole", "nigga"}


def login():
    global token
    username = "CurseBot"
    password = "Q1w2e3r4"
    url = 'http://localhost:5000/api/login'
    auth_string = username + ":" + password
    bytes_auth_string = auth_string.encode("utf-8")
    btoa = base64.b64encode(bytes_auth_string)
    auth_headers = {'Authorization': "Basic " + str(btoa, "utf-8")}
    res = requests.get(url, headers=auth_headers)
    res_data_string = res.content.decode('utf-8')
    data = json.loads(res_data_string)
    token = data['token']
    print(token)


def join():
    data = {
        'discussion_id': discussion_id,
        'token': token
    }
    sio.emit('join', data=data)


@sio.on('join room')
def join_room(data):
    print('joined room')


@sio.event
def message(comment_data):
    comment = comment_data['comment']
    print(comment)
    for word in curse_set:
        if word in comment['text']:
            alert_comment = {
                'discussionId': discussion_id,
                'author': 'CurseBot',
                'text': 'Stop Cursing!',
                'parentId': comment['id'],
                'depth': comment['depth'],
                'extra_data': {
                    'recipients_type': 'all',
                    'users_list': []
                }
            }
            sio.emit('add alert', json.dumps(alert_comment))

if __name__ == '__main__':
    # app.debug = True
    login()
    sio.connect('http://localhost:5000')
    join()
