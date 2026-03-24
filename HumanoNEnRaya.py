from AgenteNEnRaya import AgenteNEnRaya

class HumanoNEnRaya(AgenteNEnRaya):
    def __init__(self):
        super().__init__()  # Inicializa la clase base

    def programa(self):
        # Imprimir las jugadas permitidas
        print("Jugadas permitidas: {}".format(self.jugadas(self.estado)))
        print("")
        
        # Solicitar al jugador humano que ingrese una jugada
        while True:
            try:
                cad_movida = input('Ingresa tu jugada (formato: (fila, columna)): ')
                movida = eval(cad_movida)  # Evalúa la entrada como tupla
                if movida in self.jugadas(self.estado):
                    self.acciones = movida  # Actualiza la acción del humano
                    break  # Sale del bucle si la jugada es válida
                else:
                    print("Movimiento no válido. Intenta de nuevo.")
            except Exception as e:
                print(f"Error: {e}. Asegúrate de ingresar una jugada válida en el formato correcto.")
