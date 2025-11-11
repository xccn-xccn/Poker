import socketio

# standard Python
sio = socketio.Client(logger=True, engineio_logger=True)

sio.connect('http://localhost:5000')
sio.emit('my message', {'foo': 'bar'})

@sio.event
def message(data):
    print('I received a message!')

@sio.on('my message')
def on_message(data):
    print('I received a message!')
    
sio.disconnect()