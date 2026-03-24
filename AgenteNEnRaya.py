from AgenteIA.AgenteJugador import AgenteJugador
from AgenteIA.AgenteJugador import ElEstado


class AgenteNEnRaya(AgenteJugador):

    def __init__(self, h=3, v=3, k=3):
        AgenteJugador.__init__(self)
        self.h = h
        self.v = v
        self.k = k

    def jugadas(self, estado):
        return estado.movidas

    def getResultado(self, estado, m):
        if m not in estado.movidas:
            return ElEstado(jugador=('O' if estado.jugador == 'X' else 'X'),
                            get_utilidad=self.computa_utilidad(estado.tablero, m, estado.jugador),
                            tablero=estado.tablero, movidas=estado.movidas)
        tablero = estado.tablero.copy()
        tablero[m] = estado.jugador
        movidas = list(estado.movidas)
        movidas.remove(m)
        return ElEstado(jugador=('O' if estado.jugador == 'X' else 'X'),
                        get_utilidad=self.computa_utilidad(tablero, m, estado.jugador),
                        tablero=tablero, movidas=movidas)

    def get_utilidad(self, estado, jugador):
        return estado.get_utilidad if jugador == 'X' else -estado.get_utilidad

    def testTerminal(self, estado):
        return estado.get_utilidad != 0 or len(estado.movidas) == 0
    

    def mostrar(self, estado):
        tablero = estado.tablero
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(tablero.get((x, y), '.')+" ", end="")
            print()

    def computa_utilidad(self, tablero, m, jugador):
        if (self.en_raya(tablero, m, jugador, (0, 1)) or
                self.en_raya(tablero, m, jugador, (1, 0)) or
                self.en_raya(tablero, m, jugador, (1, -1)) or
                self.en_raya(tablero, m, jugador, (1, 1))):
            return +1 if jugador == 'X' else -1
        else:
            return 0

    def en_raya(self, tablero, m, jugador, delta_x_y):
        (delta_x, delta_y) = delta_x_y
        x, y = m
        n = 0
        while tablero.get((x, y)) == jugador:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = m
        while tablero.get((x, y)) == jugador:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1
        return n >= self.k
    
 
    def programa(self):
        self.acciones = self.podaAlphaBetaFunEval(self.estado)


    '''
    def programa(self):
        self.acciones = self.minimax()

    '''
