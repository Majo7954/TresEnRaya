from Tablero import Tablero
from AgenteNEnRaya import AgenteNEnRaya

def main():
    # Configuración del juego
    h = 3  # Altura del tablero
    v = h  # Anchura del tablero
    k = 3  # Número de piezas en línea para ganar

    # Crear instancias del tablero y del agente
    tablero = Tablero(h, v)
    agente_ia = AgenteNEnRaya(h, v, k)

    # Mostrar las instrucciones
    print("Bienvenido al Tres en Raya!")
    print("Juega como 'X' y la IA jugará como 'O'")
    print("Elige una posición para jugar usando coordenadas (fila, columna) desde 1 hasta", h, "para fila y", v, "para columna.")
    print(tablero.juegoActual)
    
    while True:
        # --- Turno de la IA ---
        tablero.percibir(agente_ia)
        print("Es el turno de la IA:")
        agente_ia.programa()
        movimiento_ia = agente_ia.acciones
        print(f"La IA juega en: {movimiento_ia}")
        
        # Actualizar y mostrar tablero después de IA
        tablero.juegoActual = agente_ia.getResultado(tablero.juegoActual, movimiento_ia)
        agente_ia.mostrar(tablero.juegoActual)
        
        # Verificar si la IA ganó o hay empate
        if agente_ia.testTerminal(tablero.juegoActual):
            utilidad = agente_ia.computa_utilidad(tablero.juegoActual.tablero, movimiento_ia, 'X') # Asumiendo IA es X
            # O simplemente comprobar utilidad del estado si ya está calculada
            # Nota: getResultado calcula la utilidad y la guarda en el estado
            if tablero.juegoActual.get_utilidad != 0:
                print("¡La IA ha ganado!")
            else:
                print("¡Es un empate!")
            break

        # --- Turno del Jugador ---
        print("Tu turno (Juegas como 'O'):")
        while True:
            try:
                x = int(input("Introduce la fila (1-{}): ".format(h)))
                y = int(input("Introduce la columna (1-{}): ".format(v)))
                if (x, y) not in tablero.juegoActual.movidas:
                    print("Posición ya ocupada o inválida, intenta de nuevo.")
                    continue
                break
            except ValueError:
                print("Por favor, introduce números válidos.")

        # Actualizar y mostrar tablero después del Jugador
        tablero.juegoActual = agente_ia.getResultado(tablero.juegoActual, (x, y))
        agente_ia.mostrar(tablero.juegoActual)

        # Verificar si el Jugador ganó o hay empate
        if agente_ia.testTerminal(tablero.juegoActual):
            if tablero.juegoActual.get_utilidad != 0:
                print("¡Felicidades! Has ganado.")
            else:
                print("¡Es un empate!")
            break

if __name__ == "__main__":
    main()
