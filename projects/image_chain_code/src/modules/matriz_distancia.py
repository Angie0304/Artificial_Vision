"""
Clase MatrizDistancias optimizada con soporte completo para PuntoImagen.

NUEVO: SOPORTE PARA PUNTOS DE IMAGEN
- PuntoImagen: Usa color_RGB (3D) para cálculos de distancia
- Coordenadas (2D) se usan solo como identificador/localización
- Detección automática del tipo de punto
- Soporte para mezcla de Punto y PuntoImagen en la misma matriz

CARACTERÍSTICAS EXISTENTES:
- Cálculo una sola vez usando scipy (implementación en C)
- Soporte para puntos N-dimensionales
- Múltiples métricas de distancia configurables
- Búsquedas O(1) de distancias precalculadas
- Gestión eficiente de memoria para grandes conjuntos de datos
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from typing import List, Union, Optional, Tuple, Dict, Any
import time
from modules.punto import Punto, PuntoImagen
from utils.funciones_estandar_V2 import cronometro


class MatrizDistancias:
    """
    Clase optimizada para cálculo y consulta eficiente de distancias entre puntos N-dimensionales.
    
    NUEVO: SOPORTE COMPLETO PARA PUNTOS DE IMAGEN
    - PuntoImagen: Usa color_RGB para distancias, coordenadas como ID
    - Punto: Usa coordenadas para distancias (comportamiento normal)
    - Detección automática y mezcla de tipos soportada
    
    RENDIMIENTO OPTIMIZADO:
    - Cálculo una sola vez usando scipy.spatial.distance (implementado en C)
    - Búsquedas O(1) usando indexación y hashing
    - Memoria eficiente para grandes conjuntos de datos
    - Soporte para puntos N-dimensionales
    
    MÉTRICAS SOPORTADAS:
    - 'euclidean': Distancia euclidiana (por defecto)
    - 'manhattan': Distancia de Manhattan (L1)
    - 'chebyshev': Distancia de Chebyshev (L∞)
    - 'minkowski': Distancia de Minkowski (configurable p)
    - 'cosine': Similitud coseno
    - Y todas las métricas de scipy.spatial.distance
    """
    
    # Métricas disponibles con descripción
    METRICAS_DISPONIBLES = {
        'euclidean': 'Distancia euclidiana estándar',
        'manhattan': 'Distancia de Manhattan (suma de diferencias absolutas)',
        'chebyshev': 'Distancia de Chebyshev (máxima diferencia)',
        'minkowski': 'Distancia de Minkowski generalizada',
        'cosine': 'Distancia basada en similitud coseno',
        'hamming': 'Distancia de Hamming (para datos binarios)',
        'jaccard': 'Distancia de Jaccard',
        'correlation': 'Distancia de correlación'
    }
    
    def __init__(self, 
                 puntos: List[Union[Punto, PuntoImagen, List[float], Tuple[float, ...], np.ndarray]], 
                 metrica: str = 'euclidean',
                 **kwargs):
        """
        Inicializa la matriz de distancias calculando todas las distancias una sola vez.
        
        NUEVO: Soporte automático para PuntoImagen
        - PuntoImagen: Distancias calculadas usando color_RGB (3D)
        - Punto: Distancias calculadas usando coordenadas (N-D)
        - Mezcla: Convierte automáticamente para compatibilidad
        
        Args:
            puntos: Lista de puntos (Punto, PuntoImagen, listas, tuplas o arrays numpy)
            metrica: Métrica de distancia a usar ('euclidean', 'manhattan', etc.)
            **kwargs: Parámetros adicionales para la métrica (ej: p=3 para Minkowski)
            
        Raises:
            ValueError: Si la métrica no es válida o los puntos tienen dimensiones inconsistentes
            
        Examples:
            >>> # Solo Punto normales
            >>> puntos = [Punto([0, 0]), Punto([1, 1])]
            >>> matriz = MatrizDistancias(puntos)
            
            >>> # Solo PuntoImagen (distancia por color)
            >>> puntos_img = [PuntoImagen([10, 20], [255, 0, 0]), 
            ...                PuntoImagen([30, 40], [0, 255, 0])]
            >>> matriz = MatrizDistancias(puntos_img)
            
            >>> # Mezcla automática (convierte Punto a espacio de color)
            >>> puntos_mixtos = [Punto([0, 0, 128]), PuntoImagen([10, 20], [255, 0, 0])]
            >>> matriz = MatrizDistancias(puntos_mixtos)
        """
        self.metrica = metrica
        self.kwargs_metrica = kwargs
        
        # Validar métrica
        if metrica not in self.METRICAS_DISPONIBLES:
            raise ValueError(f"Métrica '{metrica}' no soportada. "
                           f"Disponibles: {list(self.METRICAS_DISPONIBLES.keys())}")
        
        # Procesar y validar puntos
        self.puntos_originales = puntos
        self.puntos_normalizados = self._procesar_puntos(puntos)
        
        # NUEVO: Detectar tipo predominante y extraer datos apropiados
        self._analizar_tipos_puntos()
        self.coordenadas_calculo = self._extraer_coordenadas_calculo()
        self.coordenadas_identificacion = self._extraer_coordenadas_identificacion()
        
        # Validar dimensionalidad consistente
        self._validar_dimensiones()
        
        # Calcular matriz de distancias UNA SOLA VEZ
        self._calcular_matriz_distancias()
        
        # Crear índices para búsquedas eficientes O(1)
        self._crear_indices_busqueda()
        
        print(f"MatrizDistancias inicializada:")
        print(f"  - {len(self.puntos_normalizados)} puntos")
        print(f"  - Tipo predominante: {self.tipo_puntos}")
        print(f"  - Dimensión cálculo: {self.dimension_calculo}")
        print(f"  - Dimensión ID: {self.dimension_identificacion}")
        print(f"  - Métrica: {self.metrica}")
        print(f"  - Distancias únicas: {len(self.distancias_unicas)}")
    
    def _procesar_puntos(self, puntos: List) -> List[Union[Punto, PuntoImagen]]:
        """Convierte todos los puntos a objetos Punto o PuntoImagen normalizados"""
        puntos_procesados = []
        
        for i, punto in enumerate(puntos):
            if isinstance(punto, (Punto, PuntoImagen)):
                puntos_procesados.append(punto)
            elif isinstance(punto, (list, tuple, np.ndarray)):
                # Convertir a objeto Punto normal
                puntos_procesados.append(Punto(punto, etiqueta=f"Punto_{i}"))
            else:
                raise ValueError(f"Tipo de punto no soportado en índice {i}: {type(punto)}")
        
        return puntos_procesados
    
    def _analizar_tipos_puntos(self):
        """
        Analiza los tipos de puntos y determina el modo de operación.
        
        LÓGICA:
        1. Solo PuntoImagen -> Modo imagen (distancias por color_RGB)
        2. Solo Punto -> Modo normal (distancias por coordenadas)
        3. Mixto -> Modo híbrido (conversión automática)
        """
        puntos_imagen = sum(1 for p in self.puntos_normalizados if isinstance(p, PuntoImagen))
        puntos_normales = len(self.puntos_normalizados) - puntos_imagen
        
        if puntos_imagen == len(self.puntos_normalizados):
            self.tipo_puntos = "imagen"
            self.modo_calculo = "color_RGB"
        elif puntos_normales == len(self.puntos_normalizados):
            self.tipo_puntos = "normal"
            self.modo_calculo = "coordenadas"
        else:
            self.tipo_puntos = "mixto"
            self.modo_calculo = "hibrido"
            self._convertir_puntos_mixtos()
    
    def _convertir_puntos_mixtos(self):
        """
        Convierte puntos mixtos para compatibilidad.
        
        ESTRATEGIA:
        - Si Punto tiene 3D -> Interpretar como color RGB
        - Si Punto tiene != 3D -> Expandir/contraer a RGB
        - PuntoImagen mantiene su color_RGB
        """
        puntos_convertidos = []
        
        for punto in self.puntos_normalizados:
            if isinstance(punto, PuntoImagen):
                puntos_convertidos.append(punto)
            elif isinstance(punto, Punto):
                # Convertir Punto a formato compatible con color
                if punto.dimension == 3:
                    # Asumir que ya es RGB
                    color_rgb = punto.coordenadas
                    coords_2d = [0, 0]  # Coordenadas dummy
                else:
                    # Convertir dimensión a RGB
                    color_rgb = self._expandir_a_rgb(punto.coordenadas)
                    coords_2d = punto.coordenadas[:2] if punto.dimension >= 2 else [punto.coordenadas[0], 0]
                
                # Crear PuntoImagen equivalente
                punto_convertido = PuntoImagen(
                    coordenadas=coords_2d,
                    color_RGB=color_rgb,
                    color_visualizacion=punto.color,
                    etiqueta=punto.etiqueta or f"Convertido_{len(puntos_convertidos)}"
                )
                puntos_convertidos.append(punto_convertido)
        
        self.puntos_normalizados = puntos_convertidos
        print(f"Convertidos {len([p for p in self.puntos_originales if isinstance(p, Punto)])} Punto(s) a formato PuntoImagen")
    
    def _expandir_a_rgb(self, coordenadas: np.ndarray) -> np.ndarray:
        """
        Expande coordenadas de cualquier dimensión a RGB (3D).
        
        ESTRATEGIAS:
        - 1D: [x] -> [x, x, x]
        - 2D: [x, y] -> [x, y, 0]
        - 3D: [x, y, z] -> [x, y, z] (sin cambio)
        - >3D: [x, y, z, ...] -> [x, y, z] (truncar)
        """
        if len(coordenadas) == 1:
            return np.array([coordenadas[0], coordenadas[0], coordenadas[0]])
        elif len(coordenadas) == 2:
            return np.array([coordenadas[0], coordenadas[1], 0])
        elif len(coordenadas) == 3:
            return coordenadas.copy()
        else:
            return coordenadas[:3]  # Truncar a 3D
    
    def _extraer_coordenadas_calculo(self) -> np.ndarray:
        """
        Extrae coordenadas para cálculo de distancias según el tipo de punto.
        
        LÓGICA:
        - PuntoImagen: Usa color_RGB (3D)
        - Punto: Usa coordenadas (N-D)
        - Mixto: Todos convertidos a PuntoImagen, usa color_RGB
        """
        if self.tipo_puntos in ["imagen", "mixto"]:
            # Usar color_RGB para cálculos
            return np.array([punto.color_RGB for punto in self.puntos_normalizados])
        else:
            # Usar coordenadas normales
            return np.array([punto.coordenadas for punto in self.puntos_normalizados])
    
    def _extraer_coordenadas_identificacion(self) -> np.ndarray:
        """
        Extrae coordenadas para identificación/búsqueda de puntos.
        Siempre usa las coordenadas originales como ID.
        """
        return np.array([punto.coordenadas for punto in self.puntos_normalizados])
    
    def _validar_dimensiones(self):
        """Valida que todos los puntos tengan dimensionalidad consistente para cálculos"""
        if len(self.coordenadas_calculo) == 0:
            raise ValueError("La lista de puntos no puede estar vacía")
        
        # Validar dimensiones para cálculo
        dimensiones_calculo = [len(coords) for coords in self.coordenadas_calculo]
        self.dimension_calculo = dimensiones_calculo[0]
        
        if not all(dim == self.dimension_calculo for dim in dimensiones_calculo):
            raise ValueError(f"Todos los puntos deben tener la misma dimensión para cálculo. "
                           f"Encontradas dimensiones: {set(dimensiones_calculo)}")
        
        # Validar dimensiones para identificación
        dimensiones_id = [len(coords) for coords in self.coordenadas_identificacion]
        self.dimension_identificacion = dimensiones_id[0]
        
        # Información adicional para depuración
        if self.tipo_puntos == "imagen":
            print(f"  Modo imagen: Distancias por color_RGB ({self.dimension_calculo}D), IDs por coordenadas ({self.dimension_identificacion}D)")
        elif self.tipo_puntos == "mixto":
            print(f"  Modo híbrido: Puntos convertidos a formato imagen")
    
    @cronometro
    def _calcular_matriz_distancias(self):
        """
        Calcula la matriz de distancias completa usando scipy (muy eficiente).
        
        ALGORITMO:
        1. scipy.spatial.distance.pdist: Calcula distancias condensadas (triángulo superior)
        2. squareform: Convierte a matriz simétrica completa
        3. Extrae distancias únicas del triángulo superior
        
        NUEVO: Usa coordenadas_calculo (color_RGB para PuntoImagen)
        """
        try:
            # pdist calcula distancias de forma muy eficiente (implementado en C)
            # NUEVO: Usa coordenadas_calculo en lugar de coordenadas normales
            distancias_condensadas = pdist(self.coordenadas_calculo, 
                                         metric=self.metrica, 
                                         **self.kwargs_metrica)
            
            # Convertir a matriz cuadrada simétrica
            self.matriz_distancias = squareform(distancias_condensadas)
            
            # Extraer distancias únicas (excluyendo diagonal de ceros)
            # Usar solo triángulo superior para evitar duplicados
            mascara_triangulo_superior = np.triu(np.ones_like(self.matriz_distancias, dtype=bool), k=1)
            distancias_no_duplicadas = self.matriz_distancias[mascara_triangulo_superior]
            
            # Obtener valores únicos y ordenarlos
            self.distancias_unicas = np.unique(distancias_no_duplicadas)
            
        except Exception as e:
            raise RuntimeError(f"Error al calcular matriz de distancias: {e}")
    
    def _crear_indices_busqueda(self):
        """
        Crea índices para búsquedas O(1) eficientes.
        
        NUEVO: Usa coordenadas de identificación para búsqueda, no las de cálculo
        
        ESTRUCTURAS DE DATOS:
        1. Diccionario punto -> índice para localización rápida
        2. Diccionario coordenadas_id -> índice para búsqueda alternativa
        """
        # Mapeo de punto a índice en la matriz
        self.punto_a_indice = {}
        
        for i, punto in enumerate(self.puntos_normalizados):
            # Usar el objeto punto como clave
            self.punto_a_indice[punto] = i
            
            # NUEVO: También crear entrada para coordenadas de identificación
            coords_id_tuple = tuple(punto.coordenadas)  # Siempre usar coordenadas como ID
            self.punto_a_indice[coords_id_tuple] = i
    
    def obtener_distancias_unicas_ordenadas(self) -> List[float]:
        """
        Devuelve lista de todas las distancias únicas ordenadas de menor a mayor.
        
        Returns:
            Lista de distancias únicas ordenadas ascendentemente
            
        Examples:
            >>> # Para PuntoImagen, distancias son entre colores RGB
            >>> p1 = PuntoImagen([0, 0], [255, 0, 0])    # Rojo
            >>> p2 = PuntoImagen([10, 10], [0, 255, 0])  # Verde
            >>> matriz = MatrizDistancias([p1, p2])
            >>> distancias = matriz.obtener_distancias_unicas_ordenadas()
            >>> print(distancias)  # [360.62] (distancia euclidiana en RGB)
        """
        return self.distancias_unicas.tolist()
    
    def obtener_distancia(self, 
                         punto1: Union[Punto, PuntoImagen, List[float], Tuple[float, ...]], 
                         punto2: Union[Punto, PuntoImagen, List[float], Tuple[float, ...]]) -> float:
        """
        Obtiene la distancia precalculada entre dos puntos de forma eficiente O(1).
        
        NUEVO: Para PuntoImagen, la distancia se calcula usando color_RGB,
        pero la búsqueda se hace usando coordenadas como identificador.
        
        Args:
            punto1: Primer punto (objeto Punto/PuntoImagen o coordenadas de identificación)
            punto2: Segundo punto (objeto Punto/PuntoImagen o coordenadas de identificación)
            
        Returns:
            Distancia precalculada entre los puntos (calculada usando color_RGB si son PuntoImagen)
            
        Raises:
            ValueError: Si alguno de los puntos no fue incluido en la inicialización
            
        Examples:
            >>> # Distancia entre colores RGB (no coordenadas espaciales)
            >>> p1 = PuntoImagen([0, 0], [255, 0, 0])    # Rojo en (0,0)
            >>> p2 = PuntoImagen([100, 100], [255, 0, 1]) # Casi rojo en (100,100)
            >>> matriz = MatrizDistancias([p1, p2])
            >>> distancia = matriz.obtener_distancia(p1, p2)  # ≈1.0 (diferencia en RGB)
            >>> # Nota: La ubicación espacial (0,0) vs (100,100) NO afecta la distancia
        """
        # Convertir puntos para búsqueda (usando coordenadas como ID)
        punto1_norm = self._normalizar_punto_busqueda(punto1)
        punto2_norm = self._normalizar_punto_busqueda(punto2)
        
        # Obtener índices
        try:
            indice1 = self._obtener_indice_punto(punto1_norm)
            indice2 = self._obtener_indice_punto(punto2_norm)
        except KeyError as e:
            raise ValueError(f"Punto no encontrado en la matriz: {e}")
        
        # Retornar distancia precalculada (acceso O(1))
        # NOTA: Esta distancia fue calculada usando color_RGB si son PuntoImagen
        return float(self.matriz_distancias[indice1, indice2])
    
    def _normalizar_punto_busqueda(self, punto) -> Union[Punto, PuntoImagen, Tuple]:
        """
        Normaliza un punto para búsqueda en el índice.
        NUEVO: Mantiene compatibilidad con PuntoImagen
        """
        if isinstance(punto, (Punto, PuntoImagen)):
            return punto
        elif isinstance(punto, (list, tuple, np.ndarray)):
            # Usar coordenadas como tuple para búsqueda por ID
            return tuple(np.array(punto, dtype=float))
        else:
            raise ValueError(f"Tipo de punto no soportado para búsqueda: {type(punto)}")
    
    def _obtener_indice_punto(self, punto_normalizado) -> int:
        """
        Obtiene el índice de un punto en la matriz.
        NUEVO: Búsqueda compatible con PuntoImagen
        """
        if punto_normalizado in self.punto_a_indice:
            return self.punto_a_indice[punto_normalizado]
        
        # Búsqueda alternativa por aproximación (para manejar errores de punto flotante)
        if isinstance(punto_normalizado, tuple):
            coords_busqueda = np.array(punto_normalizado)
            for i, punto_almacenado in enumerate(self.puntos_normalizados):
                # Comparar usando coordenadas de identificación
                if np.allclose(coords_busqueda, punto_almacenado.coordenadas, rtol=1e-10):
                    return i
        
        raise KeyError(f"Punto no encontrado: {punto_normalizado}")
    
    # ══════════════════════════════════════════════════════════════════════════════
    # MÉTODOS ADICIONALES CON SOPORTE PARA PUNTOS DE IMAGEN
    # ══════════════════════════════════════════════════════════════════════════════
    
    def obtener_punto_mas_cercano_por_color(self, 
                                           color_referencia: Union[List[float], Tuple[float, ...], np.ndarray]) -> Tuple[Union[Punto, PuntoImagen], float]:
        """
        NUEVO: Encuentra el punto con el color más cercano a un color de referencia.
        Útil para PuntoImagen - busca por similitud de color independientemente de la ubicación.
        
        Args:
            color_referencia: Color RGB de referencia [R, G, B]
            
        Returns:
            Tupla (punto_mas_cercano, distancia_color)
        """
        if self.tipo_puntos == "normal":
            raise ValueError("Este método requiere PuntoImagen. Use obtener_punto_mas_cercano() para Punto normales.")
        
        color_ref = np.array(color_referencia, dtype=float)
        
        # Calcular distancias a todos los colores
        distancias_color = []
        for punto in self.puntos_normalizados:
            if isinstance(punto, PuntoImagen):
                dist = np.linalg.norm(color_ref - punto.color_RGB)
            else:
                # Punto convertido, usar coordenadas como color
                dist = np.linalg.norm(color_ref - punto.coordenadas[:3])
            distancias_color.append(dist)
        
        # Encontrar el mínimo
        indice_minimo = np.argmin(distancias_color)
        return self.puntos_normalizados[indice_minimo], float(distancias_color[indice_minimo])
    
    def obtener_punto_mas_cercano(self, punto_referencia: Union[Punto, PuntoImagen, List[float]]) -> Tuple[Union[Punto, PuntoImagen], float]:
        """
        Encuentra el punto más cercano a un punto de referencia.
        
        NUEVO: Para PuntoImagen, usa distancia de color, no espacial.
        
        Args:
            punto_referencia: Punto de referencia
            
        Returns:
            Tupla (punto_mas_cercano, distancia_minima)
        """
        punto_norm = self._normalizar_punto_busqueda(punto_referencia)
        indice_ref = self._obtener_indice_punto(punto_norm)
        
        # Obtener fila de distancias (excluyendo el mismo punto)
        distancias_fila = self.matriz_distancias[indice_ref].copy()
        distancias_fila[indice_ref] = np.inf  # Excluir el mismo punto
        
        # Encontrar índice del mínimo
        indice_mas_cercano = np.argmin(distancias_fila)
        distancia_minima = distancias_fila[indice_mas_cercano]
        
        return self.puntos_normalizados[indice_mas_cercano], float(distancia_minima)
    
    def obtener_k_mas_cercanos(self, punto_referencia: Union[Punto, PuntoImagen, List[float]], k: int) -> List[Tuple[Union[Punto, PuntoImagen], float]]:
        """
        Encuentra los k puntos más cercanos a un punto de referencia.
        
        NUEVO: Para PuntoImagen, proximidad basada en color_RGB.
        
        Args:
            punto_referencia: Punto de referencia
            k: Número de puntos más cercanos a encontrar
            
        Returns:
            Lista de tuplas [(punto, distancia)] ordenada por distancia
        """
        punto_norm = self._normalizar_punto_busqueda(punto_referencia)
        indice_ref = self._obtener_indice_punto(punto_norm)
        
        # Obtener distancias y excluir el mismo punto
        distancias_fila = self.matriz_distancias[indice_ref].copy()
        distancias_fila[indice_ref] = np.inf
        
        # Obtener k índices más cercanos
        indices_k_cercanos = np.argpartition(distancias_fila, k)[:k]
        
        # Crear lista de resultados
        resultado = []
        for indice in indices_k_cercanos:
            punto = self.puntos_normalizados[indice]
            distancia = float(distancias_fila[indice])
            resultado.append((punto, distancia))
        
        # Ordenar por distancia
        resultado.sort(key=lambda x: x[1])
        
        return resultado
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la matriz de distancias.
        
        Returns:
            Diccionario con estadísticas detalladas incluyendo info sobre tipos de punto
        """
        # Obtener todas las distancias (excluyendo diagonal)
        mask = np.triu(np.ones_like(self.matriz_distancias, dtype=bool), k=1)
        todas_distancias = self.matriz_distancias[mask]
        
        # Contar tipos de puntos
        num_punto_imagen = sum(1 for p in self.puntos_normalizados if isinstance(p, PuntoImagen))
        num_punto_normal = len(self.puntos_normalizados) - num_punto_imagen
        
        stats = {
            'num_puntos': len(self.puntos_normalizados),
            'num_punto_imagen': num_punto_imagen,
            'num_punto_normal': num_punto_normal,
            'tipo_puntos': self.tipo_puntos,
            'modo_calculo': self.modo_calculo,
            'dimension_calculo': self.dimension_calculo,
            'dimension_identificacion': self.dimension_identificacion,
            'metrica': self.metrica,
            'num_distancias_totales': len(todas_distancias),
            'num_distancias_unicas': len(self.distancias_unicas),
            'distancia_minima': float(np.min(todas_distancias)),
            'distancia_maxima': float(np.max(todas_distancias)),
            'distancia_media': float(np.mean(todas_distancias)),
            'distancia_mediana': float(np.median(todas_distancias)),
            'desviacion_estandar': float(np.std(todas_distancias))
        }
        
        return stats
    
    def cambiar_metrica(self, nueva_metrica: str, **kwargs):
        """
        Cambia la métrica y recalcula la matriz de distancias.
        
        Args:
            nueva_metrica: Nueva métrica a usar
            **kwargs: Parámetros adicionales para la métrica
        """
        if nueva_metrica not in self.METRICAS_DISPONIBLES:
            raise ValueError(f"Métrica '{nueva_metrica}' no soportada.")
        
        print(f"Cambiando métrica de '{self.metrica}' a '{nueva_metrica}'...")
        
        self.metrica = nueva_metrica
        self.kwargs_metrica = kwargs
        
        # Recalcular matriz
        self._calcular_matriz_distancias()
        
        print("Métrica cambiada exitosamente.")
    
    def __len__(self):
        """Número de puntos en la matriz"""
        return len(self.puntos_normalizados)
    
    def __repr__(self):
        return (f"MatrizDistancias({len(self.puntos_normalizados)} puntos, "
                f"tipo={self.tipo_puntos}, dimensión_cálculo={self.dimension_calculo}, "
                f"métrica='{self.metrica}')")


# ══════════════════════════════════════════════════════════════════════════════════
# EJEMPLOS DE USO CON SOPORTE PARA PUNTOS DE IMAGEN
# ══════════════════════════════════════════════════════════════════════════════════

def ejemplo_puntos_imagen():
    """Ejemplo específico para PuntoImagen"""
    print("=== Ejemplo con PuntoImagen ===")
    
    # Crear puntos de imagen (ubicación espacial + color RGB)
    puntos_img = [
        PuntoImagen([10, 20], [255, 0, 0], etiqueta="Rojo"),      # Rojo en (10,20)
        PuntoImagen([30, 40], [0, 255, 0], etiqueta="Verde"),     # Verde en (30,40)
        PuntoImagen([50, 60], [0, 0, 255], etiqueta="Azul"),      # Azul en (50,60)
        PuntoImagen([70, 80], [255, 255, 0], etiqueta="Amarillo"), # Amarillo en (70,80)
        PuntoImagen([90, 100], [255, 0, 255], etiqueta="Magenta") # Magenta en (90,100)
    ]
    
    # Crear matriz - las distancias se calculan usando color_RGB, no coordenadas espaciales
    matriz = MatrizDistancias(puntos_img)
    
    print("\nDistancias únicas por color (no por ubicación espacial):")
    distancias_unicas = matriz.obtener_distancias_unicas_ordenadas()
    for i, dist in enumerate(distancias_unicas):
        print(f"  {i+1}: {dist:.2f}")
    
    # Consultar distancia específica
    print(f"\nDistancia Rojo -> Verde (por color): {matriz.obtener_distancia(puntos_img[0], puntos_img[1]):.2f}")
    print(f"Distancia Rojo -> Magenta (por color): {matriz.obtener_distancia(puntos_img[0], puntos_img[4]):.2f}")
    
    # Buscar color más cercano a un color específico
    color_objetivo = [128, 0, 128]  # Púrpura
    punto_cercano, dist_color = matriz.obtener_punto_mas_cercano_por_color(color_objetivo)
    print(f"\nColor más cercano a púrpura [128,0,128]: {punto_cercano.etiqueta} (distancia: {dist_color:.2f})")
    
    # Demostrar que ubicación espacial NO afecta la distancia
    print(f"\nDemostración: Ubicación espacial NO afecta distancia de color")
    print(f"Rojo está en {puntos_img[0].coordenadas}, Verde en {puntos_img[1].coordenadas}")
    print(f"Pero distancia calculada es por color RGB: {matriz.obtener_distancia(puntos_img[0], puntos_img[1]):.2f}")


def ejemplo_puntos_mixtos():
    """Ejemplo con mezcla de Punto y PuntoImagen"""
    print("\n=== Ejemplo con Puntos Mixtos ===")
    
    # Mezclar tipos: algunos Punto normales, algunos PuntoImagen
    puntos_mixtos = [
        Punto([255, 0, 0], etiqueta="Punto_Rojo_3D"),           # Se interpretará como RGB
        PuntoImagen([10, 20], [0, 255, 0], etiqueta="Verde_Imagen"),
        Punto([128, 128], etiqueta="Punto_2D"),                 # Se expandirá a RGB
        PuntoImagen([30, 40], [0, 0, 255], etiqueta="Azul_Imagen"),
    ]
    
    # La matriz automáticamente convierte para compatibilidad
    matriz = MatrizDistancias(puntos_mixtos)
    
    print("\nEstadísticas de conversión automática:")
    stats = matriz.obtener_estadisticas()
    print(f"  Tipo de matriz: {stats['tipo_puntos']}")
    print(f"  Modo de cálculo: {stats['modo_calculo']}")
    print(f"  Puntos originales convertidos a imagen: {stats['num_punto_imagen']}")
    
    # Todas las distancias son ahora por color
    print(f"\nDistancias por color después de conversión:")
    for i in range(len(puntos_mixtos)):
        for j in range(i+1, len(puntos_mixtos)):
            dist = matriz.obtener_distancia(puntos_mixtos[i], puntos_mixtos[j])
            print(f"  {puntos_mixtos[i].etiqueta} -> {puntos_mixtos[j].etiqueta}: {dist:.2f}")


def ejemplo_comparacion_metricas_imagen():
    """Ejemplo comparando métricas con PuntoImagen"""
    print("\n=== Comparación de Métricas con PuntoImagen ===")
    
    # Puntos de colores específicos
    colores_test = [
        PuntoImagen([0, 0], [255, 0, 0], etiqueta="Rojo"),
        PuntoImagen([0, 0], [0, 255, 0], etiqueta="Verde"),
        PuntoImagen([0, 0], [0, 0, 255], etiqueta="Azul"),
        PuntoImagen([0, 0], [255, 255, 255], etiqueta="Blanco"),
        PuntoImagen([0, 0], [0, 0, 0], etiqueta="Negro")
    ]
    
    metricas_test = ['euclidean', 'manhattan', 'chebyshev']
    
    for metrica in metricas_test:
        print(f"\n--- Métrica: {metrica} ---")
        matriz = MatrizDistancias(colores_test, metrica=metrica)
        
        # Comparar Rojo vs Negro con diferentes métricas
        dist_rojo_negro = matriz.obtener_distancia(colores_test[0], colores_test[4])
        print(f"Distancia Rojo -> Negro: {dist_rojo_negro:.2f}")
        
        # Mostrar algunas distancias únicas
        unicas = matriz.obtener_distancias_unicas_ordenadas()[:3]
        print(f"Primeras 3 distancias únicas: {[round(d, 2) for d in unicas]}")


if __name__ == "__main__":
    # Ejecutar ejemplos nuevos
    ejemplo_puntos_imagen()
    ejemplo_puntos_mixtos() 
    ejemplo_comparacion_metricas_imagen()