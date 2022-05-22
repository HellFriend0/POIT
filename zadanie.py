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

def background_thread(args):
    count = 0
    counter = 0
    List = []
    global x
    x = "0"
    while True:
        if btn == 'start':
            ser.write(bytes(x,"utf-8"))
            read_ser = ser.readline()
            read_ser = read_ser.decode('ascii').split(',')
            
            hodnota = read_ser[0]
            hodnota = hodnota.strip("\r\n")
            hodnota = float(hodnota)
            
            data = {
            "x": counter,
            "y": hodnota,
            "v": float(x)/51
            }
            List.append(data)
            counter += 1
            
            socketio.emit('my_response',
                          {'data':read_ser,'data2':float(x)/51, 'count':count},
                          namespace='/test')
            count = count+1
        elif btn == "stop":
            if len(List)>0:
                array = str(List).replace("'","\"")
                
                write2file(array)
                
            List = []
            counter = 0
            
            
            #ser.write(bytes(x,"utf-8"))
            #read_ser = ser.readline()
            #read_ser = read_ser.decode('ascii').split(',')
            
        else:
            ser.write(bytes(x,"utf-8"))
            read_ser = ser.readline()
            read_ser = read_ser.decode('ascii').split(',')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/write')
def write2file(value):
    fo = open("static/files/test.txt","a+")
    val = value
    fo.write("%s\r\n" %val)
    return "done"

@app.route('/read/<string:num>')
def readmyfile(num):
    fo = open("static/files/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

@socketio.on('file_reading', namespace='/test')
def file_message(message):
    row = message['value']
    file = readmyfile(int(row))
    emit('file_response',{'data':file})

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
    emit('my_response', {'data': 'Connected','data2' : 'I am', 'count': 0})

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