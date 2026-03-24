import socketio

# Crear un cliente SocketIO
sio = socketio.Client()

# Evento que se ejecuta cuando se conecta al servidor
@sio.event
def connect():
    print("Conectado al servidor")

# Evento que se ejecuta cuando se recibe un mensaje del servidor
@sio.event
def server_message(data):
    print("Mensaje del servidor:", data)

# Evento que se ejecuta cuando se desconecta del servidor
@sio.event
def disconnect():
    print("Desconectado del servidor")

try:
    # Conectar a la URL pública que te dio ngrok (usando wss)
    sio.connect("wss://fabb-189-28-64-215.ngrok-free.app/")

    # Enviar un mensaje al servidor
    sio.emit('client_message', {'data': 'hola mundo', 'id': 1})

    # Mantener la conexión abierta para recibir mensajes
    sio.wait()  # Esto espera hasta que se cierre la conexión

except Exception as e:
    print(f"Ocurrió un error: {e}")
