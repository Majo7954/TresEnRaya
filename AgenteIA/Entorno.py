#################################################################
# Nombre      : Entorno                                         #
# Version     : 0.05.03.2017                                    #
# Autor       : Victor                                          #
# Descripcion : Clase abstracta para modelar entorno            #
##################################################################

from AgenteIA.Agente import Agente


class Entorno(object):

    def __init__(self):
        self.objetos = []
        self.agentes = []

    def percibir(self, agente):
        # Agente percibe del entorno
        raise Exception("Se debe implementar la captura de percepciones")

    def ejecutar(self, agente):
        # cambia el entorno segun su accion
        raise Exception("Se debe implementar ejecutar")

    def finalizado(self):
        return any(not agente.vive for agente in self.agentes)

    def avanzar(self):
        if not self.finalizado():
            for agente in self.agentes:
                self.percibir(agente)
                if not agente.vive:
                    break
                self.ejecutar(agente)
                if not agente.vive:
                    break


    def run(self):
        # ejecutar el entorno para un numero de pasos
        while True:
            if self.finalizado():
                break
            self.avanzar()

    def insertar_objeto(self, cosa):
        # Insertar objeto en el entorno en una ubicacion For
        # Si el objeto es un agente, creamos otro programa

        assert cosa not in self.objetos, "no insertar el mismo objeto"
        self.objetos.append(cosa)
        if isinstance(cosa, Agente):
            cosa.performance = 0
            self.agentes.append(cosa)
