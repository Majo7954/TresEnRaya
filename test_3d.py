from AgenteNEnRaya3D import AgenteNEnRaya3D


def probar_lineas():
    agente = AgenteNEnRaya3D()
    assert len(agente.lineas_ganadoras) == 76, len(agente.lineas_ganadoras)


def probar_ganador_fila():
    agente = AgenteNEnRaya3D()
    estado = agente.estado_inicial()
    for mov in [(1,1,1),(2,1,1),(1,2,1),(2,2,1),(1,3,1),(2,3,1),(1,4,1)]:
        estado = agente.getResultado(estado, mov)
    assert estado.get_utilidad == 1, estado


def probar_ganador_diagonal_espacial():
    agente = AgenteNEnRaya3D()
    estado = agente.estado_inicial()
    sec = [(1,1,1),(1,1,2),(2,2,2),(1,1,3),(3,3,3),(1,1,4),(4,4,4)]
    for mov in sec:
        estado = agente.getResultado(estado, mov)
    assert estado.get_utilidad == 1, estado


if __name__ == '__main__':
    probar_lineas()
    probar_ganador_fila()
    probar_ganador_diagonal_espacial()
    print('OK: pruebas básicas 3D correctas')
