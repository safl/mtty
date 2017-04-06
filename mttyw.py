#!/usr/bin/env python
import inspect
from flask import Flask, render_template, session, request
from flask import send_from_directory
import flask_socketio as fsio
import glob
import os

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
ASYNC_MODE = None

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SIO = fsio.SocketIO(APP, async_mode=ASYNC_MODE)
THREAD = None

def background_thread():
    """Example of how to send server generated events to clients."""

    count = 0
    while True:
        SIO.sleep(10)
        count += 1

        payload = {
            'data': 'Server generated event',
            'count': count
        }
        SIO.emit('my_response', payload, namespace='/mtty')

@APP.route('/')
def index():
    "Serve the client-side application."""

    return render_template('index.html', async_mode=SIO.async_mode)

@APP.route('/logs', defaults={"path": None})
@APP.route('/logs/', defaults={"path": None})
@APP.route('/logs/<path:path>')
def logs(path):
    """Serve the log files in their raw form"""

    logs_root = os.sep.join(["", "tmp"])

    html_entry = '<a href="%s">%s</a><br />\n'

    if path is None:
	files = glob.glob(os.sep.join([logs_root, "*"]))
	pfiles = (os.path.basename(fname) for fname in files)
	markup = (html_entry % (fname, fname) for fname in pfiles)
	
	return "".join(list(markup))

    if os.path.exists(path):
	return "DOES NOT EXIST"

    return send_from_directory(logs_root, os.path.basename(path))

@SIO.on('my_event', namespace='/mtty')
def mtty_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload)

@SIO.on('my_broadcast_event', namespace='/mtty')
def mtty_broadcast_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload, broadcast=True)

@SIO.on('connect', namespace='/mtty')
def mtty_connect():
    global THREAD
    print(inspect.currentframe().f_code.co_name)
    
    if THREAD is None:
        THREAD = SIO.start_background_task(target=background_thread)
    payload = {
        'data': 'Connected',
        'count': 0
    }
    fsio.emit('my_response', payload)

@SIO.on('disconnect', namespace='/mtty')
def mtty_disconnect():
    print(inspect.currentframe().f_code.co_name)
    
    print('Client disconnected', request.sid)

@SIO.on('join_room', namespace='/mtty')
def join_room(message):
    print(inspect.currentframe().f_code.co_name)
    
    fsio.join_room(message['room'])
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': 'In rooms: ' + ', '.join(fsio.rooms()),
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload)

@SIO.on('leave_room', namespace='/mtty')
def leave_room(message):
    print(inspect.currentframe().f_code.co_name)
    
    fsio.leave_room(message['room'])
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': 'In rooms: ' + ', '.join(fsio.rooms()),
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload)

@SIO.on('close_room', namespace='/mtty')
def close_room(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': 'Room ' + message['room'] + ' is closing.',
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload, room=message['room'])
    
    fsio.close_room(message['room'])

@SIO.on('my_room_event', namespace='/mtty')
def send_room_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload, room=message['room'])

@SIO.on('disconnect_request', namespace='/mtty')
def disconnect_request():
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1

    payload = {
        'data': 'Disconnected!',
        'count': session['receive_count']
    }
    fsio.emit('my_response', payload)
    
    fsio.disconnect()

@SIO.on('ping', namespace='/mtty')
def ping_pong():
    print(inspect.currentframe().f_code.co_name)
    
    fsio.emit('pong')

if __name__ == '__main__':
    SIO.run(APP, debug=True)
