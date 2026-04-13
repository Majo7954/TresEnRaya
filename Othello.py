import random
import copy
import json
import time
import statistics
import matplotlib.pyplot as plt
from collections import namedtuple
from AgenteIA.AgenteJugador import AgenteJugador

# ============================================================================
# PARTE 1: REGLAS DEL JUEGO
# ============================================================================

class Othello():
    """Clase que contiene las reglas y el estado del juego Othello"""

    DIRECCIONES = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]

    def __init__(self):
        self.tablero = self._crear_tablero_inicial()
        self.jugador_actual = 'N'
        self.ultimo_movimiento = None

    def _crear_tablero_inicial(self):
        tablero = [['.' for _ in range(8)] for _ in range(8)]
        tablero[3][3] = 'N'
        tablero[4][4] = 'N'
        tablero[3][4] = 'B'
        tablero[4][3] = 'B'
        return tablero

    def mostrar(self):
        print("   0 1 2 3 4 5 6 7")
        for i in range(8):
            print(f"{i}  ", end="")
            for j in range(8):
                print(self.tablero[i][j], end=" ")
            print()
        print(f"Turno: {'Negras (MAX)' if self.jugador_actual == 'N' else 'Blancas (MIN)'}")

    def es_dentro_tablero(self, fila, col):
        return 0 <= fila < 8 and 0 <= col < 8

    def es_movimiento_legal(self, fila, col, jugador):
        if not self.es_dentro_tablero(fila, col):
            return False
        if self.tablero[fila][col] != '.':
            return False

        oponente = 'B' if jugador == 'N' else 'N'
        for df, dc in self.DIRECCIONES:
            f, c = fila + df, col + dc
            hay_oponente = False
            while self.es_dentro_tablero(f, c) and self.tablero[f][c] == oponente:
                f += df
                c += dc
                hay_oponente = True
            if hay_oponente and self.es_dentro_tablero(f, c) and self.tablero[f][c] == jugador:
                return True
        return False

    def obtener_movimientos_legales(self, jugador=None):
        if jugador is None:
            jugador = self.jugador_actual
        movimientos = []
        for i in range(8):
            for j in range(8):
                if self.es_movimiento_legal(i, j, jugador):
                    movimientos.append((i, j))
        return movimientos

    def aplicar_movimiento(self, fila, col, jugador=None):
        if jugador is None:
            jugador = self.jugador_actual
        if not self.es_movimiento_legal(fila, col, jugador):
            return False

        self.tablero[fila][col] = jugador
        oponente = 'B' if jugador == 'N' else 'N'

        for df, dc in self.DIRECCIONES:
            f, c = fila + df, col + dc
            fichas_a_voltear = []
            while self.es_dentro_tablero(f, c) and self.tablero[f][c] == oponente:
                fichas_a_voltear.append((f, c))
                f += df
                c += dc
            if self.es_dentro_tablero(f, c) and self.tablero[f][c] == jugador:
                for (ff, cc) in fichas_a_voltear:
                    self.tablero[ff][cc] = jugador

        self.jugador_actual = oponente
        self.ultimo_movimiento = (fila, col)

        if len(self.obtener_movimientos_legales()) == 0:
            self.jugador_actual = jugador
        return True

    def es_terminal(self):
        tiene_N = len(self.obtener_movimientos_legales('N')) > 0
        tiene_B = len(self.obtener_movimientos_legales('B')) > 0
        return not (tiene_N or tiene_B)

    def obtener_resultado(self):
        if not self.es_terminal():
            return 0
        negras, blancas = self.contar_fichas()
        if negras > blancas:
            return 1
        elif blancas > negras:
            return -1
        else:
            return 0

    def copiar(self):
        nuevo = Othello()
        nuevo.tablero = copy.deepcopy(self.tablero)
        nuevo.jugador_actual = self.jugador_actual
        nuevo.ultimo_movimiento = self.ultimo_movimiento
        return nuevo

    def contar_fichas(self):
        negras = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'N')
        blancas = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'B')
        return negras, blancas

    # =====================================================================
    # INTERFAZ TIPO "JUEGO" (REQUERIDA POR LA CONSIGNA)
    # =====================================================================

    @staticmethod
    def estado_inicial():
        return Othello()

    def jugadas_legales(self, estado=None, jugador=None):
        juego = estado if estado is not None else self
        return juego.obtener_movimientos_legales(jugador)

    def aplicar_jugada(self, estado, jugada, jugador):
        nuevo = estado.copiar()
        nuevo.aplicar_movimiento(jugada[0], jugada[1], jugador)
        return nuevo

    def es_estado_terminal(self, estado):
        return estado.es_terminal()

    def resultado_estado(self, estado):
        return estado.obtener_resultado()


# ============================================================================
# PARTE 2: FUNCIÓN DE EVALUACIÓN CON PESOS
# ============================================================================

class OthelloEvaluacion:

    PESOS_DEFECTO = [1.0, 0.5, 2.0, 0.3]

    def __init__(self, pesos=None):
        self.pesos = pesos if pesos is not None else self.PESOS_DEFECTO.copy()

    def diferencia_fichas(self, juego, jugador_max='N'):
        negras, blancas = juego.contar_fichas()
        total = negras + blancas
        if total == 0:
            return 0
        return (negras - blancas) / 64.0 if jugador_max == 'N' else (blancas - negras) / 64.0

    def movilidad(self, juego, jugador_max='N'):
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        total = mov_max + mov_min
        if total == 0:
            return 0
        return (mov_max - mov_min) / 64.0

    def control_esquinas(self, juego, jugador_max='N'):
        esquinas = [(0, 0), (0, 7), (7, 0), (7, 7)]
        valor_max = sum(1 for f, c in esquinas if juego.tablero[f][c] == jugador_max)
        valor_min = sum(1 for f, c in esquinas if juego.tablero[f][c] not in (jugador_max, '.'))
        return (valor_max - valor_min) / 4.0

    def paridad(self, juego, jugador_max='N'):
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        total_movimientos = mov_max + mov_min
        if total_movimientos <= 10:
            if total_movimientos % 2 == 0:
                return 0.5 if mov_max > mov_min else -0.5
            else:
                return -0.5 if mov_max > mov_min else 0.5
        return 0

    def evaluar(self, juego, jugador_max='N'):
        if juego.es_terminal():
            resultado = juego.obtener_resultado()
            return resultado if jugador_max == 'N' else -resultado

        f1 = self.diferencia_fichas(juego, jugador_max)
        f2 = self.movilidad(juego, jugador_max)
        f3 = self.control_esquinas(juego, jugador_max)
        f4 = self.paridad(juego, jugador_max)

        features = {
            "fichas": f1,
            "movilidad": f2,
            "esquinas": f3,
            "paridad": f4
        }

        valores = list(features.values())
        return sum(p * v for p, v in zip(self.pesos, valores))


# ============================================================================
# PARTE 3: AGENTE OTHELLO CON MINIMAX PROPIO Y MÉTRICAS REALES
# ============================================================================

ElEstadoOthello = namedtuple('ElEstadoOthello', 'jugador, tablero, movidas')


class OthelloAgente(AgenteJugador):
    """
    Agente Othello con minimax propio y poda alfa-beta.
    Implementa métricas REALES de nodos expandidos y podados.
    """

    def __init__(self, profundidad=4, pesos=None, jugador='N'):
        AgenteJugador.__init__(self)
        self.profundidad_maxima = profundidad
        self.evaluacion = OthelloEvaluacion(pesos)
        self.jugador = jugador
        
        self.nodos_expandidos = 0
        self.nodos_podados = 0
        self.tiempo_ultima_jugada = 0
        self.profundidad_real = 0

    def _juego_a_estado(self, juego: Othello) -> ElEstadoOthello:
        movidas = juego.obtener_movimientos_legales(juego.jugador_actual)
        return ElEstadoOthello(
            jugador=juego.jugador_actual,
            tablero=copy.deepcopy(juego.tablero),
            movidas=movidas
        )

    def _estado_a_juego(self, estado: ElEstadoOthello) -> Othello:
        juego = Othello()
        juego.tablero = copy.deepcopy(estado.tablero)
        juego.jugador_actual = estado.jugador
        return juego

    def _es_terminal(self, estado: ElEstadoOthello) -> bool:
        juego = self._estado_a_juego(estado)
        return juego.es_terminal()

    def _obtener_utilidad(self, estado: ElEstadoOthello) -> float:
        juego = self._estado_a_juego(estado)
        resultado = juego.obtener_resultado()
        return resultado if self.jugador == 'N' else -resultado

    def _obtener_movimientos(self, estado: ElEstadoOthello):
        juego = self._estado_a_juego(estado)
        return juego.obtener_movimientos_legales(estado.jugador)

    def _aplicar_movimiento(self, estado: ElEstadoOthello, movimiento):
        juego = self._estado_a_juego(estado)
        juego.aplicar_movimiento(movimiento[0], movimiento[1], estado.jugador)
        return self._juego_a_estado(juego)

    def _minimax_alfa_beta(self, estado: ElEstadoOthello, profundidad, alfa, beta, es_max):
        self.nodos_expandidos += 1

        if profundidad == 0 or self._es_terminal(estado):
            return self.FunEval(estado), None

        movimientos = self._obtener_movimientos(estado)
        
        if not movimientos:
            juego = self._estado_a_juego(estado)
            oponente = 'B' if estado.jugador == 'N' else 'N'
            nuevo_estado = self._juego_a_estado(juego)
            nuevo_estado = ElEstadoOthello(
                jugador=oponente,
                tablero=nuevo_estado.tablero,
                movidas=[]
            )
            return self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, not es_max)[0], None

        mejor_movimiento = movimientos[0]

        if es_max:
            valor = float('-inf')
            for mov in movimientos:
                nuevo_estado = self._aplicar_movimiento(estado, mov)
                valor_hijo, _ = self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, False)
                
                if valor_hijo > valor:
                    valor = valor_hijo
                    mejor_movimiento = mov
                
                alfa = max(alfa, valor)
                if alfa >= beta:
                    self.nodos_podados += len(movimientos) - (movimientos.index(mov) + 1)
                    break
            return valor, mejor_movimiento
        else:
            valor = float('inf')
            for mov in movimientos:
                nuevo_estado = self._aplicar_movimiento(estado, mov)
                valor_hijo, _ = self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, True)
                
                if valor_hijo < valor:
                    valor = valor_hijo
                    mejor_movimiento = mov
                
                beta = min(beta, valor)
                if alfa >= beta:
                    self.nodos_podados += len(movimientos) - (movimientos.index(mov) + 1)
                    break
            return valor, mejor_movimiento

    def jugadas(self, estado: ElEstadoOthello):
        return self._obtener_movimientos(estado)

    def getResultado(self, estado: ElEstadoOthello, movimiento) -> ElEstadoOthello:
        return self._aplicar_movimiento(estado, movimiento)

    def get_utilidad(self, estado: ElEstadoOthello, jugador):
        return self._obtener_utilidad(estado)

    def FunEval(self, estado: ElEstadoOthello):
        juego = self._estado_a_juego(estado)
        return self.evaluacion.evaluar(juego, self.jugador)

    def seleccionar_movimiento(self, juego: Othello):
        estado = self._juego_a_estado(juego)

        self.nodos_expandidos = 0
        self.nodos_podados = 0

        inicio = time.time()

        _, movimiento = self._minimax_alfa_beta(
            estado, 
            self.profundidad_maxima, 
            float('-inf'), 
            float('inf'), 
            True
        )

        fin = time.time()
        self.tiempo_ultima_jugada = fin - inicio
        self.profundidad_real = self.profundidad_maxima

        return movimiento
    
    def obtener_metricas(self):
        return {
            "nodos_expandidos": self.nodos_expandidos,
            "nodos_podados": self.nodos_podados,
            "tiempo": self.tiempo_ultima_jugada,
            "profundidad": self.profundidad_real
        }


# ============================================================================
# PARTE 4: ALGORITMO GENÉTICO
# ============================================================================

class OthelloGenetico:
    def __init__(self, tam_poblacion=30, generaciones=20, profundidad=3, partidas_por_fitness=20):
        random.seed(42)
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.profundidad = profundidad
        self.partidas_por_fitness = max(20, partidas_por_fitness)
        self.poblacion = []
        self.mejor_historial = []
        self.promedio_historial = []
        self.mejor_individuo_global = None
        self.mejor_fitness_global = -1

    def _crear_individuo(self):
        return [random.uniform(0, 2) for _ in range(4)]

    def _normalizar_pesos(self, individuo):
        total = sum(individuo)
        if total > 0:
            return [w * 4.0 / total for w in individuo]
        return [1.0, 1.0, 1.0, 1.0]

    def _jugar_partida(self, agente1, agente2):
        juego = Othello()
        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            agente = agente1 if jugador_actual == agente1.jugador else agente2
            mov = agente.seleccionar_movimiento(juego)
            if mov is not None:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultado = juego.obtener_resultado()
        if resultado == 1 and agente1.jugador == 'N':
            return 1
        elif resultado == -1 and agente1.jugador == 'B':
            return 1
        elif resultado == 0:
            return 0
        else:
            return -1

    def _calcular_fitness(self, individuo):
        pesos = self._normalizar_pesos(individuo)
        victorias = 0

        for i in range(self.partidas_por_fitness):
            if i % 2 == 0:
                agente_prueba = OthelloAgente(profundidad=self.profundidad, pesos=pesos, jugador='N')
                agente_base = OthelloAgente(profundidad=self.profundidad,
                                           pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='B')
            else:
                agente_prueba = OthelloAgente(profundidad=self.profundidad, pesos=pesos, jugador='B')
                agente_base = OthelloAgente(profundidad=self.profundidad,
                                           pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='N')

            resultado = self._jugar_partida(agente_prueba, agente_base)
            if resultado == 1:
                victorias += 1
            elif resultado == 0:
                victorias += 0.5

        return victorias / self.partidas_por_fitness

    def _seleccion_torneo(self, fitnesses, k=3):
        mejor_idx, mejor_fitness = None, -1
        for _ in range(k):
            idx = random.randint(0, len(self.poblacion) - 1)
            if fitnesses[idx] > mejor_fitness:
                mejor_fitness = fitnesses[idx]
                mejor_idx = idx
        return self.poblacion[mejor_idx]

    def _cruce_blx(self, padre1, padre2, alpha=0.5):
        hijo = []
        for i in range(len(padre1)):
            min_val = min(padre1[i], padre2[i])
            max_val = max(padre1[i], padre2[i])
            rango = max_val - min_val
            hijo.append(random.uniform(min_val - alpha * rango, max_val + alpha * rango))
        return hijo

    def _mutacion_gaussiana(self, individuo, tasa=0.2, sigma=0.3):
        for i in range(len(individuo)):
            if random.random() < tasa:
                individuo[i] = max(0.1, min(3.0, individuo[i] + random.gauss(0, sigma)))
        return individuo

    def evolucionar(self, verbose=True):
        self.poblacion = [self._crear_individuo() for _ in range(self.tam_poblacion)]

        for gen in range(self.generaciones):
            fitnesses = [self._calcular_fitness(ind) for ind in self.poblacion]

            mejor_fitness = max(fitnesses)
            mejor_ind = self.poblacion[fitnesses.index(mejor_fitness)]
            promedio_fitness = sum(fitnesses) / len(fitnesses)

            if mejor_fitness > self.mejor_fitness_global:
                self.mejor_fitness_global = mejor_fitness
                self.mejor_individuo_global = mejor_ind.copy()

            self.mejor_historial.append(mejor_fitness)
            self.promedio_historial.append(promedio_fitness)

            if verbose:
                print(f"Gen {gen+1:3d} | Mejor: {mejor_fitness:.4f} | "
                      f"Promedio: {promedio_fitness:.4f} | "
                      f"Pesos: {[round(w, 2) for w in mejor_ind]}")

            nueva_poblacion = [mejor_ind]
            while len(nueva_poblacion) < self.tam_poblacion:
                padre1 = self._seleccion_torneo(fitnesses)
                padre2 = self._seleccion_torneo(fitnesses)
                hijo = self._cruce_blx(padre1, padre2)
                hijo = self._mutacion_gaussiana(hijo)
                nueva_poblacion.append(hijo)

            self.poblacion = nueva_poblacion

        mejores_pesos = self._normalizar_pesos(self.mejor_individuo_global)

        if verbose:
            print(f"\n✅ Mejores pesos globales: {[round(w, 2) for w in mejores_pesos]}")
            print(f"   Fitness: {self.mejor_fitness_global:.4f}")

        return mejores_pesos, self.mejor_historial, self.promedio_historial

    def guardar_pesos(self, pesos, archivo='mejores_pesos_othello.json'):
        with open(archivo, 'w') as f:
            json.dump({'pesos': pesos}, f, indent=2)
        print(f"💾 Pesos guardados en '{archivo}'")

    def cargar_pesos(self, archivo='mejores_pesos_othello.json'):
        with open(archivo, 'r') as f:
            data = json.load(f)
        print(f"📂 Pesos cargados desde '{archivo}': {data['pesos']}")
        return data['pesos']

    def graficar_convergencia(self, archivo='convergencia_othello.png'):
        if not self.mejor_historial:
            print("No hay datos de evolución. Ejecuta evolucionar() primero.")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(self.mejor_historial, label='Mejor fitness', color='blue', linewidth=2)
        plt.plot(self.promedio_historial, label='Fitness promedio', color='orange', linewidth=2, linestyle='--')
        plt.xlabel('Generación')
        plt.ylabel('Fitness (tasa de victorias)')
        plt.title('Convergencia del Algoritmo Genético — Othello')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(archivo)
        plt.show()
        print(f"📊 Gráfica guardada en '{archivo}'")


# ============================================================================
# PARTE 5: FUNCIONES DE EXPERIMENTACIÓN
# ============================================================================

def jugar_partidas(agente1, agente2, n=20):
    resultados = []
    metricas_agente1 = []

    for i in range(n):
        juego = Othello()
        
        if i % 2 == 0:
            juego.jugador_actual = agente1.jugador
        else:
            juego.jugador_actual = agente2.jugador

        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            agente = agente1 if jugador_actual == agente1.jugador else agente2
            mov = agente.seleccionar_movimiento(juego)
            
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultados.append(juego.obtener_resultado())
        
        if hasattr(agente1, 'obtener_metricas'):
            metricas_agente1.append(agente1.obtener_metricas())

    return resultados, metricas_agente1


def comparar_agentes(agente1, agente2, n_partidas=20):
    print(f"\n{'='*60}")
    print(f"Comparando: {agente1.__class__.__name__} (prof={agente1.profundidad_maxima}) vs "
          f"{agente2.__class__.__name__} (prof={agente2.profundidad_maxima})")
    print(f"Partidas: {n_partidas}")
    print(f"{'='*60}")

    resultados, metricas = jugar_partidas(agente1, agente2, n_partidas)
    
    victorias = sum(1 for r in resultados if r == 1)
    derrotas = sum(1 for r in resultados if r == -1)
    empates = sum(1 for r in resultados if r == 0)
    
    print(f"\n📊 Resultados:")
    print(f"   Victorias: {victorias} ({victorias/n_partidas*100:.1f}%)")
    print(f"   Derrotas:  {derrotas} ({derrotas/n_partidas*100:.1f}%)")
    print(f"   Empates:   {empates} ({empates/n_partidas*100:.1f}%)")
    print(f"   Tasa:      {victorias/n_partidas:.3f}")
    
    if metricas:
        tiempos = [m['tiempo'] for m in metricas if m['tiempo'] > 0]
        nodos_exp = [m['nodos_expandidos'] for m in metricas]
        nodos_pod = [m['nodos_podados'] for m in metricas]
        
        print(f"\n⏱️ Tiempos del agente1:")
        print(f"   Media: {statistics.mean(tiempos):.4f}s" if tiempos else "   No disponible")
        print(f"   Desv:  {statistics.stdev(tiempos):.4f}s" if len(tiempos) > 1 else "   No disponible")
        print(f"   Min:   {min(tiempos):.4f}s" if tiempos else "   No disponible")
        print(f"   Max:   {max(tiempos):.4f}s" if tiempos else "   No disponible")
        
        print(f"\n🌳 Nodos expandidos (media): {statistics.mean(nodos_exp):.0f}")
        print(f"✂️ Nodos podados (media):     {statistics.mean(nodos_pod):.0f}")
        print(f"📊 Tasa de poda:              {statistics.mean(nodos_pod)/max(1, statistics.mean(nodos_exp))*100:.1f}%")
    
    return resultados, metricas