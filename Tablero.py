from AgenteIA.Entorno import Entorno
from AgenteIA.AgenteJugador import ElEstado


class Tablero(Entorno):

    def __init__(self, h=3, v=3):
        Entorno.__init__(self)
        movidas = [(x, y) for x in range(1, h + 1) for y in range(1, v + 1)]
        self.juegoActual = ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=movidas)

    def percibir(self, agente):
        agente.estado = self.juegoActual
        if agente.estado.movidas:
            agente.programa()

    def ejecutar(self, agente):
        if (agente.acciones == (None, None)):
            return
        print("Agente ", agente.estado.jugador, " juega ", agente.acciones)
        self.juegoActual = agente.getResultado(self.juegoActual, agente.acciones)
        agente.mostrar(self.juegoActual)
        print("Utilidad ", agente.estado.get_utilidad)
        if agente.testTerminal(self.juegoActual):
            agente.vive = False