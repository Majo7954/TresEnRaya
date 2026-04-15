#################################################################
# Nombre      : Agente                                          #
# Version     : 0.05.03.2017                                    #
# Autor       : Victor                                          #
# Descripcion : Clase abstracta para Agentes inteligentes       #
#               Y clase abstracta para Juegos                   #
##################################################################

from abc import ABC, abstractmethod


class Agente(ABC):
    """Clase abstracta para Agentes inteligentes"""

    def __init__(self, programa=None):
        self.vive = True
        self.percepciones = []
        self.acciones = None

    def esta_vivo(self):
        return self.vive

    @abstractmethod
    def programa(self):
        """Debe implementarse el programa agente"""
        pass


class Juego(ABC):
    """
    Clase abstracta que define la interfaz para cualquier juego de tablero.
    Requerida por la práctica: Implementación de Agentes Inteligentes.
    Todos los juegos (Othello, TicTacToe3D) deben implementar estos métodos.
    """

    @abstractmethod
    def estado_inicial(self):
        """
        Retorna el estado inicial del juego.
        Returns:
            Any: Estado inicial
        """
        pass

    @abstractmethod
    def jugadas_legales(self, estado, jugador=None):
        """
        Retorna lista de jugadas legales para un estado y jugador.
        Args:
            estado: Estado actual del juego
            jugador: Identificador del jugador
        Returns:
            List: Lista de jugadas legales
        """
        pass

    @abstractmethod
    def aplicar_jugada(self, estado, jugada, jugador):
        """
        Retorna nuevo estado después de aplicar la jugada.
        Args:
            estado: Estado actual
            jugada: Jugada a aplicar
            jugador: Jugador que realiza la jugada
        Returns:
            Any: Nuevo estado
        """
        pass

    @abstractmethod
    def es_estado_terminal(self, estado):
        """
        Determina si el estado es terminal.
        Args:
            estado: Estado a evaluar
        Returns:
            bool: True si el juego terminó
        """
        pass

    @abstractmethod
    def resultado_estado(self, estado):
        """
        Retorna el resultado del estado terminal desde perspectiva MAX.
        Args:
            estado: Estado terminal
        Returns:
            int: 1 (gana MAX), -1 (gana MIN), 0 (empate)
        """
        pass