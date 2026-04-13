"""
GeneticoNEnRaya3D — Algoritmo Genético para optimizar los pesos
de la función de evaluación de AgenteNEnRaya3D.

Fase 3 de la práctica: optimización de la heurística mediante AG.

Operadores:
  - Selección por torneo (k=3)
  - Cruce aritmético BLX-alpha
  - Mutación gaussiana por gen
  - Elitismo (el mejor individuo pasa intacto)

Función de fitness:
  - Tasa de victorias jugando N partidas contra:
      a) un agente con pesos manuales (PESOS_DEFECTO_3D)
      b) un agente aleatorio
  - Se alterna quién juega como X y quién como O para evitar
    sesgo de primer jugador.
"""

import random
import json
import time

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

from AgenteNEnRaya3D import AgenteNEnRaya3D, PESOS_DEFECTO_3D
from itertools import product


# ============================================================================
# Agente aleatorio (referencia débil)
# ============================================================================

class AgenteAleatorio3D(AgenteNEnRaya3D):
    """Selecciona movimientos al azar — sirve como oponente base fácil."""

    def programa(self):
        if self.estado.movidas:
            self.acciones = random.choice(self.estado.movidas)
        else:
            self.acciones = None


# ============================================================================
# Algoritmo Genético
# ============================================================================

class GeneticoNEnRaya3D:
    """
    Optimiza los 8 pesos de FunEval de AgenteNEnRaya3D mediante un AG.

    Parámetros configurables:
      tam_poblacion     — número de individuos por generación
      generaciones      — número de generaciones a evolucionar
      profundidad       — profundidad Minimax usada en cada partida
      partidas_fitness  — partidas jugadas para estimar el fitness
      n, k              — tamaño del cubo y fichas para ganar
    """

    N_PESOS = 8   # número de pesos en FunEval

    def __init__(self, tam_poblacion=20, generaciones=15,
                 profundidad=2, partidas_fitness=8, n=4, k=4):
        self.tam_poblacion  = tam_poblacion
        self.generaciones   = generaciones
        self.profundidad    = profundidad
        self.partidas_fitness = partidas_fitness
        self.n = n
        self.k = k
        self.poblacion = []
        self.mejor_historial   = []
        self.promedio_historial = []

    # ------------------------------------------------------------------
    # Creación y normalización de individuos
    # ------------------------------------------------------------------

    # Rangos por gen alineados con la heurística real de AgenteNEnRaya3D.
    # Antes todos los genes estaban en ~[0.5, 5.0], lo cual impedía explorar
    # valores como 60, 120, 300 o 10000 usados por la línea base manual.
    RANGOS_PESOS = [
        (0.1, 6.0),        # [0] centro
        (0.1, 6.0),        # [1] linea1
        (1.0, 20.0),       # [2] linea2
        (10.0, 150.0),     # [3] linea3
        (1000.0, 20000.0), # [4] linea4 / victoria
        (10.0, 300.0),     # [5] amenaza
        (50.0, 800.0),     # [6] fork
        (1.0, 2.5),        # [7] diag3d
    ]

    def _crear_individuo(self):
        """Crea un individuo dentro de rangos coherentes con la heurística."""
        return [random.uniform(lo, hi) for lo, hi in self.RANGOS_PESOS]

    def _normalizar_pesos(self, individuo):
        """Recorta cada gen al rango permitido y preserva su escala."""
        return [max(lo, min(hi, w)) for w, (lo, hi) in zip(individuo, self.RANGOS_PESOS)]

    # ------------------------------------------------------------------
    # Función de fitness
    # ------------------------------------------------------------------

    def _jugar_partida(self, agente_x, agente_o):
        """
        Juega una partida completa entre dos agentes.
        agente_x juega como 'X' (primer jugador), agente_o como 'O'.
        Retorna: 1 si gana X, -1 si gana O, 0 si empate.
        """
        # Ambos comparten el mismo tipo de agente; usamos el estado de agente_x
        estado = agente_x.estado_inicial()

        while not agente_x.testTerminal(estado):
            if estado.jugador == 'X':
                agente_x.estado = estado
                agente_x.programa()
                mov = agente_x.acciones
            else:
                agente_o.estado = estado
                agente_o.programa()
                mov = agente_o.acciones

            if mov is None:
                break
            estado = agente_x.getResultado(estado, mov)

        return estado.get_utilidad  # +1 gana X, -1 gana O, 0 empate

    def _calcular_fitness(self, individuo):
        """
        Fitness = tasa de victorias como X + tasa de victorias como O,
        promediada y normalizada a [0, 1].

        Se juegan dos rondas contra cada tipo de oponente:
          - pesos manuales (PESOS_DEFECTO_3D)
          - agente aleatorio
        """
        pesos = self._normalizar_pesos(individuo)
        victorias = 0
        total = 0

        for i in range(self.partidas_fitness):
            agente_eval = AgenteNEnRaya3D(self.n, self.k, self.profundidad, pesos=pesos)

            # Contra pesos manuales
            agente_base = AgenteNEnRaya3D(self.n, self.k, self.profundidad,
                                          pesos=PESOS_DEFECTO_3D)
            agente_alea = AgenteAleatorio3D(self.n, self.k)

            # Partida 1: eval=X vs base=O
            resultado = self._jugar_partida(agente_eval, agente_base)
            if resultado == 1:
                victorias += 1
            elif resultado == 0:
                victorias += 0.5
            total += 1

            # Partida 2: base=X vs eval=O
            resultado = self._jugar_partida(agente_base, agente_eval)
            if resultado == -1:   # eval ganó como O
                victorias += 1
            elif resultado == 0:
                victorias += 0.5
            total += 1

            # Partida 3: eval=X vs aleatorio=O
            resultado = self._jugar_partida(agente_eval, agente_alea)
            if resultado == 1:
                victorias += 1
            elif resultado == 0:
                victorias += 0.5
            total += 1

        return victorias / total

    # ------------------------------------------------------------------
    # Operadores genéticos
    # ------------------------------------------------------------------

    def _seleccion_torneo(self, fitnesses, k=3):
        mejor_idx, mejor_fit = None, -1.0
        for _ in range(k):
            idx = random.randint(0, len(self.poblacion) - 1)
            if fitnesses[idx] > mejor_fit:
                mejor_fit = fitnesses[idx]
                mejor_idx = idx
        return self.poblacion[mejor_idx]

    def _cruce_blx(self, padre1, padre2, alpha=0.5):
        """BLX-alpha: explora fuera del intervalo [padre1, padre2]."""
        hijo = []
        for i in range(self.N_PESOS):
            lo = min(padre1[i], padre2[i])
            hi = max(padre1[i], padre2[i])
            rango = hi - lo
            hijo.append(random.uniform(lo - alpha * rango, hi + alpha * rango))
        return hijo

    def _mutacion_gaussiana(self, individuo, tasa=0.25):
        """Mutación gaussiana adaptada a la escala de cada peso."""
        for i, (lo, hi) in enumerate(self.RANGOS_PESOS):
            if random.random() < tasa:
                escala = (hi - lo) * (0.10 if i != 7 else 0.06)
                individuo[i] = max(lo, min(hi, individuo[i] + random.gauss(0, escala)))
        return individuo

    # ------------------------------------------------------------------
    # Bucle principal
    # ------------------------------------------------------------------

    def evolucionar(self, verbose=True):
        """
        Ejecuta el AG completo.
        Retorna: (mejores_pesos, historial_mejor_fitness, historial_promedio)
        """
        self.poblacion = [self._crear_individuo() for _ in range(self.tam_poblacion)]
        # Inyectar la heurística manual como semilla útil para no empezar a ciegas.
        if self.tam_poblacion > 0:
            self.poblacion[0] = list(PESOS_DEFECTO_3D)
        self.mejor_historial    = []
        self.promedio_historial = []

        if verbose:
            print(f"\n{'='*55}")
            print(f" AG 3D Tic-Tac-Toe — {self.generaciones} generaciones, "
                  f"población {self.tam_poblacion}")
            print(f"{'='*55}")

        for gen in range(self.generaciones):
            t0 = time.time()
            fitnesses = [self._calcular_fitness(ind) for ind in self.poblacion]

            mejor_fit  = max(fitnesses)
            mejor_ind  = self.poblacion[fitnesses.index(mejor_fit)]
            prom_fit   = sum(fitnesses) / len(fitnesses)

            self.mejor_historial.append(mejor_fit)
            self.promedio_historial.append(prom_fit)

            if verbose:
                elapsed = time.time() - t0
                print(f"Gen {gen+1:3d} | Mejor: {mejor_fit:.4f} | "
                      f"Prom: {prom_fit:.4f} | "
                      f"Pesos: {[round(w, 2) for w in mejor_ind]} | "
                      f"{elapsed:.1f}s")

            # Nueva generación con elitismo
            nueva = [list(mejor_ind)]
            while len(nueva) < self.tam_poblacion:
                p1 = self._seleccion_torneo(fitnesses)
                p2 = self._seleccion_torneo(fitnesses)
                hijo = self._cruce_blx(p1, p2)
                hijo = self._mutacion_gaussiana(hijo)
                nueva.append(hijo)
            self.poblacion = nueva

        # Evaluación final
        fitnesses_final = [self._calcular_fitness(ind) for ind in self.poblacion]
        mejor_idx = fitnesses_final.index(max(fitnesses_final))
        mejores_pesos = self._normalizar_pesos(self.poblacion[mejor_idx])

        if verbose:
            print(f"\n✅ Mejores pesos finales: {[round(w, 3) for w in mejores_pesos]}")
            print(f"   Fitness final: {max(fitnesses_final):.4f}")

        return mejores_pesos, self.mejor_historial, self.promedio_historial

    # ------------------------------------------------------------------
    # Persistencia y visualización
    # ------------------------------------------------------------------

    def guardar_pesos(self, pesos, archivo='mejores_pesos_3d.json'):
        with open(archivo, 'w') as f:
            json.dump({'pesos': pesos, 'n_pesos': len(pesos)}, f, indent=2)
        print(f"💾 Pesos 3D guardados en '{archivo}'")

    def cargar_pesos(self, archivo='mejores_pesos_3d.json'):
        with open(archivo) as f:
            data = json.load(f)
        print(f"📂 Pesos 3D cargados desde '{archivo}': {data['pesos']}")
        return data['pesos']

    def graficar_convergencia(self, archivo='convergencia_3d.png'):
        if not MATPLOTLIB_OK:
            print("matplotlib no disponible; se omite la gráfica.")
            return
        if not self.mejor_historial:
            print("Ejecuta evolucionar() primero.")
            return
        plt.figure(figsize=(10, 5))
        plt.plot(self.mejor_historial,    label='Mejor fitness',   color='blue',   linewidth=2)
        plt.plot(self.promedio_historial, label='Fitness promedio', color='orange', linewidth=2, linestyle='--')
        plt.xlabel('Generación')
        plt.ylabel('Fitness (tasa de victorias)')
        plt.title('Convergencia del AG — 3D Tic-Tac-Toe')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(archivo)
        print(f"📊 Gráfica guardada en '{archivo}'")


# ============================================================================
# Menú de ejecución directa
# ============================================================================

def menu_3d():
    print("\n" + "="*50)
    print("   AG PARA 3D TIC-TAC-TOE — MENÚ")
    print("="*50)
    print("1. Ejecutar AG (optimizar pesos)")
    print("2. Cargar pesos y jugar IA vs IA")
    print("3. Salir")

    op = input("Opción: ").strip()

    if op == '1':
        tam  = int(input("Tamaño población (default 20): ") or "20")
        gens = int(input("Generaciones    (default 15): ") or "15")
        pf   = int(input("Partidas/fitness (default 8): ") or "8")
        prof = int(input("Profundidad     (default 2) : ") or "2")

        ag = GeneticoNEnRaya3D(tam_poblacion=tam, generaciones=gens,
                               profundidad=prof, partidas_fitness=pf)
        mejores, _, _ = ag.evolucionar(verbose=True)
        ag.guardar_pesos(mejores)
        ag.graficar_convergencia()

    elif op == '2':
        import os
        archivo = 'mejores_pesos_3d.json'
        if not os.path.exists(archivo):
            print(f"No se encontró {archivo}. Ejecuta el AG primero.")
            return

        ag_tmp  = GeneticoNEnRaya3D()
        pesos   = ag_tmp.cargar_pesos(archivo)

        partidas = int(input("Número de partidas (default 10): ") or "10")
        prof     = int(input("Profundidad        (default 2) : ") or "2")

        v_opt, v_base, empates = 0, 0, 0
        for i in range(partidas):
            if i % 2 == 0:
                ag_opt  = AgenteNEnRaya3D(profundidad_maxima=prof, pesos=pesos)
                ag_base = AgenteNEnRaya3D(profundidad_maxima=prof, pesos=PESOS_DEFECTO_3D)
                resultado = ag_tmp._jugar_partida(ag_opt, ag_base)
                if resultado == 1: v_opt += 1
                elif resultado == -1: v_base += 1
                else: empates += 1
            else:
                ag_base = AgenteNEnRaya3D(profundidad_maxima=prof, pesos=PESOS_DEFECTO_3D)
                ag_opt  = AgenteNEnRaya3D(profundidad_maxima=prof, pesos=pesos)
                resultado = ag_tmp._jugar_partida(ag_base, ag_opt)
                if resultado == -1: v_opt += 1
                elif resultado == 1: v_base += 1
                else: empates += 1

        print(f"\nResultados ({partidas} partidas):")
        print(f"  Optimizado: {v_opt} | Manual: {v_base} | Empates: {empates}")
        print(f"  Tasa victoria optimizado: {v_opt/partidas:.1%}")


if __name__ == '__main__':
    menu_3d()
