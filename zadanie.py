from threading import Lock
from flask import Flask, render_template, session, request, jsonify,url_for
from flask_socketio import SocketIO, emit, disconnect
import time
import random
import json
import serial
import numpy as np
import matplotlib.pyplot as plt

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
btn = ""

ser = serial.Serial("/dev/ttyS0")
ser.baudrate = 9600

# i =-1
# while i <10:
#     read_ser = ser.readline()
#     print(read_ser.decode())
#     print(i)
#     p[i] = read_ser.decode()
#     i=i+1
#     
# i=-1

# while i <10:
#     ser.write(bytes(x,"utf-8"))
#     read_ser = ser.readline()
#     print(read_ser.decode())
#     print(i)
#     p[i] = read_ser.decode()
#     i=i+1

def background_thread(args):
    count = 0
    global x
    x = "0"
    while True:
        if btn == 'start':
            ser.write(bytes(x,"utf-8"))
            read_ser = ser.readline()
            read_ser = read_ser.decode('ascii').split(',')
            print(read_ser)
            socketio.emit('my_response',
                          {'data':read_ser, 'count':count},
                          namespace='/test')
            count = count+1
        else if btn == "stop":
            ser.write(bytes(x,"utf-8"))
            read_ser = ser.readline()
            read_ser = read_ser.decode('ascii').split(',')
        else:
            ser.write(bytes(x,"utf-8"))
            read_ser = ser.readline()
            read_ser = read_ser.decode('ascii').split(',')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
  


@socketio.on('my_event', namespace='/test')
def test_message(message):
    global x
    x = str(float(message['value'])*51)

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']
    
@socketio.on('click_event1', namespace='/test')
def start(message):
    global btn
    btn = message['value']
    
@socketio.on('click_event2', namespace='/test')
def stop(message):
    global btn
    btn = message['value']

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)