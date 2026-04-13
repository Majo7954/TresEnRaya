from AgenteNEnRaya3D import AgenteNEnRaya3D
from Tablero3D import Tablero3D


def leer_movimiento(estado, n):
    while True:
        try:
            texto = input(f"Ingresa tu jugada como x,y,z entre 1 y {n}: ").strip()
            partes = [int(p.strip()) for p in texto.split(',')]
            if len(partes) != 3:
                raise ValueError("Debes ingresar exactamente tres números")
            mov = tuple(partes)
            if mov not in estado.movidas:
                print("Movimiento inválido u ocupado.")
                continue
            return mov
        except Exception as e:
            print("Entrada inválida:", e)


def main():
    n = 4
    k = 4
    profundidad = 2

    agente = AgenteNEnRaya3D(n=n, k=k, profundidad_maxima=profundidad)
    tablero = Tablero3D(agente)

    print("Tic-Tac-Toe 3D", f"{n}x{n}x{n}")
    print("La IA juega como X y tú juegas como O.")
    print("Se gana alineando 4 fichas en cualquier línea 3D.")
    agente.mostrar(tablero.juegoActual)

    while True:
        # Turno IA
        tablero.percibir(agente)
        mov_ia = agente.acciones
        print("La IA juega:", mov_ia)
        tablero.juegoActual = agente.getResultado(tablero.juegoActual, mov_ia)
        agente.mostrar(tablero.juegoActual)

        if agente.testTerminal(tablero.juegoActual):
            if tablero.juegoActual.get_utilidad != 0:
                print("La IA ganó.")
            else:
                print("Empate.")
            break

        # Turno humano
        mov_humano = leer_movimiento(tablero.juegoActual, n)
        tablero.juegoActual = agente.getResultado(tablero.juegoActual, mov_humano)
        agente.mostrar(tablero.juegoActual)

        if agente.testTerminal(tablero.juegoActual):
            if tablero.juegoActual.get_utilidad != 0:
                print("Ganaste.")
            else:
                print("Empate.")
            break


if __name__ == "__main__":
    main()
