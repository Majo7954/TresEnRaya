"""
experimentos.py — Fase 4: Experimentación, análisis estadístico y gráficas.

Ejecuta torneos completos para ambos juegos y genera:
  - Tablas de rendimiento comparativo
  - Gráficas de barras con intervalos de confianza (Wilson 95%)
  - Gráficas de convergencia del AG (si existen)
  - Resumen estadístico en consola

Uso rápido:
    python experimentos.py

El script detecta automáticamente si existen pesos optimizados guardados.
Si no existen, puede ejecutar los AGs antes de medir.
"""

import os
import random
import math
import json

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
    print("[AVISO] matplotlib no disponible; se omitirán las gráficas.")

# ============================================================================
# Intervalo de confianza de Wilson (95%) para proporciones
# ============================================================================

def ic_wilson(victorias, n, confianza=0.95):
    """
    Intervalo de confianza de Wilson para proporción p = victorias/n.
    Retorna (p_hat, low, high).
    Más robusto que el intervalo de Wald cuando n es pequeño o p ≈ 0 o 1.
    """
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.96 if confianza == 0.95 else 2.576  # 95% o 99%
    p = victorias / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margen = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return p, max(0.0, centro - margen), min(1.0, centro + margen)


# ============================================================================
# Experimentos para Othello
# ============================================================================

def experimentos_othello(n_partidas=30, profundidad=3, archivo_pesos=None):
    """
    Enfrenta tres agentes entre sí en Othello:
      A: Agente aleatorio
      B: Agente con pesos manuales (PESOS_DEFECTO)
      C: Agente con pesos optimizados por AG (si existen)

    Retorna dict con resultados por par de agentes.
    """
    from Othello import Othello, OthelloAgente, OthelloEvaluacion

    print(f"\n{'='*55}")
    print(f"  OTHELLO — {n_partidas} partidas por par, prof={profundidad}")
    print(f"{'='*55}")

    # Cargar pesos AG si existen
    archivo_pesos = archivo_pesos or 'mejores_pesos_othello.json'
    pesos_ag = None
    if os.path.exists(archivo_pesos):
        with open(archivo_pesos) as f:
            pesos_ag = json.load(f)['pesos']
        print(f"  Pesos AG cargados desde '{archivo_pesos}'")
    else:
        print(f"  [AVISO] No se encontró '{archivo_pesos}'. AG no incluido.")

    def agente_aleatorio_othello(juego):
        movs = juego.obtener_movimientos_legales()
        return random.choice(movs) if movs else None

    def jugar_partida(fn_negro, fn_blanco):
        """fn_negro / fn_blanco son callables que reciben el juego y retornan (f,c)."""
        juego = Othello()
        while not juego.es_terminal():
            jugador = juego.jugador_actual
            if jugador == 'N':
                mov = fn_negro(juego)
            else:
                mov = fn_blanco(juego)
            if mov:
                juego.aplicar_movimiento(mov[0], mov[1])
            else:
                juego.jugador_actual = 'B' if jugador == 'N' else 'N'
        return juego.obtener_resultado()  # 1=N gana, -1=B gana, 0=empate

    def torneo(fn_a, fn_b, nombre_a, nombre_b):
        """Enfrenta A vs B alternando colores."""
        v_a, v_b, empates = 0, 0, 0
        for i in range(n_partidas):
            if i % 2 == 0:
                r = jugar_partida(fn_a, fn_b)   # A=N, B=B
                if r == 1: v_a += 1
                elif r == -1: v_b += 1
                else: empates += 1
            else:
                r = jugar_partida(fn_b, fn_a)   # B=N, A=B
                if r == 1: v_b += 1
                elif r == -1: v_a += 1
                else: empates += 1
        _, lo, hi = ic_wilson(v_a, n_partidas)
        tasa = v_a / n_partidas
        print(f"  {nombre_a:20s} vs {nombre_b:20s} | "
              f"V:{v_a:3d} D:{v_b:3d} E:{empates:2d} | "
              f"Tasa={tasa:.2%} IC95%=[{lo:.2%},{hi:.2%}]")
        return {'nombre_a': nombre_a, 'nombre_b': nombre_b,
                'victorias_a': v_a, 'victorias_b': v_b, 'empates': empates,
                'tasa_a': tasa, 'ic_low': lo, 'ic_high': hi}

    # Crear funciones agente
    ag_manual = OthelloAgente(profundidad=profundidad,
                              pesos=OthelloEvaluacion.PESOS_DEFECTO)
    fn_manual = lambda j: ag_manual.seleccionar_movimiento(j)
    fn_alea   = agente_aleatorio_othello

    resultados = []
    resultados.append(torneo(fn_manual, fn_alea, 'Manual', 'Aleatorio'))

    if pesos_ag:
        ag_opt = OthelloAgente(profundidad=profundidad, pesos=pesos_ag)
        fn_opt = lambda j: ag_opt.seleccionar_movimiento(j)
        resultados.append(torneo(fn_opt, fn_alea,   'AG optimizado', 'Aleatorio'))
        resultados.append(torneo(fn_opt, fn_manual,  'AG optimizado', 'Manual'))

    return resultados


# ============================================================================
# Experimentos para 3D Tic-Tac-Toe
# ============================================================================

def experimentos_3d(n_partidas=20, profundidad=2, archivo_pesos=None):
    """
    Enfrenta tres agentes en 3D Tic-Tac-Toe:
      A: Agente aleatorio
      B: Agente con pesos manuales
      C: Agente con pesos AG (si existen)
    """
    from AgenteNEnRaya3D import AgenteNEnRaya3D, PESOS_DEFECTO_3D
    from GeneticoNEnRaya3D import GeneticoNEnRaya3D, AgenteAleatorio3D

    print(f"\n{'='*55}")
    print(f"  3D TIC-TAC-TOE — {n_partidas} partidas por par, prof={profundidad}")
    print(f"{'='*55}")

    archivo_pesos = archivo_pesos or 'mejores_pesos_3d.json'
    pesos_ag = None
    if os.path.exists(archivo_pesos):
        with open(archivo_pesos) as f:
            pesos_ag = json.load(f)['pesos']
        print(f"  Pesos AG cargados desde '{archivo_pesos}'")
    else:
        print(f"  [AVISO] No se encontró '{archivo_pesos}'. AG no incluido.")

    helper = GeneticoNEnRaya3D()

    def jugar_partida_3d(agente_x, agente_o):
        estado = agente_x.estado_inicial()
        while not agente_x.testTerminal(estado):
            if estado.jugador == 'X':
                agente_x.estado = estado
                agente_x.programa()
                mov = agente_x.acciones
            else:
                agente_o.estado = estado
                agente_o.programa()
                mov = agente_o.acciones
            if mov is None:
                break
            estado = agente_x.getResultado(estado, mov)
        return estado.get_utilidad

    def torneo_3d(fn_a_cls, kw_a, fn_b_cls, kw_b, nombre_a, nombre_b):
        v_a, v_b, empates = 0, 0, 0
        for i in range(n_partidas):
            ag_a = fn_a_cls(**kw_a)
            ag_b = fn_b_cls(**kw_b)
            if i % 2 == 0:
                r = jugar_partida_3d(ag_a, ag_b)   # a=X, b=O
                if r == 1: v_a += 1
                elif r == -1: v_b += 1
                else: empates += 1
            else:
                r = jugar_partida_3d(ag_b, ag_a)   # b=X, a=O
                if r == 1: v_b += 1
                elif r == -1: v_a += 1
                else: empates += 1
        _, lo, hi = ic_wilson(v_a, n_partidas)
        tasa = v_a / n_partidas
        print(f"  {nombre_a:22s} vs {nombre_b:22s} | "
              f"V:{v_a:3d} D:{v_b:3d} E:{empates:2d} | "
              f"Tasa={tasa:.2%} IC95%=[{lo:.2%},{hi:.2%}]")
        return {'nombre_a': nombre_a, 'nombre_b': nombre_b,
                'victorias_a': v_a, 'victorias_b': v_b, 'empates': empates,
                'tasa_a': tasa, 'ic_low': lo, 'ic_high': hi}

    kw_manual = dict(n=4, k=4, profundidad_maxima=profundidad, pesos=PESOS_DEFECTO_3D)
    kw_alea   = dict(n=4, k=4)

    resultados = []
    resultados.append(torneo_3d(AgenteNEnRaya3D, kw_manual,
                                AgenteAleatorio3D, kw_alea,
                                'Manual', 'Aleatorio'))

    if pesos_ag:
        kw_ag = dict(n=4, k=4, profundidad_maxima=profundidad, pesos=pesos_ag)
        resultados.append(torneo_3d(AgenteNEnRaya3D, kw_ag,
                                    AgenteAleatorio3D, kw_alea,
                                    'AG optimizado', 'Aleatorio'))
        resultados.append(torneo_3d(AgenteNEnRaya3D, kw_ag,
                                    AgenteNEnRaya3D, kw_manual,
                                    'AG optimizado', 'Manual'))
    return resultados


# ============================================================================
# Gráficas
# ============================================================================

def graficar_resultados(resultados_othello, resultados_3d,
                        archivo='resultados_experimentos.png'):
    if not MATPLOTLIB_OK:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    def _barras(ax, resultados, titulo):
        etiquetas = [f"{r['nombre_a']}\nvs\n{r['nombre_b']}" for r in resultados]
        tasas     = [r['tasa_a'] for r in resultados]
        lows      = [r['tasa_a'] - r['ic_low']  for r in resultados]
        highs     = [r['ic_high'] - r['tasa_a'] for r in resultados]
        colores   = ['#2196F3' if 'AG' in r['nombre_a'] else '#FF9800' for r in resultados]

        x = range(len(etiquetas))
        bars = ax.bar(x, tasas, color=colores, width=0.5, zorder=3)
        ax.errorbar(x, tasas, yerr=[lows, highs], fmt='none',
                    color='black', capsize=6, linewidth=1.5, zorder=4)
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.7,
                   label='50% (igualdad)')
        ax.set_xticks(list(x))
        ax.set_xticklabels(etiquetas, fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel('Tasa de victorias (primer agente)')
        ax.set_title(titulo, fontweight='bold')
        ax.grid(axis='y', alpha=0.4, zorder=0)
        ax.legend(fontsize=8)

        # Etiquetas de porcentaje encima de cada barra
        for bar, tasa in zip(bars, tasas):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.03, f'{tasa:.1%}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    _barras(axes[0], resultados_othello, 'Othello')
    _barras(axes[1], resultados_3d,       '3D Tic-Tac-Toe')

    # Leyenda de colores
    p_ag  = mpatches.Patch(color='#2196F3', label='Agente AG optimizado')
    p_man = mpatches.Patch(color='#FF9800', label='Agente manual')
    fig.legend(handles=[p_ag, p_man], loc='lower center', ncol=2,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))

    plt.suptitle('Comparativa de rendimiento de agentes IA', fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    print(f"\n📊 Gráfica de resultados guardada en '{archivo}'")


def graficar_convergencias(archivo_othello='convergencia_othello.png',
                           archivo_3d='convergencia_3d.png',
                           salida='convergencias_combinadas.png'):
    """Combina ambas gráficas de convergencia si existen."""
    if not MATPLOTLIB_OK:
        return
    existe_oth = os.path.exists(archivo_othello)
    existe_3d  = os.path.exists(archivo_3d)
    if not existe_oth and not existe_3d:
        print("[INFO] No se encontraron gráficas de convergencia previas.")
        return

    n = sum([existe_oth, existe_3d])
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 5))
    if n == 1:
        axes = [axes]
    idx = 0
    if existe_oth:
        img = plt.imread(archivo_othello)
        axes[idx].imshow(img)
        axes[idx].axis('off')
        axes[idx].set_title('Convergencia AG — Othello')
        idx += 1
    if existe_3d:
        img = plt.imread(archivo_3d)
        axes[idx].imshow(img)
        axes[idx].axis('off')
        axes[idx].set_title('Convergencia AG — 3D Tic-Tac-Toe')
    plt.tight_layout()
    plt.savefig(salida, dpi=150)
    print(f"📈 Convergencias combinadas guardadas en '{salida}'")


# ============================================================================
# Resumen estadístico en texto
# ============================================================================

def imprimir_resumen(resultados_othello, resultados_3d):
    print(f"\n{'='*60}")
    print("  RESUMEN ESTADÍSTICO (IC al 95% — método Wilson)")
    print(f"{'='*60}")

    for titulo, resultados in [('OTHELLO', resultados_othello),
                                ('3D TIC-TAC-TOE', resultados_3d)]:
        print(f"\n  {titulo}")
        print(f"  {'Enfrentamiento':45s} {'Tasa':>6s}  IC 95%")
        print(f"  {'-'*65}")
        for r in resultados:
            label = f"{r['nombre_a']} vs {r['nombre_b']}"
            print(f"  {label:45s} {r['tasa_a']:5.1%}  [{r['ic_low']:.1%}, {r['ic_high']:.1%}]")

    print(f"\n{'='*60}")
    print("  INTERPRETACIÓN")
    print(f"{'='*60}")
    print("""
  - Tasa > 50% y IC completamente por encima de 0.5: el agente es
    significativamente mejor que el oponente al 95% de confianza.
  - Si el IC cruza 0.5: la diferencia no es estadísticamente significativa
    con el número de partidas jugadas (considera aumentar n_partidas).
  - IC más estrecho = más partidas jugadas = estimación más precisa.
""")


# ============================================================================
# Menú principal
# ============================================================================

def menu():
    print("\n" + "="*55)
    print("  FASE 4 — EXPERIMENTOS Y ANÁLISIS ESTADÍSTICO")
    print("="*55)
    print("1. Ejecutar experimentos completos (Othello + 3D)")
    print("2. Solo Othello")
    print("3. Solo 3D Tic-Tac-Toe")
    print("4. Ejecutar AGs y luego experimentos completos")
    print("5. Salir")

    op = input("\nOpción: ").strip()

    if op in ('1', '2', '3', '4'):
        if op == '4':
            # Ejecutar AGs primero
            print("\n--- Ejecutando AG para Othello ---")
            from Othello import OthelloGenetico
            ag_oth = OthelloGenetico(tam_poblacion=15, generaciones=10,
                                     profundidad=2, partidas_por_fitness=8)
            pesos_oth, _, _ = ag_oth.evolucionar(verbose=True)
            ag_oth.guardar_pesos(pesos_oth, 'mejores_pesos_othello.json')
            ag_oth.graficar_convergencia('convergencia_othello.png')

            print("\n--- Ejecutando AG para 3D Tic-Tac-Toe ---")
            from GeneticoNEnRaya3D import GeneticoNEnRaya3D
            ag_3d = GeneticoNEnRaya3D(tam_poblacion=15, generaciones=10,
                                      profundidad=2, partidas_fitness=6)
            pesos_3d, _, _ = ag_3d.evolucionar(verbose=True)
            ag_3d.guardar_pesos(pesos_3d, 'mejores_pesos_3d.json')
            ag_3d.graficar_convergencia('convergencia_3d.png')

        n_oth = int(input("\nPartidas Othello (default 30): ") or "30")
        n_3d  = int(input("Partidas 3D     (default 20): ") or "20")
        p_oth = int(input("Profundidad Othello (default 3): ") or "3")
        p_3d  = int(input("Profundidad 3D      (default 2): ") or "2")

        res_oth, res_3d = [], []

        if op in ('1', '4', '2'):
            res_oth = experimentos_othello(n_oth, p_oth)
        if op in ('1', '4', '3'):
            res_3d = experimentos_3d(n_3d, p_3d)

        # Fallback si solo se ejecutó uno de los dos
        if not res_oth:
            res_oth = [{'nombre_a': 'N/A', 'nombre_b': '-',
                        'victorias_a': 0, 'victorias_b': 0, 'empates': 0,
                        'tasa_a': 0, 'ic_low': 0, 'ic_high': 0}]
        if not res_3d:
            res_3d  = [{'nombre_a': 'N/A', 'nombre_b': '-',
                        'victorias_a': 0, 'victorias_b': 0, 'empates': 0,
                        'tasa_a': 0, 'ic_low': 0, 'ic_high': 0}]

        imprimir_resumen(res_oth, res_3d)
        graficar_resultados(res_oth, res_3d)
        if op == '4':
            graficar_convergencias()


if __name__ == '__main__':
    menu()
