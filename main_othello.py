"""
Main para Othello
Permite: jugar contra la IA, enfrentar IA vs IA, y ejecutar el algoritmo genético
"""

import random
from Othello import Othello, OthelloAgente, OthelloEvaluacion, OthelloGenetico


def jugar_contra_ia():
    """Juego: Humano (blancas) vs IA (negras)"""
    juego = Othello()
    profundidad = 3
    pesos = OthelloEvaluacion.PESOS_DEFECTO
    
    print("=" * 50)
    print("OTHELLO - Humano vs IA")
    print("Tú juegas con BLANCAS (B), la IA juega con NEGRAS (N)")
    print("Formato de jugada: fila columna (ej: 2 3)")
    print("=" * 50)
    
    # Preguntar si quiere usar pesos optimizados
    usar_opt = input("¿Usar pesos optimizados? (s/n): ").lower() == 's'
    if usar_opt:
        # Pesos optimizados (ejemplo, puedes cambiarlos después de ejecutar el AG)
        pesos_opt = [1.2, 0.8, 1.5, 0.4]
        pesos = pesos_opt
        print(f"Usando pesos optimizados: {pesos_opt}")
    
    agente_ia = OthelloAgente(profundidad=profundidad, pesos=pesos, jugador='N')
    
    while not juego.es_terminal():
        juego.mostrar()
        
        if juego.jugador_actual == 'N':
            # Turno de la IA
            print("\n🤖 IA pensando...")
            mov = agente_ia.seleccionar_movimiento(juego)
            if mov:
                print(f"IA juega en: {mov}")
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                print("IA no tiene movimientos, pasa turno")
                juego.jugador_actual = 'B'
        else:
            # Turno del humano
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
                        print(f"Movimiento inválido. Movimientos legales: {movimientos}")
                except:
                    print("Entrada inválida. Usa formato: fila columna (ej: 2 3)")
    
    # Fin del juego
    juego.mostrar()
    negras, blancas = juego.contar_fichas()
    print(f"\n📊 Resultado final: Negras (IA): {negras} | Blancas (Tú): {blancas}")
    
    resultado = juego.obtener_resultado()
    if resultado == 1:
        print("🏆 ¡Gana la IA (Negras)!")
    elif resultado == -1:
        print("🎉 ¡Ganaste (Blancas)!")
    else:
        print("🤝 Empate")


def enfrentar_ia_vs_ia(partidas=10, profundidad=3):
    """Enfrenta dos agentes IA entre sí"""
    print(f"\n{'='*50}")
    print(f"IA vs IA - {partidas} partidas (profundidad={profundidad})")
    print(f"{'='*50}")
    
    # Agente con pesos manuales
    agente_manual = OthelloAgente(profundidad=profundidad, pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='N')
    
    # Agente con pesos mejorados (puedes cambiarlos después de ejecutar AG)
    pesos_mejorados = [1.2, 0.8, 1.5, 0.4]  # Ejemplo
    agente_mejorado = OthelloAgente(profundidad=profundidad, pesos=pesos_mejorados, jugador='B')
    
    victorias_manual = 0
    victorias_mejorado = 0
    empates = 0
    
    for i in range(partidas):
        juego = Othello()
        
        # Alternar quién empieza
        if i % 2 == 0:
            agente_manual.jugador = 'N'
            agente_mejorado.jugador = 'B'
        else:
            agente_manual.jugador = 'B'
            agente_mejorado.jugador = 'N'
        
        while not juego.es_terminal():
            jugador_actual = juego.jugador_actual
            
            if jugador_actual == agente_manual.jugador:
                mov = agente_manual.seleccionar_movimiento(juego)
            else:
                mov = agente_mejorado.seleccionar_movimiento(juego)
            
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                # Pasar turno
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'
        
        resultado = juego.obtener_resultado()
        
        # Determinar quién ganó (desde perspectiva de agente_manual)
        if (resultado == 1 and agente_manual.jugador == 'N') or (resultado == -1 and agente_manual.jugador == 'B'):
            victorias_manual += 1
        elif resultado == 0:
            empates += 1
        else:
            victorias_mejorado += 1
        
        if (i + 1) % 10 == 0:
            print(f"Partidas jugadas: {i+1}")
    
    print(f"\n📊 Resultados finales:")
    print(f"  Victorias agente manual: {victorias_manual}")
    print(f"  Victorias agente mejorado: {victorias_mejorado}")
    print(f"  Empates: {empates}")
    print(f"  Tasa de victoria manual: {victorias_manual/partidas:.2%}")


def ejecutar_algoritmo_genetico():
    """Ejecuta el algoritmo genético para optimizar los pesos"""
    print("=" * 50)
    print("ALGORITMO GENÉTICO para optimizar pesos de Othello")
    print("=" * 50)
    
    # Parámetros del AG
    tam_poblacion = 20      # Tamaño de la población
    generaciones = 15       # Número de generaciones
    profundidad = 2         # Profundidad de búsqueda (menor para que sea más rápido)
    partidas_por_fitness = 10  # Partidas por evaluación de fitness
    
    print(f"\nParámetros:")
    print(f"  Población: {tam_poblacion}")
    print(f"  Generaciones: {generaciones}")
    print(f"  Profundidad Minimax: {profundidad}")
    print(f"  Partidas por fitness: {partidas_por_fitness}")
    print()
    
    input("Presiona Enter para comenzar...")
    
    ag = OthelloGenetico(
        tam_poblacion=tam_poblacion,
        generaciones=generaciones,
        profundidad=profundidad,
        partidas_por_fitness=partidas_por_fitness
    )
    
    mejores_pesos, historial_mejor, historial_promedio = ag.evolucionar(verbose=True)
    
    print("\n" + "=" * 50)
    print("RESULTADOS DEL ALGORITMO GENÉTICO")
    print("=" * 50)
    print(f"Mejores pesos encontrados: {[round(w, 2) for w in mejores_pesos]}")
    
    # Prueba final con los mejores pesos
    print("\n🧪 Prueba final con mejores pesos vs pesos manuales...")
    agente_opt = OthelloAgente(profundidad=3, pesos=mejores_pesos, jugador='N')
    agente_manual = OthelloAgente(profundidad=3, pesos=OthelloEvaluacion.PESOS_DEFECTO, jugador='B')
    
    victorias = 0
    partidas_test = 20
    for _ in range(partidas_test):
        juego = Othello()
        while not juego.es_terminal():
            if juego.jugador_actual == agente_opt.jugador:
                mov = agente_opt.seleccionar_movimiento(juego)
            else:
                mov = agente_manual.seleccionar_movimiento(juego)
            
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if juego.jugador_actual == 'N' else 'N'
        
        resultado = juego.obtener_resultado()
        if (resultado == 1 and agente_opt.jugador == 'N') or (resultado == -1 and agente_opt.jugador == 'B'):
            victorias += 1
    
    print(f"  Agente optimizado ganó {victorias}/{partidas_test} partidas ({victorias/partidas_test:.0%}) contra agente manual")
    
    return mejores_pesos


def menu():
    """Menú principal"""
    print("\n" + "=" * 50)
    print("          OTHELLO - MENÚ PRINCIPAL")
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
    
    # Volver al menú
    input("\nPresiona Enter para continuar...")
    menu()


if __name__ == "__main__":
    menu()