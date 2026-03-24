import eventlet
eventlet.monkey_patch()
from flask import Flask
from flask_socketio import SocketIO, emit
from Tablero import Tablero
tablero = Tablero()

# Configuración de Flask y SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Almacenar clientes conectados
clientes = {}

# Evento cuando el cliente se conecta
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

# Evento para manejar los mensajes entrantes del cliente
@socketio.on('client_message')
def handle_message(data):
    id = data['id']
    mensaje = data['mensaje']
    tabla = data['tabla']
    
    print(f"Cliente {id} envió: {mensaje}")
    '''
    if id == 1 and mensaje == "hola":
        # Cliente 1 dice "hola", le decimos al Cliente 2 que envíe "como estas?"
        emit('server_message', {'mensaje': "hola", 'from': 1}, broadcast=True)
        
    elif id == 2 and mensaje == "como estas?":
        # Cliente 2 responde "como estas?", ahora Cliente 1 responde
        emit('server_message', {'mensaje': "como estas?", 'from': 2}, broadcast=True)
        
    elif id == 1 and mensaje == "bien y vos?":
        # Cliente 1 responde "bien y vos?", ahora Cliente 2 dice "yo tambien"
        emit('server_message', {'mensaje': "bien y vos?", 'from': 1}, broadcast=True)
    
    elif id == 2 and mensaje == "yo tambien":
        # Cliente 2 finaliza con "yo tambien"
        emit('server_message', {'mensaje': "yo tambien", 'from': 2}, broadcast=True)

    # Manejar la secuencia de "blabla"
    elif current_blabla <= max_blabla:
        emit('server_message', {'mensaje': f"blabla{current_blabla}", 'from': id}, broadcast=True)
        current_blabla += 1
    '''
    if tablero.juegoActual.movidas:
        emit('server_message', {'id': id, 'mensaje': mensaje, 'tabla': tabla}, broadcast=True)

# Evento cuando el cliente se desconecta
@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# Iniciar el servidor en el puerto 5001
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
