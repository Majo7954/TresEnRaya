import socketio
from Tablero import Tablero
from AgenteNEnRaya import AgenteNEnRaya

sio = socketio.Client()
id = 2  # ID del cliente 2

tablero = Tablero()
agente_ia = AgenteNEnRaya()

tablero.percibir(agente_ia)
agente_ia.programa()
movimiento_ia = agente_ia.acciones
tabla = tablero.juegoActual

print(tabla)

@sio.event
def connect():
    print('Cliente 2 conectado')

@sio.on('server_message')
def on_message(data):
    if data['id'] == 1:
        print('Cliente 2 recibe')
        tablero.percibir(agente_ia)
        agente_ia.programa()
        movimiento_ia = agente_ia.acciones
        tabla = agente_ia.getResultado(tablero.juegoActual, movimiento_ia)

        # Convierte las tuplas de movidas a listas
        if isinstance(tabla, dict) and 'movidas' in tabla:
            tabla['movidas'] = [list(movida) for movida in tabla['movidas']]  # Convertir tuplas a listas

        # Verifica si el contenido es correcto
        print('Enviando:', {'id': id, 'mensaje': movimiento_ia, 'tabla': tabla})

        sio.emit('client_message', {
            'id': id,
            'mensaje': movimiento_ia,
            'tabla': tabla
        })

@sio.event
def disconnect():
    print('Cliente 2 desconectado')

if __name__ == '__main__':
    sio.connect('http://localhost:5000')  # Cambia esto a la URL de tu servidor si es necesario
    sio.wait()
