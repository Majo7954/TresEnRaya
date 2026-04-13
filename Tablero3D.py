from AgenteIA.Entorno import Entorno


class Tablero3D(Entorno):
    def __init__(self, agente_3d):
        super().__init__()
        self.agente_3d = agente_3d
        self.juegoActual = agente_3d.estado_inicial()

    def percibir(self, agente):
        agente.estado = self.juegoActual
        if agente.estado.movidas:
            agente.programa()

    def ejecutar(self, agente):
        if agente.acciones is None:
            return
        print("Agente", agente.estado.jugador, "juega", agente.acciones)
        self.juegoActual = agente.getResultado(self.juegoActual, agente.acciones)
        agente.mostrar(self.juegoActual)
        print("Utilidad", self.juegoActual.get_utilidad)
        if agente.testTerminal(self.juegoActual):
            agente.vive = False
