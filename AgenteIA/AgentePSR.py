#################################################################
# Nombre      : Agente PSR                                      #
# Version     : 0.05.03.2017                                    #
# Autor       : Victor                                          #
# Descripcion : Clase especificacion de Agente, implementa      #
#               algoritmos Backtrack para PSR                   #
#################################################################

from AgenteIA.Agente import Agente


class AgentePSR(Agente):

    def __init__(self):
        Agente.__init__(self)
        self.variables = None
        self.dominio = None
        self.vecinos = None

    def setVariables(self, variables):
        self.variables = variables

    def setDominio(self, dominio):
        self.dominio = dominio

    def setVecinos(self, vecinos):
        self.vecinos = vecinos

    def asignar(self, variable, val, asignacion):
        raise Exception("Error: no se implemento")

    def desasignar(self, variable, asignacion):
        raise Exception("Error: no se implemento")

    def seleccionarVariableNoAsignada(self, asignacion):
        return ([var for var in self.variables if var not in asignacion])[0]

    def getConflictos(self, var, val, assignment):
        raise Exception("Error: no se implemento")

    def getDominio(self):
        return self.dominio

    def esCompleto(self, asignacion):
        raise Exception("Error: no se implemento")

    def programa(self):

        def backtrack(asignacion):
            if self.esCompleto(asignacion):
                return asignacion
            vari = self.seleccionarVariableNoAsignada(asignacion)

            for valor in self.getDominio():
                if self.getConflictos(vari, valor, asignacion) == 0:
                    self.asignar(vari, valor, asignacion)
                    resultado = backtrack(asignacion)
                    if resultado is not None:
                        return resultado
            self.desasignar(vari, asignacion)
            return None

        self.acciones = backtrack({})
        self.vive = False
