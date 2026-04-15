import random
import copy
import json
import time
import statistics
import math
import matplotlib.pyplot as plt
from collections import namedtuple
from AgenteIA.Agente import Juego, Agente
from AgenteIA.AgenteJugador import AgenteJugador

# ============================================================================
# PARTE 1: REGLAS DEL JUEGO
# ============================================================================

class Othello(Juego):
    """Clase que contiene las reglas y el estado del juego Othello"""

    DIRECCIONES = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]

    # Tabla de pesos posicionales (mejora la evaluación)
    TABLA_PESOS = [
        [ 4.0, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  4.0],
        [-0.5, -1.0, -0.2, -0.2, -0.2, -0.2, -1.0, -0.5],
        [ 0.5, -0.2,  0.3,  0.1,  0.1,  0.3, -0.2,  0.5],
        [ 0.5, -0.2,  0.1,  0.0,  0.0,  0.1, -0.2,  0.5],
        [ 0.5, -0.2,  0.1,  0.0,  0.0,  0.1, -0.2,  0.5],
        [ 0.5, -0.2,  0.3,  0.1,  0.1,  0.3, -0.2,  0.5],
        [-0.5, -1.0, -0.2, -0.2, -0.2, -0.2, -1.0, -0.5],
        [ 4.0, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  4.0]
    ]

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
    # IMPLEMENTACIÓN DE LA INTERFAZ JUEGO (REQUERIDA POR LA CONSIGNA)
    # =====================================================================

    def estado_inicial(self):
        """Retorna un nuevo juego en estado inicial"""
        return Othello()

    def jugadas_legales(self, estado=None, jugador=None):
        """Retorna movimientos legales para un estado y jugador"""
        juego = estado if estado is not None else self
        return juego.obtener_movimientos_legales(jugador)

    def aplicar_jugada(self, estado, jugada, jugador):
        """Retorna nuevo estado después de aplicar la jugada"""
        nuevo = estado.copiar()
        nuevo.aplicar_movimiento(jugada[0], jugada[1], jugador)
        return nuevo

    def es_estado_terminal(self, estado):
        """Verifica si el estado es terminal"""
        return estado.es_terminal()

    def resultado_estado(self, estado):
        """Retorna 1 si gana MAX (Negras), -1 si gana MIN (Blancas), 0 empate"""
        return estado.obtener_resultado()


# ============================================================================
# PARTE 2: FUNCIÓN DE EVALUACIÓN CON PESOS (MEJORADA)
# ============================================================================

class OthelloEvaluacion:
    # Pesos MANUALES originales (oponente base para AG)
    PESOS_MANUALES = [0.25, 0.40, 2.80, 0.15, 0.40]
    
    # Pesos OPTIMIZADOS (para competir)
    PESOS_DEFECTO = [0.137, 0.316, 0.017, 0.124, 0.406]  # ← tus pesos AG

    def __init__(self, pesos=None):
        if pesos is None:
            self.pesos = self.PESOS_DEFECTO.copy()
        else:
            # Si vienen 4 pesos del AG antiguo, adaptar a 5
            if len(pesos) == 4:
                self.pesos = pesos + [0.30]  # agregar peso posicional
            else:
                self.pesos = pesos.copy()

    def diferencia_fichas(self, juego, jugador_max='N'):
        """Diferencia de fichas normalizada [-1, 1]"""
        negras, blancas = juego.contar_fichas()
        total = negras + blancas
        if total == 0:
            return 0
        if jugador_max == 'N':
            return (negras - blancas) / 64.0
        else:
            return (blancas - negras) / 64.0

    def movilidad(self, juego, jugador_max='N'):
        """Diferencia de movilidad normalizada [-1, 1]"""
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        total = mov_max + mov_min
        if total == 0:
            return 0
        return (mov_max - mov_min) / 64.0

    def control_esquinas(self, juego, jugador_max='N'):
        """Control de esquinas (muy importante en Othello)"""
        esquinas = [(0, 0), (0, 7), (7, 0), (7, 7)]
        valor_max = 0
        valor_min = 0
        for f, c in esquinas:
            if juego.tablero[f][c] == jugador_max:
                valor_max += 1
            elif juego.tablero[f][c] != '.':
                valor_min += 1
        return (valor_max - valor_min) / 4.0

    def paridad(self, juego, jugador_max='N'):
        """Paridad: quien juega último tiene ventaja"""
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        total = mov_max + mov_min
        
        # Solo importa en juego temprano/medio
        negras, blancas = juego.contar_fichas()
        if negras + blancas < 50:
            if total % 2 == 0:
                return 0.2 if mov_max > mov_min else -0.2
            else:
                return -0.2 if mov_max > mov_min else 0.2
        return 0

    def evaluacion_posicional(self, juego, jugador_max='N'):
        """Evaluación basada en tabla de pesos posicionales"""
        valor = 0
        for i in range(8):
            for j in range(8):
                if juego.tablero[i][j] == jugador_max:
                    valor += Othello.TABLA_PESOS[i][j]
                elif juego.tablero[i][j] != '.':
                    valor -= Othello.TABLA_PESOS[i][j]
        # Normalizar a rango [-1, 1]
        max_posible = sum(abs(Othello.TABLA_PESOS[i][j]) for i in range(8) for j in range(8))
        if max_posible > 0:
            return valor / max_posible
        return 0

    def evaluar(self, juego, jugador_max='N'):
        """Función de evaluación completa con 5 características"""
        # Si es terminal, retornar resultado definitivo
        if juego.es_terminal():
            resultado = juego.obtener_resultado()
            if resultado == 1 and jugador_max == 'N':
                return 100.0
            elif resultado == -1 and jugador_max == 'B':
                return 100.0
            elif resultado == -1:
                return -100.0
            elif resultado == 1:
                return -100.0
            return 0.0

        # Calcular características
        f1 = self.diferencia_fichas(juego, jugador_max)
        f2 = self.movilidad(juego, jugador_max)
        f3 = self.control_esquinas(juego, jugador_max)
        f4 = self.paridad(juego, jugador_max)
        f5 = self.evaluacion_posicional(juego, jugador_max)

        valores = [f1, f2, f3, f4, f5]
        
        # Asegurar que los pesos coinciden en longitud
        pesos_ajustados = self.pesos[:len(valores)]
        while len(pesos_ajustados) < len(valores):
            pesos_ajustados.append(0.1)
        
        return sum(p * v for p, v in zip(pesos_ajustados, valores))


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
        self.ordenar_movimientos = True  # Activar ordenamiento para mejor poda

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
        if resultado == 1:
            return 100.0 if self.jugador == 'N' else -100.0
        elif resultado == -1:
            return 100.0 if self.jugador == 'B' else -100.0
        return 0.0

    def _obtener_movimientos(self, estado: ElEstadoOthello):
        juego = self._estado_a_juego(estado)
        return juego.obtener_movimientos_legales(estado.jugador)

    def _ordenar_movimientos_por_valor(self, estado, movimientos, es_max):
        """Ordena movimientos para mejorar la poda alfa-beta"""
        if not self.ordenar_movimientos or len(movimientos) <= 1:
            return movimientos
        
        # Evaluación rápida de cada movimiento
        valores = []
        juego_base = self._estado_a_juego(estado)
        
        for mov in movimientos:
            juego_temp = juego_base.copiar()
            juego_temp.aplicar_movimiento(mov[0], mov[1], estado.jugador)
            valor = self.evaluacion.evaluar(juego_temp, self.jugador)
            valores.append((mov, valor))
        
        # Ordenar: mayores primero si es MAX, menores primero si es MIN
        valores.sort(key=lambda x: x[1], reverse=es_max)
        return [v[0] for v in valores]

    def _aplicar_movimiento(self, estado: ElEstadoOthello, movimiento):
        juego = self._estado_a_juego(estado)
        juego.aplicar_movimiento(movimiento[0], movimiento[1], estado.jugador)
        return self._juego_a_estado(juego)

    def _pasar_turno(self, estado: ElEstadoOthello) -> ElEstadoOthello:
        """Pasa el turno al oponente sin cambiar el tablero"""
        oponente = 'B' if estado.jugador == 'N' else 'N'
        return ElEstadoOthello(
            jugador=oponente,
            tablero=estado.tablero,
            movidas=[]
        )

    def _minimax_alfa_beta(self, estado: ElEstadoOthello, profundidad, alfa, beta, es_max):
        self.nodos_expandidos += 1

        if profundidad == 0 or self._es_terminal(estado):
            return self.FunEval(estado), None

        movimientos = self._obtener_movimientos(estado)
        
        # Si no hay movimientos, pasar turno
        if not movimientos:
            nuevo_estado = self._pasar_turno(estado)
            valor, _ = self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, not es_max)
            return valor, None

        # Ordenar movimientos para mejor poda
        movimientos = self._ordenar_movimientos_por_valor(estado, movimientos, es_max)
        mejor_movimiento = movimientos[0]

        if es_max:
            valor = float('-inf')
            for i, mov in enumerate(movimientos):
                nuevo_estado = self._aplicar_movimiento(estado, mov)
                valor_hijo, _ = self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, False)
                
                if valor_hijo > valor:
                    valor = valor_hijo
                    mejor_movimiento = mov
                
                alfa = max(alfa, valor)
                if alfa >= beta:
                    self.nodos_podados += len(movimientos) - (i + 1)
                    break
            return valor, mejor_movimiento
        else:
            valor = float('inf')
            for i, mov in enumerate(movimientos):
                nuevo_estado = self._aplicar_movimiento(estado, mov)
                valor_hijo, _ = self._minimax_alfa_beta(nuevo_estado, profundidad - 1, alfa, beta, True)
                
                if valor_hijo < valor:
                    valor = valor_hijo
                    mejor_movimiento = mov
                
                beta = min(beta, valor)
                if alfa >= beta:
                    self.nodos_podados += len(movimientos) - (i + 1)
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

        return movimiento
    
    def obtener_metricas(self):
        return {
            "nodos_expandidos": self.nodos_expandidos,
            "nodos_podados": self.nodos_podados,
            "tiempo": self.tiempo_ultima_jugada,
            "profundidad": self.profundidad_maxima
        }


# ============================================================================
# PARTE 4: AGENTE ALEATORIO (PARA COMPARATIVAS)
# ============================================================================

class OthelloAleatorio(AgenteJugador):
    """Agente que selecciona movimientos aleatoriamente (baseline)"""

    def __init__(self, jugador='N'):
        AgenteJugador.__init__(self)
        self.jugador = jugador

    def seleccionar_movimiento(self, juego: Othello):
        movimientos = juego.obtener_movimientos_legales(self.jugador)
        if movimientos:
            return random.choice(movimientos)
        return None

    def obtener_metricas(self):
        return {
            "nodos_expandidos": 0,
            "nodos_podados": 0,
            "tiempo": 0,
            "profundidad": 0
        }


# ============================================================================
# PARTE 5: ALGORITMO GENÉTICO (CORREGIDO Y MEJORADO)
# ============================================================================

class OthelloGenetico:
    def __init__(self, tam_poblacion=30, generaciones=20, profundidad=3, partidas_por_fitness=15):
        random.seed(42)
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.profundidad = profundidad
        self.partidas_por_fitness = partidas_por_fitness  # Ya no se fuerza a 20
        self.poblacion = []
        self.mejor_historial = []
        self.promedio_historial = []
        self.mejor_individuo_global = None
        self.mejor_fitness_global = -1

    def _crear_individuo(self):
        """Crea un individuo con 5 pesos (ahora incluye posicional)"""
        return [random.uniform(0, 2) for _ in range(5)]

    def _normalizar_pesos(self, individuo):
        """
        Normaliza los pesos para que sumen 1 (corregido)
        Esto mantiene la magnitud relativa de las características
        """
        total = sum(individuo)
        if total > 0:
            return [w / total for w in individuo]
        # Si todos son cero, devolver pesos uniformes
        return [1.0 / len(individuo) for _ in range(len(individuo))]

    def _jugar_partida(self, agente1, agente2):
        """Juega una partida completa entre dos agentes"""
        juego = Othello()
        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            agente = agente1 if jugador_actual == agente1.jugador else agente2
            mov = agente.seleccionar_movimiento(juego)
            if mov is not None:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                # Pasar turno
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultado = juego.obtener_resultado()
        # Retornar 1 si gana agente1, 0 si empate, -1 si pierde
        if resultado == 1 and agente1.jugador == 'N':
            return 1
        elif resultado == -1 and agente1.jugador == 'B':
            return 1
        elif resultado == 0:
            return 0
        else:
            return -1

    def _calcular_fitness(self, individuo):
        """Calcula el fitness de un individuo enfrentándolo a pesos fijos"""
        pesos = self._normalizar_pesos(individuo)
        victorias = 0

        for i in range(self.partidas_por_fitness):
            # Alternar colores para evitar sesgo
            if i % 2 == 0:
                agente_prueba = OthelloAgente(profundidad=self.profundidad, pesos=pesos, jugador='N')
                agente_base = OthelloAgente(profundidad=self.profundidad,
                                            pesos=OthelloEvaluacion.PESOS_MANUALES, jugador='B')
            else:
                agente_prueba = OthelloAgente(profundidad=self.profundidad, pesos=pesos, jugador='B')
                agente_base = OthelloAgente(profundidad=self.profundidad,
                                           pesos=OthelloEvaluacion.PESOS_MANUALES, jugador='N')

            resultado = self._jugar_partida(agente_prueba, agente_base)
            if resultado == 1:
                victorias += 1
            elif resultado == 0:
                victorias += 0.5

        return victorias / self.partidas_por_fitness

    def _seleccion_torneo(self, fitnesses, k=3):
        """Selección por torneo (k competidores)"""
        mejor_idx, mejor_fitness = None, -1
        for _ in range(k):
            idx = random.randint(0, len(self.poblacion) - 1)
            if fitnesses[idx] > mejor_fitness:
                mejor_fitness = fitnesses[idx]
                mejor_idx = idx
        return self.poblacion[mejor_idx]

    def _cruce_blx(self, padre1, padre2, alpha=0.5):
        """Cruce BLX-α (Breeder Genetic Algorithm)"""
        hijo = []
        for i in range(len(padre1)):
            min_val = min(padre1[i], padre2[i])
            max_val = max(padre1[i], padre2[i])
            rango = max_val - min_val
            # Extender el rango en alpha
            hijo.append(random.uniform(min_val - alpha * rango, max_val + alpha * rango))
        return hijo

    def _mutacion_gaussiana(self, individuo, tasa=0.2, sigma=0.2):
        """Mutación con ruido gaussiano (sigma reducido para mejor convergencia)"""
        for i in range(len(individuo)):
            if random.random() < tasa:
                individuo[i] = max(0.01, min(3.0, individuo[i] + random.gauss(0, sigma)))
        return individuo

    def evolucionar(self, verbose=True):
        """Ejecuta el algoritmo genético completo"""
        self.poblacion = [self._crear_individuo() for _ in range(self.tam_poblacion)]

        for gen in range(self.generaciones):
            # Calcular fitness de toda la población
            fitnesses = [self._calcular_fitness(ind) for ind in self.poblacion]

            mejor_fitness = max(fitnesses)
            mejor_ind = self.poblacion[fitnesses.index(mejor_fitness)]
            promedio_fitness = sum(fitnesses) / len(fitnesses)

            # Actualizar mejor global
            if mejor_fitness > self.mejor_fitness_global:
                self.mejor_fitness_global = mejor_fitness
                self.mejor_individuo_global = mejor_ind.copy()

            # Guardar historial
            self.mejor_historial.append(mejor_fitness)
            self.promedio_historial.append(promedio_fitness)

            if verbose:
                pesos_norm = self._normalizar_pesos(mejor_ind)
                print(f"Gen {gen+1:3d} | Mejor: {mejor_fitness:.4f} | "
                      f"Promedio: {promedio_fitness:.4f} | "
                      f"Pesos: {[round(w, 3) for w in pesos_norm]}")

            # Crear nueva población (élite + cruce)
            nueva_poblacion = [mejor_ind.copy()]  # Elitismo: mantener el mejor
            
            while len(nueva_poblacion) < self.tam_poblacion:
                padre1 = self._seleccion_torneo(fitnesses)
                padre2 = self._seleccion_torneo(fitnesses)
                hijo = self._cruce_blx(padre1, padre2)
                hijo = self._mutacion_gaussiana(hijo)
                nueva_poblacion.append(hijo)

            self.poblacion = nueva_poblacion

        # Normalizar los mejores pesos finales
        mejores_pesos = self._normalizar_pesos(self.mejor_individuo_global)

        if verbose:
            print(f"\n✅ Mejores pesos globales: {[round(w, 3) for w in mejores_pesos]}")
            print(f"   Fitness: {self.mejor_fitness_global:.4f}")
            print(f"   Significado: [fichas, movilidad, esquinas, paridad, posicional]")

        return mejores_pesos, self.mejor_historial, self.promedio_historial

    def guardar_pesos(self, pesos, archivo='mejores_pesos_othello.json'):
        """Guarda los pesos en un archivo JSON"""
        with open(archivo, 'w') as f:
            json.dump({'pesos': pesos, 'fitness': self.mejor_fitness_global}, f, indent=2)
        print(f"💾 Pesos guardados en '{archivo}'")

    def cargar_pesos(self, archivo='mejores_pesos_othello.json'):
        """Carga los pesos desde un archivo JSON"""
        with open(archivo, 'r') as f:
            data = json.load(f)
        print(f"📂 Pesos cargados desde '{archivo}': {data['pesos']}")
        if 'fitness' in data:
            print(f"   Fitness asociado: {data['fitness']:.4f}")
        return data['pesos']

    def graficar_convergencia(self, archivo='convergencia_othello.png', mostrar=True):
        """Genera y guarda la gráfica de convergencia"""
        if not self.mejor_historial:
            print("No hay datos de evolución. Ejecuta evolucionar() primero.")
            return

        plt.figure(figsize=(12, 6))
        plt.plot(self.mejor_historial, label='Mejor fitness', color='blue', linewidth=2, marker='o')
        plt.plot(self.promedio_historial, label='Fitness promedio', color='orange', linewidth=2, linestyle='--', marker='s')
        plt.xlabel('Generación', fontsize=12)
        plt.ylabel('Fitness (tasa de victorias)', fontsize=12)
        plt.title('Convergencia del Algoritmo Genético — Othello', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(archivo, dpi=150)
        print(f"📊 Gráfica guardada en '{archivo}'")
        
        if mostrar:
            try:
                plt.show()
            except:
                print("   (No se pudo mostrar la gráfica, pero se guardó correctamente)")


# ============================================================================
# PARTE 6: FUNCIONES DE EXPERIMENTACIÓN (MEJORADAS)
# ============================================================================

def jugar_partidas(agente1, agente2, n=20, verbose=False):
    """
    Juega n partidas entre dos agentes.
    Alterna quién empieza para evitar sesgo.
    """
    resultados = []
    metricas_agente1 = []

    for i in range(n):
        juego = Othello()
        
        # Alternar quién empieza
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
                # Pasar turno
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultados.append(juego.obtener_resultado())
        
        if hasattr(agente1, 'obtener_metricas'):
            metricas_agente1.append(agente1.obtener_metricas())
        
        if verbose and (i + 1) % 10 == 0:
            print(f"  Partidas completadas: {i+1}/{n}")

    return resultados, metricas_agente1


def intervalo_confianza(data, confianza=0.95):
    """Calcula intervalo de confianza para una lista de resultados"""
    n = len(data)
    if n == 0:
        return (0, 0)
    media = sum(data) / n
    if n == 1:
        return (media, media)
    desv = (sum((x - media) ** 2 for x in data) / (n - 1)) ** 0.5
    # Aproximación normal para proporciones (95% = 1.96)
    z = 1.96
    error = z * (desv / (n ** 0.5))
    return (media - error, media + error)


def comparar_agentes(agente1, agente2, n_partidas=20, verbose=True):
    """Compara dos agentes y muestra estadísticas completas"""
    print(f"\n{'='*70}")
    print(f"Comparando: {agente1.__class__.__name__} (prof={agente1.profundidad_maxima}) vs "
          f"{agente2.__class__.__name__} (prof={agente2.profundidad_maxima})")
    print(f"Partidas: {n_partidas}")
    print(f"{'='*70}")

    resultados, metricas = jugar_partidas(agente1, agente2, n_partidas, verbose)
    
    victorias = sum(1 for r in resultados if r == 1)
    derrotas = sum(1 for r in resultados if r == -1)
    empates = sum(1 for r in resultados if r == 0)
    
    tasa_victoria = victorias / n_partidas
    
    print(f"\n📊 Resultados:")
    print(f"   Victorias: {victorias} ({tasa_victoria*100:.1f}%)")
    print(f"   Derrotas:  {derrotas} ({derrotas/n_partidas*100:.1f}%)")
    print(f"   Empates:   {empates} ({empates/n_partidas*100:.1f}%)")
    
    # Intervalo de confianza
    resultados_binarios = [1 if r == 1 else 0 for r in resultados]
    ic_inf, ic_sup = intervalo_confianza(resultados_binarios)
    print(f"\n📈 Intervalo de confianza 95% para tasa de victoria:")
    print(f"   [{ic_inf:.3f}, {ic_sup:.3f}]")
    
    if metricas:
        tiempos = [m['tiempo'] for m in metricas if m['tiempo'] > 0]
        nodos_exp = [m['nodos_expandidos'] for m in metricas]
        nodos_pod = [m['nodos_podados'] for m in metricas]
        
        if tiempos:
            print(f"\n⏱️ Tiempos del agente1:")
            print(f"   Media: {statistics.mean(tiempos):.4f}s")
            if len(tiempos) > 1:
                print(f"   Desv:  {statistics.stdev(tiempos):.4f}s")
            print(f"   Min:   {min(tiempos):.4f}s")
            print(f"   Max:   {max(tiempos):.4f}s")
        
        if nodos_exp:
            media_exp = statistics.mean(nodos_exp)
            media_pod = statistics.mean(nodos_pod) if nodos_pod else 0
            print(f"\n🌳 Nodos expandidos (media): {media_exp:.0f}")
            print(f"✂️ Nodos podados (media):     {media_pod:.0f}")
            if media_exp > 0:
                print(f"📊 Tasa de poda: {media_pod/media_exp*100:.1f}%")
    
    return resultados, metricas
