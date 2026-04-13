"""
AgenteNEnRaya3D — Agente para Tic-Tac-Toe 3D (n x n x n).

Mejoras respecto a la versión anterior (Fase 2 + 3):
  - FunEval acepta vector de pesos externo para integrarse con AG.
  - Nuevas características: amenazas dobles (fork), distinción
    plano/diagonal 3D, bloqueo urgente ponderado.
  - Pesos por defecto ajustados manualmente como línea base.
"""

from itertools import product
from AgenteIA.AgenteJugador import AgenteJugador, ElEstado


# Pesos por defecto — 8 características:
#  [0] centro      peso del control del centro del cubo
#  [1] linea1      línea con 1 ficha propia (apertura)
#  [2] linea2      línea con 2 fichas propias
#  [3] linea3      línea con 3 fichas propias (casi gana)
#  [4] linea4      línea ganadora (victoria)
#  [5] amenaza     bonus por amenaza simple (k-1 + 1 hueco)
#  [6] fork        bonus por amenaza doble (fork)
#  [7] diag3d      multiplicador extra para diagonales 3D puras
PESOS_DEFECTO_3D = [1.5, 1.0, 8.0, 60.0, 10000.0, 120.0, 300.0, 1.3]


class AgenteNEnRaya3D(AgenteJugador):
    """Agente Minimax + poda Alfa-Beta para Tic-Tac-Toe 3D n×n×n."""

    def __init__(self, n=4, k=4, profundidad_maxima=2, pesos=None):
        super().__init__()
        self.n = n
        self.k = k
        self.profundidad_maxima = profundidad_maxima
        self.pesos = pesos if pesos is not None else PESOS_DEFECTO_3D.copy()
        self.lineas_ganadoras = self._generar_lineas_ganadoras()
        self.centro = (n + 1) / 2.0

        # Precalcular qué líneas son diagonales 3D puras (dx≠0, dy≠0, dz≠0)
        self._lineas_diag3d = set()
        for linea in self.lineas_ganadoras:
            dx = linea[1][0] - linea[0][0]
            dy = linea[1][1] - linea[0][1]
            dz = linea[1][2] - linea[0][2]
            if dx != 0 and dy != 0 and dz != 0:
                self._lineas_diag3d.add(linea)

    # ------------------------------------------------------------------
    # Interfaz del juego
    # ------------------------------------------------------------------

    def estado_inicial(self):
        movidas = [(x, y, z) for x, y, z in product(range(1, self.n + 1), repeat=3)]
        return ElEstado(jugador='X', get_utilidad=0, tablero={}, movidas=movidas)

    def jugadas(self, estado):
        return estado.movidas

    def getResultado(self, estado, m):
        if m not in estado.movidas:
            return estado
        tablero = estado.tablero.copy()
        tablero[m] = estado.jugador
        movidas = list(estado.movidas)
        movidas.remove(m)
        utilidad = self.computa_utilidad(tablero, m, estado.jugador)
        return ElEstado(
            jugador=('O' if estado.jugador == 'X' else 'X'),
            get_utilidad=utilidad,
            tablero=tablero,
            movidas=movidas,
        )

    def get_utilidad(self, estado, jugador):
        return estado.get_utilidad if jugador == 'X' else -estado.get_utilidad

    def testTerminal(self, estado):
        return estado.get_utilidad != 0 or len(estado.movidas) == 0

    def mostrar(self, estado):
        tablero = estado.tablero
        for z in range(1, self.n + 1):
            print(f"\nNivel z={z}")
            for x in range(1, self.n + 1):
                fila = [tablero.get((x, y, z), '.') for y in range(1, self.n + 1)]
                print(' '.join(fila))
        print()

    def computa_utilidad(self, tablero, ultima_movida, jugador):
        for linea in self.lineas_por_movida[ultima_movida]:
            if all(tablero.get(celda) == jugador for celda in linea):
                return 1 if jugador == 'X' else -1
        return 0

    # ------------------------------------------------------------------
    # Motor Minimax + poda Alfa-Beta con profundidad limitada
    # ------------------------------------------------------------------

    def programa(self):
        self.acciones = self.poda_alpha_beta_limitada(self.estado)

    def poda_alpha_beta_limitada(self, estado):
        jugador_raiz = estado.jugador

        def valor_max(e, alpha, beta, profundidad):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador_raiz)
            if profundidad == 0:
                return self.FunEval(e, jugador_raiz)
            valor = -float('inf')
            for accion in self.ordenar_jugadas(e):
                valor = max(valor, valor_min(self.getResultado(e, accion), alpha, beta, profundidad - 1))
                if valor >= beta:
                    return valor
                alpha = max(alpha, valor)
            return valor

        def valor_min(e, alpha, beta, profundidad):
            if self.testTerminal(e):
                return self.get_utilidad(e, jugador_raiz)
            if profundidad == 0:
                return self.FunEval(e, jugador_raiz)
            valor = float('inf')
            for accion in self.ordenar_jugadas(e):
                valor = min(valor, valor_max(self.getResultado(e, accion), alpha, beta, profundidad - 1))
                if valor <= alpha:
                    return valor
                beta = min(beta, valor)
            return valor

        mejor_accion = None
        mejor_valor = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for accion in self.ordenar_jugadas(estado):
            valor = valor_min(self.getResultado(estado, accion), alpha, beta, self.profundidad_maxima - 1)
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = accion
            alpha = max(alpha, mejor_valor)

        return mejor_accion

    # ------------------------------------------------------------------
    # Función de evaluación heurística — Fase 2 mejorada
    # ------------------------------------------------------------------

    def FunEval(self, estado, jugador_raiz=None):
        """
        E(s) = w0·centro + sum(wi·lineasi) + w5·amenaza + w6·fork
        Los 8 pesos pueden ser inyectados externamente por el AG.

        Características nuevas respecto a versión anterior:
          - Distinción diagonal 3D pura (multiplicador w[7])
          - Amenaza doble (fork): detecta posición con >=2 amenazas
          - Bloqueo ponderado asimétrico (bloquear vale 1.2x atacar)
        """
        if jugador_raiz is None:
            jugador_raiz = estado.jugador

        w = self.pesos
        oponente = 'O' if jugador_raiz == 'X' else 'X'
        puntaje = 0.0

        # --- Característica 0: control del centro ---
        for (x, y, z), ficha in estado.tablero.items():
            distancia = abs(x - self.centro) + abs(y - self.centro) + abs(z - self.centro)
            bonus_pos = (3 * self.n) - distancia
            if ficha == jugador_raiz:
                puntaje += w[0] * bonus_pos
            else:
                puntaje -= w[0] * bonus_pos

        # --- Características 1-4: líneas potenciales ---
        for linea in self.lineas_ganadoras:
            fichas  = [estado.tablero.get(celda) for celda in linea]
            propias = fichas.count(jugador_raiz)
            rivales = fichas.count(oponente)

            if propias > 0 and rivales > 0:
                continue  # línea muerta

            # Factor extra para diagonales 3D (más difíciles de bloquear)
            diag_factor = w[7] if linea in self._lineas_diag3d else 1.0

            if propias == self.k:
                puntaje += w[4] * diag_factor
            elif rivales == self.k:
                puntaje -= w[4] * diag_factor
            elif rivales == 0 and 0 < propias < self.k:
                # w[1], w[2] o w[3] según cuántas fichas tenga la línea
                puntaje += w[propias] * diag_factor
            elif propias == 0 and 0 < rivales < self.k:
                puntaje -= w[rivales] * diag_factor

        # --- Características 5-6: amenazas y forks ---
        amenaza_propia = self.contar_lineas_casi_ganadoras(estado, jugador_raiz)
        amenaza_rival  = self.contar_lineas_casi_ganadoras(estado, oponente)

        # Bloquear es ligeramente más urgente que atacar (factor 1.2)
        puntaje += w[5] * amenaza_propia
        puntaje -= w[5] * 1.2 * amenaza_rival

        # Fork: tener >=2 amenazas simultáneas es muy valioso
        if amenaza_propia >= 2:
            puntaje += w[6]
        if amenaza_rival >= 2:
            puntaje -= w[6]

        return puntaje

    # ------------------------------------------------------------------
    # Utilidades auxiliares
    # ------------------------------------------------------------------

    def contar_lineas_casi_ganadoras(self, estado, jugador):
        """Cuenta líneas con exactamente k-1 fichas propias y 1 hueco."""
        oponente = 'O' if jugador == 'X' else 'X'
        total = 0
        for linea in self.lineas_ganadoras:
            fichas = [estado.tablero.get(celda) for celda in linea]
            if (fichas.count(jugador)  == self.k - 1
                    and fichas.count(None) == 1
                    and fichas.count(oponente) == 0):
                total += 1
        return total

    def ordenar_jugadas(self, estado):
        """Ordena movidas por valor heurístico para maximizar la poda."""
        jugador  = estado.jugador
        oponente = 'O' if jugador == 'X' else 'X'

        def prioridad(mov):
            x, y, z = mov
            distancia = abs(x - self.centro) + abs(y - self.centro) + abs(z - self.centro)
            score = -distancia
            # Victoria inmediata
            nuevo = self.getResultado(estado, mov)
            if nuevo.get_utilidad == (1 if jugador == 'X' else -1):
                score += 10_000
            # Bloqueo de victoria rival
            tablero_temp = estado.tablero.copy()
            tablero_temp[mov] = oponente
            if self.computa_utilidad(tablero_temp, mov, oponente) == (1 if oponente == 'X' else -1):
                score += 5_000
            return score

        return sorted(estado.movidas, key=prioridad, reverse=True)

    # ------------------------------------------------------------------
    # Generación de líneas ganadoras e índice inverso
    # ------------------------------------------------------------------

    def _generar_lineas_ganadoras(self):
        direcciones = [
            (dx, dy, dz)
            for dx, dy, dz in product([-1, 0, 1], repeat=3)
            if not (dx == 0 and dy == 0 and dz == 0)
        ]
        canonicas = [
            (dx, dy, dz) for dx, dy, dz in direcciones
            if (dx, dy, dz) > tuple(-v for v in (dx, dy, dz))
        ]

        lineas = []
        for x, y, z in product(range(1, self.n + 1), repeat=3):
            for dx, dy, dz in canonicas:
                fin_x = x + (self.k - 1) * dx
                fin_y = y + (self.k - 1) * dy
                fin_z = z + (self.k - 1) * dz
                if not self._dentro(fin_x, fin_y, fin_z):
                    continue
                if self._dentro(x - dx, y - dy, z - dz):
                    continue
                linea = tuple((x + i * dx, y + i * dy, z + i * dz) for i in range(self.k))
                lineas.append(linea)

        self.lineas_por_movida = {
            celda: [] for celda in product(range(1, self.n + 1), repeat=3)
        }
        for linea in lineas:
            for celda in linea:
                self.lineas_por_movida[celda].append(linea)

        return lineas

    def _dentro(self, x, y, z):
        return 1 <= x <= self.n and 1 <= y <= self.n and 1 <= z <= self.n
