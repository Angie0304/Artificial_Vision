import random
import math
from typing import List, Optional, Tuple
import matplotlib.colors as mcolors

# Función auxiliar para convertir cualquier formato de color aceptado a RGB (tupla de flotantes 0-1)
def _to_rgb(color_input: str) -> Tuple[float, float, float]:
    """
    Convierte una entrada de color (nombre, hex, tupla RGB) a una tupla RGB de flotantes (0-1).
    """
    try:
        # Intenta convertir nombres de color, hexadecimales o tuplas RGB (0-1)
        return mcolors.to_rgb(color_input)
    except ValueError:
        # Si es una cadena de tupla RGB (0-255) como '(255, 0, 0)', la convierte
        if isinstance(color_input, str) and color_input.startswith('(') and color_input.endswith(')'):
            parts = color_input.strip('()').split(',')
            if len(parts) == 3:
                try:
                    r, g, b = float(parts[0])/255, float(parts[1])/255, float(parts[2])/255
                    return (r, g, b)
                except ValueError:
                    pass
        raise ValueError(f"Formato de color no reconocido: '{color_input}'. Debe ser un nombre (ej. 'red'), un código hexadecimal (ej. '#RRGGBB'), o una tupla RGB (ej. '(0.5, 0.5, 0.5)' para 0-1, o '(255, 128, 0)' para 0-255).")

# Función auxiliar para convertir RGB (tupla de flotantes 0-1) a cadena hexadecimal
def _to_hex(rgb_color: Tuple[float, float, float]) -> str:
    """
    Convierte una tupla RGB de flotantes (0-1) a una cadena hexadecimal (#RRGGBB).
    """
    return mcolors.to_hex(rgb_color)

# Calcula la distancia euclidiana entre dos colores en el espacio RGB (normalizada a 0-1)
def _rgb_distance(rgb1: Tuple[float, float, float], rgb2: Tuple[float, float, float]) -> float:
    """
    Calcula la distancia euclidiana entre dos colores RGB (normalizada a 0-1).
    La distancia máxima posible es sqrt(3), por lo que se divide por sqrt(3) para normalizar.
    """
    return math.sqrt(
        (rgb1[0] - rgb2[0])**2 +
        (rgb1[1] - rgb2[1])**2 +
        (rgb1[2] - rgb2[2])**2
    ) / math.sqrt(3)

# Convierte un color RGB (0-1) a HSL (Hue, Saturation, Lightness), todos en el rango [0, 1]
def _rgb_to_hsl(rgb: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Convierte una tupla RGB (0-1) a HSL (Hue, Saturation, Lightness).
    H, S, L están todos en el rango [0, 1].
    """
    r, g, b = rgb
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    h, s, l = 0, 0, (max_val + min_val) / 2

    if max_val == min_val:
        h = s = 0  # Color acromático (gris)
    else:
        d = max_val - min_val
        s = l > 0.5 and d / (2 - max_val - min_val) or d / (max_val + min_val)
        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        elif max_val == b:
            h = (r - g) / d + 4
        h /= 6
    return (h, s, l)

# Convierte un color HSL (0-1) a RGB (0-1)
def _hsl_to_rgb(hsl: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Convierte una tupla HSL (0-1) a RGB (0-1).
    """
    h, s, l = hsl
    if s == 0:
        return (l, l, l) # Color acromático (gris)
    
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    q = l < 0.5 and l * (1 + s) or l + s - l * s
    p = 2 * l - q
    r = hue_to_rgb(p, q, h + 1/3)
    g = hue_to_rgb(p, q, h)
    b = hue_to_rgb(p, q, h - 1/3)
    return (r, g, b)


def generar_color_para_scatter(
    colores_existentes: Optional[List[str]] = None,
    modo: str = 'disimilar',
    tolerancia_similitud: float = 0.2, # 0.0 (muy similar) a 1.0 (muy diferente)
    color_forzado: Optional[str] = None
) -> str:
    """
    Genera un color aleatorio compatible con matplotlib.pyplot.scatter,
    considerando colores existentes y modos de generación.

    ENTRADAS:
    colores_existentes (Optional[List[str]]): Lista de colores ya utilizados.
                                               Pueden ser nombres de colores (ej. 'red'),
                                               códigos hexadecimales (ej. '#RRGGBB'),
                                               o tuplas RGB (ej. '(0.5, 0.5, 0.5)' para 0-1,
                                               o '(255, 128, 0)' para 0-255).
                                               El formato de las entradas debe ser el mismo que el de la salida.
    modo (str): El modo de generación de color. Opciones:
                - 'disimilar': Genera un color que sea lo más diferente posible
                               a los colores existentes. Ideal para distinguir grupos.
                - 'combinar': Genera un color que "combine" con los colores
                              existentes (similar en paleta). Ideal para subgrupos
                              o variaciones dentro de un tema.
                - 'primario_nuevo': Si no hay colores existentes, usa colores
                                    primarios predefinidos. Si hay, busca un
                                    primario no usado que sea distinto.
                - 'forzar': Fuerza un color específico (usando color_forzado)
                            y lo convierte al formato de salida.
    tolerancia_similitud (float): Un valor entre 0.0 y 1.0 que controla la
                                  similitud/diferencia.
                                  - En modo 'disimilar': Un valor más alto busca colores
                                    más diferentes.
                                  - En modo 'combinar': Un valor más alto permite más
                                    variación del color base (menos "combinación" estricta,
                                    más variedad dentro de la paleta).
    color_forzado (Optional[str]): El color a forzar si el modo es 'forzar'.
                                   Puede ser un nombre, hex o tupla RGB.

    SALIDA:
    str: El color generado en formato hexadecimal (#RRGGBB), que es aceptado
         directamente por `plt.scatter`.
    """

    # Colores primarios/distintos predefinidos (ciclo de color por defecto de Matplotlib)
    colores_primarios_base = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # Convierte los colores existentes a la representación interna RGB (flotantes 0-1)
    existing_rgbs = []
    if colores_existentes:
        for c in colores_existentes:
            try:
                existing_rgbs.append(_to_rgb(c))
            except ValueError as e:
                print(f"Advertencia: No se pudo convertir el color '{c}'. Ignorando. Error: {e}")
                continue

    # Si no se ingresaron colores existentes y el modo no es 'forzar', inicia con los primarios
    if not existing_rgbs and modo != 'forzar':
        modo = 'primario_nuevo'

    if modo == 'forzar':
        if not color_forzado:
            raise ValueError("El modo 'forzar' requiere que se especifique 'color_forzado'.")
        return _to_hex(_to_rgb(color_forzado))

    elif modo == 'primario_nuevo':
        for primary_hex in colores_primarios_base:
            primary_rgb = _to_rgb(primary_hex)
            is_new = True
            for existing_rgb in existing_rgbs:
                # Comprueba si el color primario es demasiado similar a alguno existente
                # Se usa un umbral fijo para asegurar la distinción de los colores primarios
                if _rgb_distance(primary_rgb, existing_rgb) < 0.1: # Umbral de distancia para considerarlo "nuevo"
                    is_new = False
                    break
            if is_new:
                return primary_hex
        
        # Si todos los colores primarios base han sido utilizados o son demasiado similares,
        # se intenta generar un color disimilar como alternativa.
        print("Advertencia: Todos los colores primarios base han sido utilizados o son similares a los existentes. Intentando generar un color disimilar como alternativa.")
        return generar_color_para_scatter(colores_existentes, 'disimilar', tolerancia_similitud=0.7)


    elif modo == 'disimilar':
        num_attempts = 500 # Número de intentos para encontrar un color disimilar
        best_color_rgb = None
        max_min_distance = -1 # La distancia mínima más grande encontrada hasta ahora

        if not existing_rgbs:
            # Si no hay colores existentes, devuelve un color aleatorio brillante por defecto
            return _to_hex(_hsl_to_rgb((random.random(), 0.8 + random.random()*0.2, 0.5 + random.random()*0.3)))

        for _ in range(num_attempts):
            # Genera un color RGB aleatorio
            r, g, b = random.random(), random.random(), random.random()
            current_rgb = (r, g, b)

            # Calcula la distancia mínima a cualquier color existente
            min_distance_to_existing = float('inf')
            for existing_rgb in existing_rgbs:
                dist = _rgb_distance(current_rgb, existing_rgb)
                min_distance_to_existing = min(min_distance_to_existing, dist)
            
            # Si este color está más lejos de su vecino existente más cercano
            # y cumple con la tolerancia de similitud (escalada por la distancia máxima posible)
            if min_distance_to_existing > max_min_distance and \
               min_distance_to_existing >= tolerancia_similitud * 0.4: # 0.4 es un factor para la 'distinción'
                max_min_distance = min_distance_to_existing
                best_color_rgb = current_rgb
        
        if best_color_rgb:
            return _to_hex(best_color_rgb)
        else:
            # Si no se encuentra un color disimilar adecuado después de muchos intentos,
            # se genera un color aleatorio con alta saturación y luminosidad para asegurar que sea "bonito".
            print("Advertencia: No se encontró un color disimilar adecuado después de varios intentos. Generando un color aleatorio con alta saturación y luminosidad.")
            return _to_hex(_hsl_to_rgb((random.random(), 0.8 + random.random()*0.2, 0.5 + random.random()*0.3)))


    elif modo == 'combinar':
        if not existing_rgbs:
            print("Advertencia: No hay colores existentes para 'combinar'. Volviendo al modo 'primario_nuevo'.")
            return generar_color_para_scatter(colores_existentes, 'primario_nuevo', tolerancia_similitud)
        
        # Elige un color existente aleatorio como base para el nuevo color
        base_rgb = random.choice(existing_rgbs)
        base_hsl = _rgb_to_hsl(base_rgb)
        
        new_rgb = None
        attempts = 0
        max_attempts = 50 # Limita los intentos para evitar bucles infinitos

        while new_rgb is None and attempts < max_attempts:
            # Perturba los componentes HSL basándose en tolerancia_similitud
            # Una tolerancia_similitud más pequeña significa menos perturbación (más similar)
            
            # Perturbación del tono (colores análogos)
            # Cambio máximo de tono: +/- 0.15 (aprox. 54 grados) para tolerancia_similitud = 1.0
            hue_change = (random.random() * 2 - 1) * 0.15 * tolerancia_similitud
            new_h = (base_hsl[0] + hue_change) % 1.0
            
            # Perturbación de la saturación
            # Cambio máximo de saturación: +/- 0.4 para tolerancia_similitud = 1.0
            sat_change = (random.random() * 2 - 1) * 0.4 * tolerancia_similitud
            new_s = max(0.0, min(1.0, base_hsl[1] + sat_change))
            
            # Perturbación de la luminosidad (tintes/sombras)
            # Cambio máximo de luminosidad: +/- 0.3 para tolerancia_similitud = 1.0
            light_change = (random.random() * 2 - 1) * 0.3 * tolerancia_similitud
            new_l = max(0.0, min(1.0, base_hsl[2] + light_change))
            
            perturbed_hsl = (new_h, new_s, new_l)
            candidate_rgb = _hsl_to_rgb(perturbed_hsl)

            # Asegura que el color candidato no sea demasiado similar a ningún color existente
            # para mantener la distinción, incluso si su objetivo es "combinar".
            min_dist_to_existing = float('inf')
            for existing_rgb in existing_rgbs:
                min_dist_to_existing = min(min_dist_to_existing, _rgb_distance(candidate_rgb, existing_rgb))
            
            # Si el candidato es suficientemente distinto (ej. distancia > 0.08), se acepta
            # O si es el primer intento, se acepta directamente.
            if min_dist_to_existing > 0.08 or attempts == 0: # Umbral de distinción
                new_rgb = candidate_rgb
            
            attempts += 1
        
        if new_rgb:
            return _to_hex(new_rgb)
        else:
            print("Advertencia: No se pudo generar un color de 'combinación' suficientemente distinto. Generando un color disimilar como alternativa.")
            return generar_color_para_scatter(colores_existentes, 'disimilar', tolerancia_similitud)

    else:
        raise ValueError("Modo no válido. Las opciones son 'disimilar', 'combinar', 'primario_nuevo', 'forzar'.")

