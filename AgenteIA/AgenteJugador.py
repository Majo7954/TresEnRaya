#################################################################
# Nombre      : Entorno                                         #
# Version     : 0.05.03.2017                                    #
# Autor       : Victor                                          #
# Descripcion : Clase Agentes con Adversarios                   #
##################################################################


from AgenteIA.Agente import Agente
from collections import namedtuple


ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')


class AgenteJugador(Agente):

    def __init__(self):
        Agente.__init__(self)
        self.estado = None
        self.juego = None
        self.utilidad = None
        self.altura = 4
        self.profundidad_maxima = 3

    def jugadas(self, estado):
        raise Exception("Error: No se implemento")

    def get_utilidad(self, estado, jugador):
        raise Exception("Error: No se implemento")

    def testTerminal(self, estado):
        return not self.jugadas(estado)

    def getResultado(self, estado, m):
        raise Exception("Error: No se implemento")

    def programa(self):

        #self.acciones = self.minimax()
        #self.acciones = self.podaAlphaBeta()
        self.acciones = self.podaAlphaBetaFunEval(self.estado)
        #self.acciones = self.podaalphaBetaFunEval(self.estado, self.estado.jugador)

    def minimax(self):
        def valorMax(e):
            if self.testTerminal(e):
                return self.get_utilidad(e, self.estado.jugador)
            v = -100
            for a in self.jugadas(e):
                v = max(v, valorMin(self.getResultado(e, a)))
            return v

        def valorMin(e):
            if self.testTerminal(e):
                return self.get_utilidad(e, self.estado.jugador)
            v = 100
            for a in self.jugadas(e):
                v = min(v, valorMax(self.getResultado(e, a)))
            return v

        return max(self.jugadas(self.estado), key=lambda a: valorMin(self.getResultado(self.estado, a)))
    
    def FunEval(self, estado):
        jugador_actual = estado.jugador
        jugador_oponente = 'O' if jugador_actual == 'X' else 'X'
        
        return (
            self.bloqueos(estado, jugador_actual) +
            self.pos3R(estado, jugador_actual) -
            self.pos3R(estado, jugador_oponente)
        )

    def bloqueos(self, estado, jugador):
        bloqueos = 0
        for (i, j), ficha in estado.tablero.items():
            if ficha == jugador:
                bloqueos += self.contar_espacios_vacios_adyacentes(estado, i, j)
        return bloqueos * 10

    def pos3R(self, estado, jugador):
        tresR = 0
        for (i, j), ficha in estado.tablero.items():
            if ficha == jugador:
                tresR += self.contar_3_en_raya(estado, i, j, jugador)
        return tresR * 50

    def contar_espacios_vacios_adyacentes(self, estado, i, j):
        count = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if (ni, nj) not in estado.tablero:
                    count += 1
        return count

    def contar_3_en_raya(self, estado, i, j, jugador):
        count = 0
        direcciones = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for di, dj in direcciones:
            linea = self.obtener_linea(estado, i, j, di, dj, 4)
            if self.es_3_en_raya(linea, jugador):
                count += 1
        return count

    def obtener_linea(self, estado, i, j, di, dj, longitud):
        linea = []
        for _ in range(longitud):
            if (i, j) in estado.tablero:
                linea.append(estado.tablero[(i, j)])
            else:
                linea.append(None)
            i, j = i + di, j + dj
        return linea

    def es_3_en_raya(self, linea, jugador):
        return linea.count(jugador) == 3 and linea.count(None) == 1
    
    # funcion de evaluacion
    #def funcion_evaluacion(self, estado):
    #    bloqueos(estado) + pos3RJ(estado) + pos_3RO(estado)

    def podaAlphaBeta(self, estado):
        def valorMax(e, alpha, beta):
            if self.testTerminal(e):
                return self.get_utilidad(e, estado.jugador)
            v = -float('inf')
            for a in self.jugadas(e):
                v = max(v, valorMin(self.getResultado(e, a), alpha, beta))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def valorMin(e, alpha, beta):
            if self.testTerminal(e):
                return self.get_utilidad(e, estado.jugador)
            v = float('inf')
            for a in self.jugadas(e):
                v = min(v, valorMax(self.getResultado(e, a), alpha, beta))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        alpha = -1e9
        beta = 1e9
        mejor_jugada = None
        for a in self.jugadas(estado):
            valor = valorMin(self.getResultado(estado, a), alpha, beta)
            if valor > alpha:
                alpha = valor
                mejor_jugada = a
        return mejor_jugada
    
    def podaAlphaBetaFunEval(self, estado):
        def valorMax(e, alpha, beta, altura):
            if self.testTerminal(e) or altura == 0:
                return self.FunEval(e)
            v = -float('inf')
            for a in self.jugadas(e):
                v = max(v, valorMin(self.getResultado(e, a), alpha, beta, altura - 1))
                if v >= beta:
                    break  # Se puede salir del bucle si encontramos un valor válido
                alpha = max(alpha, v)
            return v

        def valorMin(e, alpha, beta, altura):
            if self.testTerminal(e) or altura == 0:
                return self.FunEval(e)
            v = float('inf')
            for a in self.jugadas(e):
                v = min(v, valorMax(self.getResultado(e, a), alpha, beta, altura - 1))
                if v <= alpha:
                    break
                beta = min(beta, v)
            return v

        alpha = -float('inf')
        beta = float('inf')
        mejor_jugada = None

        for a in self.jugadas(estado):
            valor = valorMin(self.getResultado(estado, a), alpha, beta, self.profundidad_maxima)
            if valor > alpha:
                alpha = valor
                mejor_jugada = a

        return mejor_jugada
