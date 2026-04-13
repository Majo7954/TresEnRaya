```markdown
# Implementación de Agentes Inteligentes para Othello y 3D Tic-Tac-Toe

Proyecto desarrollado para la asignatura de Inteligencia Artificial. Este trabajo implementa agentes capaces de jugar Othello (Reversi) y Tic-Tac-Toe 3D (4x4x4) utilizando algoritmos de búsqueda adversarial y optimización heurística.

## Objetivo

El objetivo principal es diseñar e implementar agentes inteligentes que puedan tomar decisiones en entornos adversariales, utilizando:

- Minimax con poda Alfa-Beta
- Funciones de evaluación heurística
- Optimización de parámetros mediante algoritmos genéticos
- Evaluación experimental del rendimiento de los agentes

## Juegos implementados

### Othello (Reversi)

- Tablero de 8x8
- Generación de movimientos legales
- Aplicación de jugadas con volteo de fichas
- Evaluación heurística basada en:
  - Diferencia de fichas
  - Movilidad
  - Control de esquinas
  - Paridad

### Tic-Tac-Toe 3D (4x4x4)

- Tablero tridimensional 4x4x4
- Generación de todas las líneas ganadoras en 3D
- Detección de estados terminales
- Evaluación heurística basada en:
  - Control del centro
  - Líneas parciales
  - Amenazas
  - Diagonales espaciales

## Algoritmos utilizados

### Minimax con poda Alfa-Beta

Se implementa el algoritmo Minimax para la toma de decisiones en ambos juegos, optimizado mediante poda Alfa-Beta para reducir el número de nodos explorados.

### Función heurística

Cada juego cuenta con una función de evaluación que permite estimar la calidad de un estado cuando no se alcanza una condición terminal.

### Algoritmo Genético

Se utiliza un algoritmo genético para optimizar los pesos de las funciones heurísticas. Este incluye:

- Inicialización de población
- Selección
- Cruce
- Mutación
- Elitismo
- Evaluación mediante partidas simuladas

## Estructura del proyecto

```

TresEnRaya-main/
│
├── AgenteIA/
│   ├── Agente.py
│   ├── AgenteBuscador.py
│   ├── AgenteJugador.py
│   ├── AgentePSR.py
│   ├── Entorno.py
│   └── **init**.py
│
├── AgenteNEnRaya3D.py
├── GeneticoNEnRaya3D.py
├── Othello.py
├── Tablero3D.py
├── main_othello.py
├── main_3d_vs_ia.py
├── experimentos.py
├── test_3d.py
├── test_ag_3d.py
├── README.md
└── requirements.txt

```

## Requisitos

- Python 3.10 o superior
- Librerías necesarias:
  - matplotlib

Instalación:

```

pip install -r requirements.txt

```

Contenido sugerido de requirements.txt:

```

matplotlib>=3.7

```

## Ejecución

### Ejecutar Othello

```

python main_othello.py

```

Opciones disponibles:
- Jugar contra la IA
- IA vs IA
- Ejecutar algoritmo genético

### Ejecutar Tic-Tac-Toe 3D contra la IA

```

python main_3d_vs_ia.py

```

Formato de entrada de jugadas:
```

x,y,z

```

Ejemplo:
```

1,1,1

```

### Ejecutar algoritmo genético para 3D

```

python GeneticoNEnRaya3D.py

```

### Ejecutar experimentos

```

python experimentos.py

```

Este módulo permite comparar el rendimiento entre distintos agentes.

## Pruebas

Se incluyen pruebas básicas para el juego 3D:

```

python test_3d.py
python test_ag_3d.py

```

Se recomienda complementar con pruebas adicionales para Othello.

## Resultados esperados

- Los agentes optimizados mediante algoritmo genético deben superar a agentes aleatorios.
- En algunos casos, los agentes optimizados superan a los de pesos manuales.
- Las gráficas de convergencia muestran la evolución del fitness a lo largo de las generaciones.

## Archivos generados

Dependiendo de la ejecución, se pueden generar:

- mejores_pesos_othello.json
- mejores_pesos_3d.json
- convergencia_othello.png
- convergencia_3d.png

## Limitaciones

- El costo computacional del algoritmo Minimax crece exponencialmente con la profundidad.
- La calidad del agente depende fuertemente de la heurística.
- El algoritmo genético requiere múltiples ejecuciones para encontrar buenos resultados.

## Trabajo futuro

- Incorporar más pruebas unitarias
- Mejorar la arquitectura común entre juegos
- Optimizar la búsqueda con técnicas adicionales
- Explorar enfoques de aprendizaje automático

## Autores

María José Murillo Mendoza
Laura Camacho Lipa
Andres Revollo Almendras

