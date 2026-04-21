""" 
Algoritmo para agrupar puntos según un umbral de distancia.

Contiene:
- AlgoritmoCadena: Clase que implementa el algoritmo de cadena para agrupamiento de puntos.
- Resultados: Clase que almacena los resultados del algoritmo con grupos, umbrales e imágenes.

ALGORITMO DE LA CADENA:
1. El primer punto siempre crea el primer grupo
2. Para cada punto subsecuente:
   - Se evalúa la distancia a todos los grupos existentes
   - Si la distancia mínima es menor al umbral, se asigna al grupo más cercano
   - Si no, se crea un nuevo grupo
3. Se prueban todos los umbrales de distancia únicos posibles
4. Se almacenan resultados que cumplan con el rango de grupos deseado

COLORIZACIÓN:
- Cada grupo recibe un color único usando 'generar_color_para_scatter'
- Modo 'primario_nuevo' para máxima distinción visual
"""

from typing import List, Dict, Tuple, Set, Optional
from modules.imagen import Imagen
from modules.punto import Punto, PuntoImagen
from modules.matriz_distancia import MatrizDistancias
from modules.color import generar_color_para_scatter
import numpy as np
import random
import cv2 as cv


class Resultados:
    """
    Clase para almacenar los resultados del algoritmo de cadena.
    
    MODIFICADO: Ahora incluye estadísticas de cantidad de puntos por color/clase.

    Almacena un diccionario donde la clave es el número de grupos formados y el valor 
    es una tupla que contiene (umbral_usado, imagen_con_grupos_coloreados).
    
    Estructura: {num_grupos: (umbral, imagen_resultado)}
    
    NUEVO: También almacena estadísticas por color:
    - _estadisticas_por_umbral: {umbral: {color_hex: cantidad_puntos}}
    - _estadisticas_por_grupos: {num_grupos: {color_hex: cantidad_puntos}}
    """
    
    def __init__(self):
        self.resultados: Dict[int, Tuple[float, Imagen]] = {}
        self._grupos_por_umbral: Dict[float, List[List[PuntoImagen]]] = {}
        self._colores_por_grupo: Dict[float, List[str]] = {}
        
        # NUEVO: Estadísticas de puntos por color
        self._estadisticas_por_umbral: Dict[float, Dict[str, int]] = {}
        self._estadisticas_por_grupos: Dict[int, Dict[str, int]] = {}

    def agregar_resultado(self, 
                         num_grupos: int, 
                         umbral: float, 
                         grupos: List[List[PuntoImagen]], 
                         imagen_base: Imagen) -> None:
        """
        Agrega un resultado del algoritmo de cadena.
        
        MODIFICADO: Ahora calcula y almacena estadísticas de puntos por color.
        
        Args:
            num_grupos: Número de grupos formados
            umbral: Umbral de distancia usado
            grupos: Lista de grupos, cada grupo es una lista de PuntoImagen
            imagen_base: Imagen base sobre la cual aplicar la colorización
        """
        # Generar colores únicos para cada grupo
        colores_grupos = []
        for i in range(num_grupos):
            color = generar_color_para_scatter(
                colores_existentes=colores_grupos,
                modo='primario_nuevo'
            )
            colores_grupos.append(color)
        
        # NUEVO: Calcular estadísticas de puntos por color
        estadisticas_color = {}
        for i, grupo in enumerate(grupos):
            color_hex = colores_grupos[i]
            cantidad_puntos = len(grupo)
            estadisticas_color[color_hex] = cantidad_puntos
        
        # Almacenar información de grupos y colores
        self._grupos_por_umbral[umbral] = grupos
        self._colores_por_grupo[umbral] = colores_grupos
        
        # NUEVO: Almacenar estadísticas
        self._estadisticas_por_umbral[umbral] = estadisticas_color
        self._estadisticas_por_grupos[num_grupos] = estadisticas_color
        
        # Crear imagen con grupos coloreados
        imagen_resultado = self._crear_imagen_con_grupos(
            imagen_base, grupos, colores_grupos
        )
        
        # Almacenar resultado
        self.resultados[num_grupos] = (umbral, imagen_resultado)
        
        print(f"Resultado agregado: {num_grupos} grupos con umbral {umbral:.4f}")
        
        # NUEVO: Mostrar estadísticas de puntos por color
        print("Estadísticas por color:")
        for color, cantidad in estadisticas_color.items():
            print(f"  {color}: {cantidad} puntos")

    def _crear_imagen_con_grupos(self, 
                                imagen_base: Imagen, 
                                grupos: List[List[PuntoImagen]], 
                                colores_hex: List[str]) -> Imagen:
        """
        Crea una nueva imagen con los grupos coloreados.
        
        Args:
            imagen_base: Imagen original
            grupos: Lista de grupos de puntos
            colores_hex: Lista de colores en formato hex para cada grupo
            
        Returns:
            Nueva instancia de Imagen con puntos coloreados por grupo
        """
        # Crear nueva instancia de imagen
        imagen_resultado = Imagen()
        imagen_resultado.imagen_original = imagen_base.imagen_original.copy()
        imagen_resultado.imagen_actual = imagen_base.imagen_original.copy()
        imagen_resultado.seleccionada = True
        imagen_resultado.alto = imagen_base.alto
        imagen_resultado.ancho = imagen_base.ancho
        imagen_resultado.nombre = f"{imagen_base.nombre}_grupos"
        
        # Convertir colores hex a BGR para OpenCV
        def hex_a_bgr(hex_color: str) -> Tuple[int, int, int]:
            """Convierte color hex a BGR para OpenCV"""
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return (rgb[2], rgb[1], rgb[0])  # BGR
        
        # Agregar puntos coloreados por grupo
        for i, grupo in enumerate(grupos):
            color_bgr = hex_a_bgr(colores_hex[i])
            
            for punto_img in grupo:
                # Crear punto con color del grupo
                punto_coloreado = Punto(
                    coordenadas=punto_img.coordenadas,
                    color=color_bgr,
                    etiqueta=f"Grupo_{i+1}"
                )
                imagen_resultado.puntos_seleccionados.append(punto_coloreado)
        
        return imagen_resultado

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÉTODOS ORIGINALES
    # ═══════════════════════════════════════════════════════════════════════════════

    def obtener_resultados(self) -> Dict[int, Tuple[float, Imagen]]:
        """Devuelve los resultados almacenados."""
        return self.resultados

    def obtener_grupos_por_umbral(self, umbral: float) -> Optional[List[List[PuntoImagen]]]:
        """Obtiene los grupos formados para un umbral específico."""
        return self._grupos_por_umbral.get(umbral)

    def obtener_colores_por_umbral(self, umbral: float) -> Optional[List[str]]:
        """Obtiene los colores asignados para un umbral específico."""
        return self._colores_por_grupo.get(umbral)

    def tiene_resultados(self) -> bool:
        """Verifica si hay resultados almacenados."""
        return len(self.resultados) > 0

    def tiene_un_resultado(self) -> bool:
        """Verifica si hay un único resultado almacenado."""
        return len(self.resultados) == 1

    def limpiar_resultados(self) -> None:
        """Limpia todos los resultados almacenados."""
        self.resultados.clear()
        self._grupos_por_umbral.clear()
        self._colores_por_grupo.clear()
        # NUEVO: Limpiar estadísticas
        self._estadisticas_por_umbral.clear()
        self._estadisticas_por_grupos.clear()

    # ═══════════════════════════════════════════════════════════════════════════════
    # NUEVOS MÉTODOS PARA ESTADÍSTICAS POR COLOR
    # ═══════════════════════════════════════════════════════════════════════════════

    def obtener_estadisticas_por_umbral(self, umbral: float) -> Optional[Dict[str, int]]:
        """
        Obtiene las estadísticas de puntos por color para un umbral específico.
        
        Args:
            umbral: Umbral de distancia usado
            
        Returns:
            Diccionario {color_hex: cantidad_puntos} o None si no existe
            
        Example:
            >>> estadisticas = resultados.obtener_estadisticas_por_umbral(0.5)
            >>> print(estadisticas)
            {'#1f77b4': 15, '#ff7f0e': 8, '#2ca02c': 12}
        """
        return self._estadisticas_por_umbral.get(umbral)

    def obtener_estadisticas_por_grupos(self, num_grupos: int) -> Optional[Dict[str, int]]:
        """
        Obtiene las estadísticas de puntos por color para un número específico de grupos.
        
        Args:
            num_grupos: Número de grupos formados
            
        Returns:
            Diccionario {color_hex: cantidad_puntos} o None si no existe
            
        Example:
            >>> estadisticas = resultados.obtener_estadisticas_por_grupos(3)
            >>> print(estadisticas)
            {'#1f77b4': 15, '#ff7f0e': 8, '#2ca02c': 12}
        """
        return self._estadisticas_por_grupos.get(num_grupos)

    def obtener_todas_las_estadisticas_por_umbral(self) -> Dict[float, Dict[str, int]]:
        """
        Obtiene todas las estadísticas organizadas por umbral.
        
        Returns:
            Diccionario {umbral: {color_hex: cantidad_puntos}}
        """
        return self._estadisticas_por_umbral.copy()

    def obtener_todas_las_estadisticas_por_grupos(self) -> Dict[int, Dict[str, int]]:
        """
        Obtiene todas las estadísticas organizadas por número de grupos.
        
        Returns:
            Diccionario {num_grupos: {color_hex: cantidad_puntos}}
        """
        return self._estadisticas_por_grupos.copy()

    def obtener_color_con_mas_puntos(self, umbral: Optional[float] = None, num_grupos: Optional[int] = None) -> Optional[Tuple[str, int]]:
        """
        Obtiene el color que tiene más puntos para un resultado específico.
        
        Args:
            umbral: Umbral específico (alternativo a num_grupos)
            num_grupos: Número de grupos específico (alternativo a umbral)
            
        Returns:
            Tupla (color_hex, cantidad_puntos) del color con más puntos
            
        Raises:
            ValueError: Si no se especifica umbral ni num_grupos, o si se especifican ambos
        """
        if (umbral is None) == (num_grupos is None):
            raise ValueError("Debe especificar exactamente uno: umbral o num_grupos")
        
        if umbral is not None:
            estadisticas = self.obtener_estadisticas_por_umbral(umbral)
        else:
            estadisticas = self.obtener_estadisticas_por_grupos(num_grupos)
        
        if not estadisticas:
            return None
        
        color_max = max(estadisticas.items(), key=lambda x: x[1])
        return color_max

    def obtener_color_con_menos_puntos(self, umbral: Optional[float] = None, num_grupos: Optional[int] = None) -> Optional[Tuple[str, int]]:
        """
        Obtiene el color que tiene menos puntos para un resultado específico.
        
        Args:
            umbral: Umbral específico (alternativo a num_grupos)
            num_grupos: Número de grupos específico (alternativo a umbral)
            
        Returns:
            Tupla (color_hex, cantidad_puntos) del color con menos puntos
        """
        if (umbral is None) == (num_grupos is None):
            raise ValueError("Debe especificar exactamente uno: umbral o num_grupos")
        
        if umbral is not None:
            estadisticas = self.obtener_estadisticas_por_umbral(umbral)
        else:
            estadisticas = self.obtener_estadisticas_por_grupos(num_grupos)
        
        if not estadisticas:
            return None
        
        color_min = min(estadisticas.items(), key=lambda x: x[1])
        return color_min

    def obtener_distribucion_equilibrada(self, tolerancia: float = 0.2) -> List[Tuple[int, float, Dict[str, int]]]:
        """
        Encuentra los resultados donde la distribución de puntos por color es más equilibrada.
        
        Args:
            tolerancia: Tolerancia para considerar equilibrado (0.0 = perfectamente equilibrado, 1.0 = cualquier distribución)
            
        Returns:
            Lista de tuplas (num_grupos, umbral, estadisticas) ordenadas por equilibrio
            
        Example:
            >>> equilibrados = resultados.obtener_distribucion_equilibrada(tolerancia=0.3)
            >>> for grupos, umbral, stats in equilibrados:
            ...     print(f"{grupos} grupos (umbral {umbral:.4f}): {stats}")
        """
        resultados_equilibrados = []
        
        for num_grupos, (umbral, _) in self.resultados.items():
            estadisticas = self._estadisticas_por_grupos[num_grupos]
            
            if len(estadisticas) <= 1:
                continue  # No se puede calcular equilibrio con 1 o 0 grupos
            
            # Calcular coeficiente de variación (desviación estándar / media)
            cantidades = list(estadisticas.values())
            media = np.mean(cantidades)
            desv_std = np.std(cantidades)
            
            if media > 0:
                coef_variacion = desv_std / media
                
                # Consideramos equilibrado si está dentro de la tolerancia
                if coef_variacion <= tolerancia:
                    resultados_equilibrados.append((num_grupos, umbral, estadisticas, coef_variacion))
        
        # Ordenar por coeficiente de variación (más equilibrado primero)
        resultados_equilibrados.sort(key=lambda x: x[3])
        
        # Retornar sin el coeficiente de variación
        return [(grupos, umbral, stats) for grupos, umbral, stats, _ in resultados_equilibrados]

    def imprimir_resumen_estadisticas(self) -> None:
        """
        Imprime un resumen completo de todas las estadísticas por color.
        """
        if not self.tiene_resultados():
            print("No hay resultados para mostrar estadísticas.")
            return
        
        print("═══════════════════════════════════════════════════════════")
        print("RESUMEN DE ESTADÍSTICAS POR COLOR")
        print("═══════════════════════════════════════════════════════════")
        
        for num_grupos in sorted(self.resultados.keys()):
            umbral, _ = self.resultados[num_grupos]
            estadisticas = self._estadisticas_por_grupos[num_grupos]
            
            print(f"\n{num_grupos} GRUPOS (Umbral: {umbral:.4f})")
            print("-" * 50)
            
            total_puntos = sum(estadisticas.values())
            
            for color_hex, cantidad in sorted(estadisticas.items(), key=lambda x: x[1], reverse=True):
                porcentaje = (cantidad / total_puntos) * 100
                print(f"  {color_hex}: {cantidad:3d} puntos ({porcentaje:5.1f}%)")
            
            print(f"  Total: {total_puntos} puntos")
            
            # Información adicional
            if len(estadisticas) > 1:
                cantidades = list(estadisticas.values())
                coef_var = np.std(cantidades) / np.mean(cantidades)
                equilibrio = "Equilibrado" if coef_var <= 0.3 else "Desequilibrado"
                print(f"  Equilibrio: {equilibrio} (CV: {coef_var:.3f})")

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de los resultados.
        
        MODIFICADO: Ahora incluye estadísticas de distribución por color.
        """
        if not self.tiene_resultados():
            return {"mensaje": "No hay resultados almacenados"}
        
        num_grupos_lista = list(self.resultados.keys())
        umbrales_lista = [resultado[0] for resultado in self.resultados.values()]
        
        # NUEVO: Estadísticas de distribución por color
        total_puntos_por_resultado = {}
        equilibrio_por_resultado = {}
        
        for num_grupos, estadisticas in self._estadisticas_por_grupos.items():
            total_puntos = sum(estadisticas.values())
            total_puntos_por_resultado[num_grupos] = total_puntos
            
            if len(estadisticas) > 1:
                cantidades = list(estadisticas.values())
                coef_var = np.std(cantidades) / np.mean(cantidades)
                equilibrio_por_resultado[num_grupos] = coef_var
        
        resultado_base = {
            "total_resultados": len(self.resultados),
            "grupos_min": min(num_grupos_lista),
            "grupos_max": max(num_grupos_lista),
            "umbral_min": min(umbrales_lista),
            "umbral_max": max(umbrales_lista),
            "configuraciones": [(grupos, f"{umbral:.4f}") for grupos, (umbral, _) in self.resultados.items()]
        }
        
        # NUEVO: Agregar estadísticas de color
        resultado_base.update({
            "total_puntos_por_resultado": total_puntos_por_resultado,
            "equilibrio_por_resultado": equilibrio_por_resultado,
            "resultado_mas_equilibrado": min(equilibrio_por_resultado.items(), key=lambda x: x[1])[0] if equilibrio_por_resultado else None
        })
        
        return resultado_base

class AlgoritmoCadena:
    """
    Clase que implementa el algoritmo de cadena para agrupar puntos según un umbral de distancia.

    El algoritmo agrupa PuntoImagen en una imagen basándose en la proximidad de sus colores RGB.
    Se prueban múltiples umbrales de distancia para encontrar agrupamientos óptimos.
    """
    
    def __init__(self, imagen: Imagen, resultados: Resultados):
        self.imagen = imagen
        self.resultados = resultados

    def ejecutar(self, 
                num_puntos: int, 
                grupos_buscados: Tuple[int, int] = (3, 5),
                metrica_distancia: str = 'euclidean') -> None:
        """
        Ejecuta el algoritmo de cadena con el número de puntos especificado.
        
        Args:
            num_puntos: Número de puntos aleatorios a generar en la imagen
            grupos_buscados: Rango de número de grupos deseados (min, max)
            metrica_distancia: Métrica de distancia a usar ('euclidean' por defecto)
        """
        if not self.imagen.seleccionada:
            print("Error: Primero debes seleccionar una imagen.")
            return
        
        if num_puntos < 2:
            print("Error: Se necesitan al menos 2 puntos para formar grupos.")
            return
        
        print(f"Ejecutando algoritmo de cadena con {num_puntos} puntos...")
        print(f"Buscando entre {grupos_buscados[0]} y {grupos_buscados[1]} grupos")
        
        # Limpiar resultados anteriores
        self.resultados.limpiar_resultados()
        
        # Generar puntos aleatorios como PuntoImagen
        puntos_imagen = self.generar_puntos_random(num_puntos)
        print(f"Generados {len(puntos_imagen)} puntos de imagen")
        
        # Obtener matriz de distancias usando color_RGB
        matriz_distancias = MatrizDistancias(puntos_imagen, metrica=metrica_distancia)
        print(f"Matriz de distancias calculada ({metrica_distancia})")
        
        # Obtener lista de distancias únicas ordenadas
        distancias_unicas = matriz_distancias.obtener_distancias_unicas_ordenadas()
        #distancias_unicas = self.muestra_ordenada(distancias_unicas, 100)  # Muestra ordenada de distancias únicas
        print(f"Probando {len(distancias_unicas)} umbrales únicos de distancia")
        
        resultados_encontrados = 0
        
        # Probar cada distancia única como umbral
        for i, umbral in enumerate(distancias_unicas):
            grupos = self._algoritmo_cadena(puntos_imagen, matriz_distancias, umbral)
            num_grupos_formados = len(grupos)
            
            # Validar si los grupos formados están en el intervalo de búsqueda
            if grupos_buscados[0] <= num_grupos_formados <= grupos_buscados[1]:
                # Almacenar el resultado
                self.resultados.agregar_resultado(
                    num_grupos_formados, 
                    umbral, 
                    grupos, 
                    self.imagen
                )
                resultados_encontrados += 1
                
                print(f"✓ Umbral {umbral:.4f}: {num_grupos_formados} grupos (guardado)")
            
            # Progreso cada 25% de umbrales probados
            if (i + 1) % max(1, len(distancias_unicas) // 4) == 0:
                progreso = ((i + 1) / len(distancias_unicas)) * 100
                print(f"Progreso: {progreso:.0f}% - Resultados encontrados: {resultados_encontrados}")
        
        print(f"\nAlgoritmo completado:")
        print(f"- Umbrales probados: {len(distancias_unicas)}")
        print(f"- Resultados válidos encontrados: {resultados_encontrados}")
        
        if resultados_encontrados > 0:
            stats = self.resultados.obtener_estadisticas()
            print(f"- Rango de grupos: {stats['grupos_min']} - {stats['grupos_max']}")
            print(f"- Rango de umbrales: {stats['umbral_min']:.4f} - {stats['umbral_max']:.4f}")
        else:
            print("- No se encontraron configuraciones en el rango especificado")
            self._sugerir_alternativas(grupos_buscados, distancias_unicas, puntos_imagen, matriz_distancias)

    @staticmethod
    def muestra_ordenada(lista, k):
        # Elegimos índices aleatorios sin reemplazo
        if k >= len(lista):
            indices = sorted(random.sample(range(len(lista)), k))
            # Usamos esos índices para seleccionar los elementos en orden
            return [lista[i] for i in indices]

    def generar_puntos_random(self, num_puntos: int) -> List[PuntoImagen]:
        """
        Genera puntos aleatorios como PuntoImagen en la imagen seleccionada.
        
        Args:
            num_puntos: Número de puntos a generar
            
        Returns:
            Lista de PuntoImagen con coordenadas aleatorias y colores RGB de la imagen
        """
        puntos_imagen = []
        
        for i in range(num_puntos):
            # Generar coordenadas aleatorias dentro de la imagen
            x = random.randint(0, self.imagen.ancho - 1)
            y = random.randint(0, self.imagen.alto - 1)
            
            # Obtener color RGB del pixel en esa posición
            color_rgb = self.imagen.obtener_color_pixel((x, y))
            
            # Crear PuntoImagen
            punto_img = PuntoImagen(
                coordenadas=[x, y],
                color_RGB=color_rgb,
                color_visualizacion=None,  # Se asignará en colorización
                etiqueta=f"Punto_{i+1}"
            )
            
            puntos_imagen.append(punto_img)
        
        print(f"Rango de coordenadas X: {min(p.x for p in puntos_imagen):.0f} - {max(p.x for p in puntos_imagen):.0f}")
        print(f"Rango de coordenadas Y: {min(p.y for p in puntos_imagen):.0f} - {max(p.y for p in puntos_imagen):.0f}")
        
        return puntos_imagen

    def _algoritmo_cadena(self, 
                         puntos: List[PuntoImagen], 
                         matriz_distancias: MatrizDistancias, 
                         umbral: float) -> List[List[PuntoImagen]]:
        """
        Implementa el algoritmo de cadena para agrupar puntos según un umbral.
        
        ALGORITMO:
        1. El primer punto crea el primer grupo
        2. Para cada punto subsecuente:
           - Calcular distancia a todos los grupos existentes (distancia al punto más cercano del grupo)
           - Si la distancia mínima ≤ umbral: agregar al grupo más cercano
           - Si no: crear nuevo grupo
        
        Args:
            puntos: Lista de PuntoImagen a agrupar
            matriz_distancias: Matriz de distancias precalculada
            umbral: Umbral de distancia para agrupar
            
        Returns:
            Lista de grupos, cada grupo es una lista de PuntoImagen
        """
        if not puntos:
            return []
        
        grupos: List[List[PuntoImagen]] = []
        
        # El primer punto siempre crea el primer grupo
        grupos.append([puntos[0]])
        
        # Procesar puntos restantes
        for punto_actual in puntos[1:]:
            distancia_minima = float('inf')
            grupo_mas_cercano = -1
            
            # Evaluar distancia a todos los grupos existentes
            for i, grupo in enumerate(grupos):
                # Calcular distancia mínima al grupo (distancia al punto más cercano del grupo)
                distancia_al_grupo = min(
                    matriz_distancias.obtener_distancia(punto_actual, punto_grupo)
                    for punto_grupo in grupo
                )
                
                # Actualizar grupo más cercano
                if distancia_al_grupo < distancia_minima:
                    distancia_minima = distancia_al_grupo
                    grupo_mas_cercano = i
            
            # Decidir si agregar al grupo más cercano o crear nuevo grupo
            if distancia_minima <= umbral:
                # Agregar al grupo más cercano
                grupos[grupo_mas_cercano].append(punto_actual)
            else:
                # Crear nuevo grupo
                grupos.append([punto_actual])
        
        return grupos

    def _sugerir_alternativas(self, 
                             grupos_buscados: Tuple[int, int], 
                             distancias_unicas: List[float], 
                             puntos: List[PuntoImagen], 
                             matriz_distancias: MatrizDistancias) -> None:
        """
        Sugiere alternativas cuando no se encuentran resultados en el rango deseado.
        """
        print("\n=== SUGERENCIAS PARA MEJORAR RESULTADOS ===")
        
        # Probar algunos umbrales y ver qué grupos forman
        umbrales_muestra = [
            distancias_unicas[0],  # Mínimo
            distancias_unicas[len(distancias_unicas)//4],  # 25%
            distancias_unicas[len(distancias_unicas)//2],  # 50%
            distancias_unicas[3*len(distancias_unicas)//4],  # 75%
            distancias_unicas[-1]  # Máximo
        ]
        
        print("Análisis de umbrales de muestra:")
        for umbral in umbrales_muestra:
            grupos = self._algoritmo_cadena(puntos, matriz_distancias, umbral)
            print(f"  Umbral {umbral:.4f}: {len(grupos)} grupos")
        
        print(f"\nRecomendaciones:")
        print(f"1. Ajustar rango de grupos buscados")
        print(f"2. Cambiar número de puntos aleatorios")
        print(f"3. Usar métrica de distancia diferente")
        print(f"4. Seleccionar región de imagen más homogénea")

    def obtener_informacion_puntos(self, puntos: List[PuntoImagen]) -> Dict:
        """Obtiene información estadística de los puntos generados."""
        if not puntos:
            return {}
        
        # Estadísticas de coordenadas
        coords_x = [p.x for p in puntos]
        coords_y = [p.y for p in puntos]
        
        # Estadísticas de colores RGB
        colores_r = [p.color_RGB[0] for p in puntos]
        colores_g = [p.color_RGB[1] for p in puntos]
        colores_b = [p.color_RGB[2] for p in puntos]
        
        return {
            "num_puntos": len(puntos),
            "coordenadas": {
                "x": {"min": min(coords_x), "max": max(coords_x), "promedio": np.mean(coords_x)},
                "y": {"min": min(coords_y), "max": max(coords_y), "promedio": np.mean(coords_y)}
            },
            "colores_rgb": {
                "r": {"min": min(colores_r), "max": max(colores_r), "promedio": np.mean(colores_r)},
                "g": {"min": min(colores_g), "max": max(colores_g), "promedio": np.mean(colores_g)},
                "b": {"min": min(colores_b), "max": max(colores_b), "promedio": np.mean(colores_b)}
            }
        }





# ═══════════════════════════════════════════════════════════════════════════════════
# EJEMPLO DE USO Y TESTING
# ═══════════════════════════════════════════════════════════════════════════════════

def ejemplo_uso_algoritmo():
    """Ejemplo de uso del algoritmo de cadena."""
    print("=== Ejemplo de Algoritmo de Cadena ===")
    
    # Crear imagen y resultados
    imagen = Imagen()
    resultados = Resultados()
    
    # Crear algoritmo
    algoritmo = AlgoritmoCadena(imagen, resultados)
    
    if imagen.seleccionar_imagen():
        print("Imagen cargada. Ejecutando algoritmo...")
        
        # Ejecutar con parámetros de ejemplo
        algoritmo.ejecutar(
            num_puntos=50,
            grupos_buscados=(3, 6),
            metrica_distancia='euclidean'
        )
        
        # Mostrar estadísticas
        if resultados.tiene_resultados():
            stats = resultados.obtener_estadisticas()
            print(f"\nResultados obtenidos: {stats}")
            
            # Mostrar primer resultado
            primer_resultado = list(resultados.obtener_resultados().values())[0]
            umbral, imagen_resultado = primer_resultado
            print(f"Mostrando primer resultado (umbral: {umbral:.4f})")
            imagen_resultado.dibujar_imagen(
                mostrar_original=False,
                titulo_ventana="Grupos por Algoritmo de Cadena"
            )
        else:
            print("No se encontraron resultados en el rango especificado.")


if __name__ == "__main__":
    ejemplo_uso_algoritmo()