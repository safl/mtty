#!/usr/bin/env python
import inspect
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask import send_from_directory
import glob
import os

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def background_thread():
    """Example of how to send server generated events to clients."""

    count = 0
    while True:
        socketio.sleep(10)
        count += 1

        payload = {
            'data': 'Server generated event',
            'count': count
        }
        socketio.emit('my_response', payload, namespace='/mtty')

@app.route('/')
def index():
    "Serve the client-side application."""

    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/logs', defaults={"path": None})
@app.route('/logs/', defaults={"path": None})
@app.route('/logs/<path:path>')
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

@socketio.on('my_event', namespace='/mtty')
def mtty_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    emit('my_response', payload)

@socketio.on('my_broadcast_event', namespace='/mtty')
def mtty_broadcast_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    emit('my_response', payload, broadcast=True)

@socketio.on('connect', namespace='/mtty')
def mtty_connect():
    global thread
    print(inspect.currentframe().f_code.co_name)
    
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    payload = {
        'data': 'Connected',
        'count': 0
    }
    emit('my_response', payload)

@socketio.on('disconnect', namespace='/mtty')
def mtty_disconnect():
    print(inspect.currentframe().f_code.co_name)
    
    print('Client disconnected', request.sid)

@socketio.on('join', namespace='/mtty')
def join(message):
    print(inspect.currentframe().f_code.co_name)
    
    join_room(message['room'])
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': 'In rooms: ' + ', '.join(rooms()),
        'count': session['receive_count']
    }
    emit('my_response', payload)

@socketio.on('leave', namespace='/mtty')
def leave(message):
    print(inspect.currentframe().f_code.co_name)
    
    leave_room(message['room'])
    
    session['receive_count'] = session.get('receive_count', 0) + 1
   
    payload = {
        'data': 'In rooms: ' + ', '.join(rooms()),
        'count': session['receive_count']
    }
    emit('my_response', payload)

@socketio.on('close_room', namespace='/mtty')
def close(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': 'Room ' + message['room'] + ' is closing.',
        'count': session['receive_count']
    }
    emit('my_response', payload, room=message['room'])
    
    close_room(message['room'])

@socketio.on('my_room_event', namespace='/mtty')
def send_room_message(message):
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1
    
    payload = {
        'data': message['data'],
        'count': session['receive_count']
    }
    emit('my_response', payload, room=message['room'])

@socketio.on('disconnect_request', namespace='/mtty')
def disconnect_request():
    print(inspect.currentframe().f_code.co_name)
    
    session['receive_count'] = session.get('receive_count', 0) + 1

    payload = {
        'data': 'Disconnected!',
        'count': session['receive_count']
    }
    emit('my_response', payload)
    
    disconnect()

@socketio.on('ping', namespace='/mtty')
def ping_pong():
    print(inspect.currentframe().f_code.co_name)
    
    emit('pong')

if __name__ == '__main__':
    socketio.run(app, debug=True)
