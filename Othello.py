"""
Othello (Reversi) - Implementación completa
Incluye: reglas, evaluación, minimax con poda alfa-beta y algoritmo genético
"""

import random
import copy
from collections import deque

# ============================================================================
# PARTE 1: REGLAS DEL JUEGO
# ============================================================================

class Othello:
    """Clase que contiene las reglas y el estado del juego Othello"""
    
    # Direcciones para voltear fichas: 8 direcciones (filas, columnas)
    DIRECCIONES = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]
    
    def __init__(self):
        """Inicializa el tablero en la posición inicial"""
        self.tablero = self._crear_tablero_inicial()
        self.jugador_actual = 'N'  # 'N' = negras (MAX), 'B' = blancas (MIN)
        self.ultimo_movimiento = None
    
    def _crear_tablero_inicial(self):
        """Crea el tablero 8x8 con las 4 fichas iniciales"""
        tablero = [['.' for _ in range(8)] for _ in range(8)]
        # Posiciones iniciales: negras (N) en (3,3) y (4,4); blancas (B) en (3,4) y (4,3)
        tablero[3][3] = 'N'
        tablero[4][4] = 'N'
        tablero[3][4] = 'B'
        tablero[4][3] = 'B'
        return tablero
    
    def mostrar(self):
        """Imprime el tablero por consola"""
        print("   0 1 2 3 4 5 6 7")
        for i in range(8):
            print(f"{i}  ", end="")
            for j in range(8):
                print(self.tablero[i][j], end=" ")
            print()
        print(f"Turno: {'Negras (MAX)' if self.jugador_actual == 'N' else 'Blancas (MIN)'}")
    
    def es_dentro_tablero(self, fila, col):
        """Verifica si una posición está dentro del tablero"""
        return 0 <= fila < 8 and 0 <= col < 8
    
    def es_movimiento_legal(self, fila, col, jugador):
        """Verifica si colocar una ficha en (fila, col) es un movimiento legal"""
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
        """Retorna una lista de todos los movimientos legales para un jugador"""
        if jugador is None:
            jugador = self.jugador_actual
        
        movimientos = []
        for i in range(8):
            for j in range(8):
                if self.es_movimiento_legal(i, j, jugador):
                    movimientos.append((i, j))
        return movimientos
    
    def aplicar_movimiento(self, fila, col, jugador=None):
        """
        Aplica un movimiento en el tablero y voltea las fichas correspondientes.
        Retorna True si fue exitoso, False si no es legal.
        """
        if jugador is None:
            jugador = self.jugador_actual
        
        if not self.es_movimiento_legal(fila, col, jugador):
            return False
        
        # Colocar la ficha
        self.tablero[fila][col] = jugador
        oponente = 'B' if jugador == 'N' else 'N'
        
        # Voltear fichas en todas las direcciones
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
        
        # Cambiar turno
        self.jugador_actual = oponente
        self.ultimo_movimiento = (fila, col)
        
        # Si el oponente no tiene movimientos, se queda el mismo jugador
        if len(self.obtener_movimientos_legales()) == 0:
            self.jugador_actual = jugador
        
        return True
    
    def es_terminal(self):
        """Verifica si el juego ha terminado (sin movimientos para ambos)"""
        tiene_N = len(self.obtener_movimientos_legales('N')) > 0
        tiene_B = len(self.obtener_movimientos_legales('B')) > 0
        return not (tiene_N or tiene_B)
    
    def obtener_resultado(self):
        """
        Retorna el resultado desde la perspectiva de MAX (negras):
        +1 si ganan negras, -1 si ganan blancas, 0 si empate
        """
        if not self.es_terminal():
            return 0
        
        negras = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'N')
        blancas = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'B')
        
        if negras > blancas:
            return 1
        elif blancas > negras:
            return -1
        else:
            return 0
    
    def copiar(self):
        """Crea una copia profunda del estado actual"""
        nuevo = Othello()
        nuevo.tablero = copy.deepcopy(self.tablero)
        nuevo.jugador_actual = self.jugador_actual
        nuevo.ultimo_movimiento = self.ultimo_movimiento
        return nuevo
    
    def contar_fichas(self):
        """Retorna (negras, blancas)"""
        negras = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'N')
        blancas = sum(1 for i in range(8) for j in range(8) if self.tablero[i][j] == 'B')
        return negras, blancas


# ============================================================================
# PARTE 2: FUNCIÓN DE EVALUACIÓN CON PESOS
# ============================================================================

class OthelloEvaluacion:
    """
    Función de evaluación lineal: E(s) = w1*f1 + w2*f2 + w3*f3 + w4*f4
    f1: Diferencia de fichas
    f2: Movilidad (diferencia de movimientos posibles)
    f3: Control de esquinas
    f4: Paridad (oportunidad de último movimiento)
    """
    
    # Pesos por defecto (heurísticos manuales)
    PESOS_DEFECTO = [1.0, 0.5, 2.0, 0.3]
    
    # Matriz de valor de posiciones (para bonus adicional opcional)
    TABLA_POSICIONES = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -30, -2, -2, -2, -2, -30, -20],
        [10, -2, 1, 1, 1, 1, -2, 10],
        [5, -2, 1, 1, 1, 1, -2, 5],
        [5, -2, 1, 1, 1, 1, -2, 5],
        [10, -2, 1, 1, 1, 1, -2, 10],
        [-20, -30, -2, -2, -2, -2, -30, -20],
        [100, -20, 10, 5, 5, 10, -20, 100]
    ]
    
    def __init__(self, pesos=None):
        self.pesos = pesos if pesos is not None else self.PESOS_DEFECTO.copy()
    
    def diferencia_fichas(self, juego, jugador_max='N'):
        """f1: Diferencia de fichas (MAX - MIN) normalizada"""
        negras, blancas = juego.contar_fichas()
        total = negras + blancas
        if total == 0:
            return 0
        if jugador_max == 'N':
            return (negras - blancas) / 64.0
        else:
            return (blancas - negras) / 64.0
    
    def movilidad(self, juego, jugador_max='N'):
        """f2: Diferencia de movimientos posibles (MAX - MIN) normalizada"""
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        total = mov_max + mov_min
        if total == 0:
            return 0
        return (mov_max - mov_min) / 64.0
    
    def control_esquinas(self, juego, jugador_max='N'):
        """f3: Control de esquinas (las esquinas son muy valiosas)"""
        esquinas = [(0,0), (0,7), (7,0), (7,7)]
        valor_max = 0
        valor_min = 0
        
        for (f,c) in esquinas:
            if juego.tablero[f][c] == jugador_max:
                valor_max += 1
            elif juego.tablero[f][c] != '.':
                valor_min += 1
        
        return (valor_max - valor_min) / 4.0
    
    def paridad(self, juego, jugador_max='N'):
        """f4: Paridad - beneficio para quien juega último"""
        mov_max = len(juego.obtener_movimientos_legales(jugador_max))
        mov_min = len(juego.obtener_movimientos_legales('B' if jugador_max == 'N' else 'N'))
        
        # Si hay pocos movimientos restantes, la paridad importa
        total_movimientos = mov_max + mov_min
        if total_movimientos <= 10:
            # El que juega último tiene ventaja
            if total_movimientos % 2 == 0:
                return 0.5 if mov_max > mov_min else -0.5
            else:
                return -0.5 if mov_max > mov_min else 0.5
        return 0
    
    def evaluar(self, juego, jugador_max='N'):
        """
        Calcula el valor del estado actual usando la combinación lineal de pesos
        """
        if juego.es_terminal():
            resultado = juego.obtener_resultado()
            if jugador_max == 'N':
                return resultado
            else:
                return -resultado
        
        f1 = self.diferencia_fichas(juego, jugador_max)
        f2 = self.movilidad(juego, jugador_max)
        f3 = self.control_esquinas(juego, jugador_max)
        f4 = self.paridad(juego, jugador_max)
        
        caracteristicas = [f1, f2, f3, f4]
        
        valor = sum(p * c for p, c in zip(self.pesos, caracteristicas))
        
        # Bonus opcional: valor posicional (puedes activarlo si quieres)
        # valor += self._bonus_posicional(juego, jugador_max) * 0.01
        
        return valor
    
    def _bonus_posicional(self, juego, jugador_max='N'):
        """Bonus opcional basado en la tabla de posiciones"""
        bonus = 0
        for i in range(8):
            for j in range(8):
                if juego.tablero[i][j] == jugador_max:
                    bonus += self.TABLA_POSICIONES[i][j]
                elif juego.tablero[i][j] != '.':
                    bonus -= self.TABLA_POSICIONES[i][j]
        return bonus / 1000.0


# ============================================================================
# PARTE 3: MINIMAX CON PODA ALFA-BETA
# ============================================================================

class OthelloAgente:
    """Agente que usa Minimax con poda Alfa-Beta para decidir movimientos"""
    
    def __init__(self, profundidad=4, pesos=None, jugador='N'):
        self.profundidad = profundidad
        self.evaluacion = OthelloEvaluacion(pesos)
        self.jugador = jugador  # 'N' o 'B'
    
    def alfa_beta(self, juego, profundidad, alpha, beta, es_maximizador):
        """
        Algoritmo Minimax con poda Alfa-Beta
        Retorna (valor, mejor_movimiento)
        """
        if profundidad == 0 or juego.es_terminal():
            return self.evaluacion.evaluar(juego, self.jugador), None
        
        jugador_actual = self.jugador if es_maximizador else ('B' if self.jugador == 'N' else 'N')
        movimientos = juego.obtener_movimientos_legales(jugador_actual)
        
        if not movimientos:
            # Si no hay movimientos, pasar turno
            juego_copia = juego.copiar()
            juego_copia.jugador_actual = 'B' if jugador_actual == 'N' else 'N'
            valor, _ = self.alfa_beta(juego_copia, profundidad - 1, alpha, beta, not es_maximizador)
            return valor, None
        
        if es_maximizador:
            mejor_valor = -float('inf')
            mejor_mov = None
            for mov in movimientos:
                juego_copia = juego.copiar()
                juego_copia.aplicar_movimiento(mov[0], mov[1], jugador_actual)
                valor, _ = self.alfa_beta(juego_copia, profundidad - 1, alpha, beta, False)
                
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_mov = mov
                
                alpha = max(alpha, valor)
                if beta <= alpha:
                    break  # Poda
            return mejor_valor, mejor_mov
        else:
            mejor_valor = float('inf')
            mejor_mov = None
            for mov in movimientos:
                juego_copia = juego.copiar()
                juego_copia.aplicar_movimiento(mov[0], mov[1], jugador_actual)
                valor, _ = self.alfa_beta(juego_copia, profundidad - 1, alpha, beta, True)
                
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_mov = mov
                
                beta = min(beta, valor)
                if beta <= alpha:
                    break  # Poda
            return mejor_valor, mejor_mov
    
    def seleccionar_movimiento(self, juego):
        """Selecciona el mejor movimiento dado el estado actual del juego"""
        _, mejor_mov = self.alfa_beta(juego, self.profundidad, -float('inf'), float('inf'), True)
        return mejor_mov


# ============================================================================
# PARTE 4: ALGORITMO GENÉTICO PARA OPTIMIZAR PESOS
# ============================================================================

class OthelloGenetico:
    """
    Algoritmo Genético para optimizar los pesos de la función de evaluación
    """
    
    def __init__(self, tam_poblacion=30, generaciones=20, profundidad=3, partidas_por_fitness=20):
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.profundidad = profundidad
        self.partidas_por_fitness = partidas_por_fitness
        self.poblacion = []
        self.mejor_historial = []
        self.promedio_historial = []
    
    def _crear_individuo(self):
        """Crea un individuo (vector de pesos) aleatorio"""
        # Pesos iniciales aleatorios entre 0 y 2
        return [random.uniform(0, 2) for _ in range(4)]
    
    def _normalizar_pesos(self, individuo):
        """Normaliza los pesos para que sumen 4 (opcional)"""
        total = sum(individuo)
        if total > 0:
            return [w * 4.0 / total for w in individuo]
        return [1.0, 1.0, 1.0, 1.0]
    
    def _jugar_partida(self, agente1, agente2):
        """
        Juega una partida entre dos agentes
        Retorna: 1 si gana agente1, -1 si gana agente2, 0 empate
        """
        juego = Othello()
        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            if jugador_actual == agente1.jugador:
                mov = agente1.seleccionar_movimiento(juego)
            else:
                mov = agente2.seleccionar_movimiento(juego)
            
            if mov is not None:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                # Pasar turno si no hay movimiento
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
        """
        Calcula el fitness de un individuo enfrentándolo contra un oponente base
        (en este caso, un agente con pesos manuales)
        """
        pesos = self._normalizar_pesos(individuo)
        
        agente_prueba = OthelloAgente(profundidad=self.profundidad, pesos=pesos, jugador='N')
        agente_base = OthelloAgente(profundidad=self.profundidad, pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='B')
        
        victorias = 0
        for _ in range(self.partidas_por_fitness):
            resultado = self._jugar_partida(agente_prueba, agente_base)
            if resultado == 1:
                victorias += 1
            elif resultado == 0:
                victorias += 0.5
        
        return victorias / self.partidas_por_fitness
    
    def _seleccion_torneo(self, fitnesses, k=3):
        """Selección por torneo"""
        mejor_idx = None
        mejor_fitness = -1
        
        for _ in range(k):
            idx = random.randint(0, len(self.poblacion) - 1)
            if fitnesses[idx] > mejor_fitness:
                mejor_fitness = fitnesses[idx]
                mejor_idx = idx
        
        return self.poblacion[mejor_idx]
    
    def _cruce_blx(self, padre1, padre2, alpha=0.5):
        """
        Cruce BLX-α (Blend Crossover)
        """
        hijo = []
        for i in range(len(padre1)):
            min_val = min(padre1[i], padre2[i])
            max_val = max(padre1[i], padre2[i])
            rango = max_val - min_val
            low = min_val - alpha * rango
            high = max_val + alpha * rango
            hijo.append(random.uniform(low, high))
        return hijo
    
    def _mutacion_gaussiana(self, individuo, tasa=0.2, sigma=0.3):
        """Mutación con ruido gaussiano"""
        for i in range(len(individuo)):
            if random.random() < tasa:
                individuo[i] += random.gauss(0, sigma)
                # Mantener en rango razonable
                individuo[i] = max(0.1, min(3.0, individuo[i]))
        return individuo
    
    def evolucionar(self, verbose=True):
        """Ejecuta el algoritmo genético completo"""
        # Inicializar población
        self.poblacion = [self._crear_individuo() for _ in range(self.tam_poblacion)]
        
        for gen in range(self.generaciones):
            # Calcular fitness
            fitnesses = [self._calcular_fitness(ind) for ind in self.poblacion]
            
            mejor_fitness = max(fitnesses)
            mejor_ind = self.poblacion[fitnesses.index(mejor_fitness)]
            promedio_fitness = sum(fitnesses) / len(fitnesses)
            
            self.mejor_historial.append(mejor_fitness)
            self.promedio_historial.append(promedio_fitness)
            
            if verbose:
                print(f"Gen {gen+1:3d} | Mejor fitness: {mejor_fitness:.4f} | Promedio: {promedio_fitness:.4f} | Mejor pesos: {[round(w,2) for w in mejor_ind]}")
            
            # Nueva población
            nueva_poblacion = []
            
            # Elitismo: mantener al mejor individuo
            nueva_poblacion.append(mejor_ind)
            
            while len(nueva_poblacion) < self.tam_poblacion:
                # Selección
                padre1 = self._seleccion_torneo(fitnesses)
                padre2 = self._seleccion_torneo(fitnesses)
                
                # Cruce
                hijo = self._cruce_blx(padre1, padre2)
                
                # Mutación
                hijo = self._mutacion_gaussiana(hijo)
                
                nueva_poblacion.append(hijo)
            
            self.poblacion = nueva_poblacion
        
        # Retornar el mejor individuo encontrado
        fitnesses_final = [self._calcular_fitness(ind) for ind in self.poblacion]
        mejor_idx = fitnesses_final.index(max(fitnesses_final))
        mejores_pesos = self._normalizar_pesos(self.poblacion[mejor_idx])
        
        if verbose:
            print(f"\n✅ Mejores pesos encontrados: {[round(w, 2) for w in mejores_pesos]}")
        
        return mejores_pesos, self.mejor_historial, self.promedio_historial