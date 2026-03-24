import socketio
from Tablero import Tablero
from AgenteNEnRaya import AgenteNEnRaya

sio = socketio.Client()
id = 1  # ID del cliente 1

N = 3
tablero = Tablero()
agente_ia = AgenteNEnRaya()

tablero.percibir(agente_ia)
agente_ia.programa()
movimiento_ia = agente_ia.acciones
tabla = tablero.juegoActual

@sio.event
def connect():
    print('Cliente 1 conectado')
    sio.emit('client_message', {
        'id': id,
        'mensaje': movimiento_ia,
        'tabla': tabla
        })

@sio.on('server_message')
def on_message(data):
    if data['id'] == 2:
        tablero.juegoActual = agente_ia.getResultado(data['tabla'], data['mensaje'])
        tablero.percibir(agente_ia)
        movimiento_ia = agente_ia.acciones
        sio.emit('client_message', {
            'id': id,
            'mensaje': movimiento_ia,
            'tabla': tablero.juegoActual
            })

@sio.event
def disconnect():
    print('Cliente 1 desconectado')

if __name__ == '__main__':
    sio.connect('http://localhost:5000')  # Cambia esto a la URL de tu servidor si es necesario
    sio.wait()
