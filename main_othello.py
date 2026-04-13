"""
Main para Othello
Permite: jugar contra la IA, enfrentar IA vs IA, y ejecutar el algoritmo genético.
Usa OthelloAgente que hereda de AgenteJugador.
"""

import os
from Othello import Othello, OthelloAgente, OthelloEvaluacion, OthelloGenetico, comparar_agentes

ARCHIVO_PESOS = 'mejores_pesos_othello.json'


# ============================================================================
# MODO 1: Humano vs IA
# ============================================================================

def jugar_contra_ia():
    juego = Othello()
    profundidad = 3

    print("=" * 50)
    print("OTHELLO — Humano vs IA")
    print("Tú juegas con BLANCAS (B), la IA juega con NEGRAS (N)")
    print("Formato de jugada: fila columna  (ej: 2 3)")
    print("=" * 50)

    pesos = OthelloEvaluacion.PESOS_DEFECTO
    if os.path.exists(ARCHIVO_PESOS):
        usar_opt = input("Se encontraron pesos optimizados. ¿Usarlos? (s/n): ").lower() == 's'
        if usar_opt:
            ag_tmp = OthelloGenetico()
            pesos = ag_tmp.cargar_pesos(ARCHIVO_PESOS)
    else:
        print("(No se encontraron pesos optimizados, usando pesos manuales)")

    agente_ia = OthelloAgente(profundidad=profundidad, pesos=pesos, jugador='N')

    while not juego.es_terminal():
        juego.mostrar()

        if juego.jugador_actual == 'N':
            print("\n🤖 IA pensando...")
            mov = agente_ia.seleccionar_movimiento(juego)
            if mov:
                print(f"IA juega en: {mov}")
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                print("IA no tiene movimientos, pasa turno")
                juego.jugador_actual = 'B'
        else:
            print("\n👤 Tu turno (Blancas)")
            movimientos = juego.obtener_movimientos_legales('B')
            print(f"Movimientos legales: {movimientos}")

            if not movimientos:
                print("No tienes movimientos, pasas turno")
                juego.jugador_actual = 'N'
                continue

            while True:
                try:
                    entrada = input("Ingresa fila y columna (0-7): ")
                    f, c = map(int, entrada.split())
                    if (f, c) in movimientos:
                        juego.aplicar_movimiento(f, c, 'B')
                        break
                    else:
                        print(f"Movimiento inválido. Legales: {movimientos}")
                except Exception:
                    print("Entrada inválida. Usa formato: fila columna  (ej: 2 3)")

    _mostrar_resultado(juego)


# ============================================================================
# MODO 2: IA vs IA
# ============================================================================

def enfrentar_ia_vs_ia(partidas=10, profundidad=3):
    print(f"\n{'='*50}")
    print(f"IA vs IA — {partidas} partidas (profundidad={profundidad})")
    print(f"{'='*50}")

    pesos_mejorados = OthelloEvaluacion.PESOS_DEFECTO
    if os.path.exists(ARCHIVO_PESOS):
        ag_tmp = OthelloGenetico()
        pesos_mejorados = ag_tmp.cargar_pesos(ARCHIVO_PESOS)
        print("Agente optimizado usa pesos del AG.")
    else:
        print("No se encontraron pesos optimizados. Ambos agentes usarán pesos manuales.")

    victorias_manual   = 0
    victorias_mejorado = 0
    empates            = 0

    for i in range(partidas):
        juego = Othello()

        if i % 2 == 0:
            agente_manual   = OthelloAgente(profundidad=profundidad,
                                            pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='N')
            agente_mejorado = OthelloAgente(profundidad=profundidad,
                                            pesos=pesos_mejorados, jugador='B')
        else:
            agente_manual   = OthelloAgente(profundidad=profundidad,
                                            pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='B')
            agente_mejorado = OthelloAgente(profundidad=profundidad,
                                            pesos=pesos_mejorados, jugador='N')

        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            agente = agente_manual if jugador_actual == agente_manual.jugador else agente_mejorado
            mov = agente.seleccionar_movimiento(juego)
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultado = juego.obtener_resultado()

        gano_manual = (
            (resultado == 1  and agente_manual.jugador == 'N') or
            (resultado == -1 and agente_manual.jugador == 'B')
        )
        if resultado == 0:
            empates += 1
        elif gano_manual:
            victorias_manual += 1
        else:
            victorias_mejorado += 1

        if (i + 1) % 5 == 0:
            print(f"  Partidas jugadas: {i+1}/{partidas}")

    print(f"\n📊 Resultados finales:")
    print(f"  Victorias agente manual   : {victorias_manual}")
    print(f"  Victorias agente mejorado : {victorias_mejorado}")
    print(f"  Empates                   : {empates}")
    print(f"  Tasa victoria manual      : {victorias_manual/partidas:.2%}")
    print(f"  Tasa victoria mejorado    : {victorias_mejorado/partidas:.2%}")


# ============================================================================
# MODO 3: Algoritmo Genético
# ============================================================================

def ejecutar_algoritmo_genetico():
    print("=" * 50)
    print("ALGORITMO GENÉTICO — optimizar pesos de Othello")
    print("=" * 50)

    tam_poblacion      = 20
    generaciones       = 15
    profundidad        = 2
    partidas_por_fitness = 10

    print(f"\nParámetros:")
    print(f"  Población           : {tam_poblacion}")
    print(f"  Generaciones        : {generaciones}")
    print(f"  Profundidad Minimax : {profundidad}")
    print(f"  Partidas/fitness    : {partidas_por_fitness}")
    input("\nPresiona Enter para comenzar...")

    ag = OthelloGenetico(
        tam_poblacion=tam_poblacion,
        generaciones=generaciones,
        profundidad=profundidad,
        partidas_por_fitness=partidas_por_fitness
    )

    mejores_pesos, historial_mejor, historial_promedio = ag.evolucionar(verbose=True)

    ag.guardar_pesos(mejores_pesos, ARCHIVO_PESOS)
    ag.graficar_convergencia('convergencia_othello.png')

    print("\n🧪 Prueba final: pesos AG vs pesos manuales (20 partidas)...")
    victorias = 0
    partidas_test = 20

    for i in range(partidas_test):
        juego = Othello()
        if i % 2 == 0:
            agente_opt    = OthelloAgente(profundidad=3, pesos=mejores_pesos, jugador='N')
            agente_manual = OthelloAgente(profundidad=3,
                                          pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='B')
        else:
            agente_opt    = OthelloAgente(profundidad=3, pesos=mejores_pesos, jugador='B')
            agente_manual = OthelloAgente(profundidad=3,
                                          pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='N')

        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            agente = agente_opt if jugador_actual == agente_opt.jugador else agente_manual
            mov = agente.seleccionar_movimiento(juego)
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'

        resultado = juego.obtener_resultado()
        gano_opt = (
            (resultado == 1  and agente_opt.jugador == 'N') or
            (resultado == -1 and agente_opt.jugador == 'B')
        )
        if gano_opt:
            victorias += 1

    print(f"  Agente optimizado: {victorias}/{partidas_test} victorias ({victorias/partidas_test:.0%})")

    return mejores_pesos


# ============================================================================
# UTILIDADES
# ============================================================================

def _mostrar_resultado(juego: Othello):
    juego.mostrar()
    negras, blancas = juego.contar_fichas()
    print(f"\n📊 Resultado final — Negras (IA): {negras} | Blancas (Tú): {blancas}")
    resultado = juego.obtener_resultado()
    if resultado == 1:
        print("🏆 ¡Gana la IA (Negras)!")
    elif resultado == -1:
        print("🎉 ¡Ganaste (Blancas)!")
    else:
        print("🤝 Empate")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu():
    print("\n" + "=" * 50)
    print("          OTHELLO — MENÚ PRINCIPAL")
    print("=" * 50)
    print("1. Jugar contra la IA")
    print("2. Enfrentar IA vs IA")
    print("3. Ejecutar Algoritmo Genético (optimizar pesos)")
    print("4. Salir")
    print("=" * 50)

    opcion = input("Selecciona una opción: ")

    if opcion == '1':
        jugar_contra_ia()
    elif opcion == '2':
        partidas = int(input("Número de partidas (default 10): ") or "10")
        profundidad = int(input("Profundidad de búsqueda (default 3): ") or "3")
        enfrentar_ia_vs_ia(partidas, profundidad)
    elif opcion == '3':
        ejecutar_algoritmo_genetico()
    elif opcion == '4':
        print("¡Hasta luego!")
        return
    else:
        print("Opción inválida")

    input("\nPresiona Enter para continuar...")
    menu()


if __name__ == "__main__":
    menu()