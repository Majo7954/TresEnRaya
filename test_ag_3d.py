from GeneticoNEnRaya3D import GeneticoNEnRaya3D
from AgenteNEnRaya3D import PESOS_DEFECTO_3D


def probar_normalizacion():
    ag = GeneticoNEnRaya3D()
    bruto = [-10, 99, 0, 999, 999999, -5, 2000, 8]
    norm = ag._normalizar_pesos(bruto)
    assert norm[0] >= 0.1
    assert norm[4] <= 20000.0
    assert 1.0 <= norm[7] <= 2.5


def probar_semilla_manual_en_poblacion():
    ag = GeneticoNEnRaya3D(tam_poblacion=4, generaciones=1, profundidad=1, partidas_fitness=1)
    ag.evolucionar(verbose=False)
    # la población evoluciona, pero la heurística manual debe poder representarse y normalizarse sin alterarse
    assert ag._normalizar_pesos(PESOS_DEFECTO_3D) == PESOS_DEFECTO_3D


if __name__ == '__main__':
    probar_normalizacion()
    probar_semilla_manual_en_poblacion()
    print('OK: pruebas básicas AG 3D correctas')
