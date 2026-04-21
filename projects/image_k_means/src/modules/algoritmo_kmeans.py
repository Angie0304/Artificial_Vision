"""
Implementación del algoritmo K-means para agrupamiento de puntos por color.

Este módulo implementa K-means usando la infraestructura existente:
- PuntoImagen para representar píxeles con coordenadas y color RGB
- MatrizDistancias para cálculo eficiente de distancias entre colores
- Imagen para manipulación y visualización

Principios del Zen de Python aplicados:
- Simple es mejor que complejo
- Plano es mejor que anidado
- La legibilidad cuenta
- Los casos especiales no son tan especiales como para romper las reglas
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from modules.punto import PuntoImagen
from modules.imagen import Imagen
from modules.matriz_distancia import MatrizDistancias
from modules.color import generar_color_para_scatter
from utils.funciones_estandar_V2 import cronometro
import random


class ResultadosKMeans:
    """
    Almacena los resultados y el historial del algoritmo K-means.
    
    Attributes:
        k: Número de clusters
        centroides_finales: Lista de PuntoImagen representando centroides finales
        grupos_finales: Asignación final de puntos a grupos
        historial_centroides: Lista con centroides de cada iteración
        historial_grupos: Lista con asignaciones de cada iteración
        num_iteraciones: Número total de iteraciones ejecutadas
        colores_clusters: Colores asignados a cada cluster para visualización
    """
    
    def __init__(self, k: int):
        self.k = k
        self.centroides_finales: List[PuntoImagen] = []
        self.grupos_finales: np.ndarray = None
        self.historial_centroides: List[List[PuntoImagen]] = []
        self.historial_grupos: List[np.ndarray] = []
        self.num_iteraciones = 0
        self.colores_clusters: List[str] = []
        self._generar_colores_clusters()
    
    def _generar_colores_clusters(self):
        """Genera colores únicos para cada cluster."""
        self.colores_clusters = []
        for i in range(self.k):
            color = generar_color_para_scatter(
                colores_existentes=self.colores_clusters,
                modo='primario_nuevo' if i < 10 else 'disimilar'
            )
            self.colores_clusters.append(color)
    
    def agregar_iteracion(self, centroides: List[PuntoImagen], grupos: np.ndarray):
        """Agrega una iteración al historial."""
        self.historial_centroides.append(centroides.copy())
        self.historial_grupos.append(grupos.copy())
        self.num_iteraciones = len(self.historial_centroides) - 1  # -1 por estado inicial
    
    def finalizar(self, centroides: List[PuntoImagen], grupos: np.ndarray):
        """Marca el resultado final del algoritmo."""
        self.centroides_finales = centroides
        self.grupos_finales = grupos
    
    def obtener_estadisticas(self) -> Dict:
        """Calcula estadísticas de los clusters finales."""
        if self.grupos_finales is None:
            return {}
        
        total_puntos = len(self.grupos_finales)
        estadisticas = {
            'k': self.k,
            'iteraciones': self.num_iteraciones,
            'total_puntos': total_puntos,
            'clusters': {}
        }
        
        for i in range(self.k):
            puntos_cluster = np.sum(self.grupos_finales == i)
            porcentaje = (puntos_cluster / total_puntos) * 100 if total_puntos > 0 else 0
            
            # Color RGB del centroide
            centroide = self.centroides_finales[i]
            color_rgb = centroide.color_RGB.astype(int).tolist()
            
            estadisticas['clusters'][i] = {
                'puntos': int(puntos_cluster),
                'porcentaje': round(porcentaje, 1),
                'color_rgb': color_rgb,
                'color_hex': self.colores_clusters[i]
            }
        
        return estadisticas


class AlgoritmoKMeans:
    """
    Implementación del algoritmo K-means para agrupamiento por color.
    
    El algoritmo agrupa puntos basándose en la similitud de sus colores RGB,
    no en su posición espacial. Utiliza MatrizDistancias para cálculos eficientes.
    """
    
    def __init__(self, imagen: Imagen):
        """
        Inicializa el algoritmo K-means.
        
        Args:
            imagen: Instancia de Imagen sobre la cual ejecutar el algoritmo
        """
        self.imagen = imagen
        self.puntos: List[PuntoImagen] = []
        self.matriz_distancias: Optional[MatrizDistancias] = None
        self.resultados: Optional[ResultadosKMeans] = None
    
    def generar_puntos_aleatorios(self, n: int) -> List[PuntoImagen]:
        """
        Genera n puntos aleatorios como PuntoImagen en la imagen.
        
        Args:
            n: Número de puntos a generar
            
        Returns:
            Lista de PuntoImagen con coordenadas aleatorias y colores de la imagen
        """
        if not self.imagen.seleccionada:
            raise ValueError("No hay imagen seleccionada")
        
        puntos = []
        for i in range(n):
            # Coordenadas aleatorias dentro de la imagen
            x = random.randint(0, self.imagen.ancho - 1)
            y = random.randint(0, self.imagen.alto - 1)
            
            # Color RGB del píxel
            color_rgb = self.imagen.obtener_color_pixel((x, y))
            
            punto = PuntoImagen(
                coordenadas=[x, y],
                color_RGB=color_rgb,
                etiqueta=f"P{i+1}"
            )
            puntos.append(punto)
        
        self.puntos = puntos
        return puntos
    
    def _inicializar_centroides(self, k: int) -> List[PuntoImagen]:
        """
        Inicializa k centroides usando el método K-means++.
        
        K-means++ mejora la convergencia eligiendo centroides iniciales
        que estén bien distribuidos en el espacio de color.
        """
        if k > len(self.puntos):
            raise ValueError(f"k ({k}) no puede ser mayor que el número de puntos ({len(self.puntos)})")
        
        centroides = []
        
        # Primer centroide aleatorio
        primer_indice = random.randint(0, len(self.puntos) - 1)
        centroides.append(self.puntos[primer_indice])
        
        # Resto de centroides usando K-means++
        for _ in range(1, k):
            # Calcular distancia mínima de cada punto a los centroides existentes
            distancias_minimas = []
            
            for punto in self.puntos:
                min_dist = float('inf')
                for centroide in centroides:
                    dist = self.matriz_distancias.obtener_distancia(punto, centroide)
                    min_dist = min(min_dist, dist)
                distancias_minimas.append(min_dist)
            
            # Convertir distancias a probabilidades
            distancias_array = np.array(distancias_minimas)
            if np.sum(distancias_array) > 0:
                probabilidades = distancias_array / np.sum(distancias_array)
            else:
                probabilidades = np.ones(len(self.puntos)) / len(self.puntos)
            
            # Elegir siguiente centroide con probabilidad proporcional a la distancia
            siguiente_indice = np.random.choice(len(self.puntos), p=probabilidades)
            centroides.append(self.puntos[siguiente_indice])
        
        return centroides
    
    def _asignar_puntos_a_clusters(self, centroides: List[PuntoImagen]) -> np.ndarray:
        """
        Asigna cada punto al centroide más cercano basándose en color RGB.
        
        Returns:
            Array con la asignación de cada punto a un cluster (0 a k-1)
        """
        n_puntos = len(self.puntos)
        grupos = np.zeros(n_puntos, dtype=int)
        
        for i, punto in enumerate(self.puntos):
            min_distancia = float('inf')
            mejor_cluster = 0
            
            for j, centroide in enumerate(centroides):
                distancia = self.matriz_distancias.obtener_distancia(punto, centroide)
                
                if distancia < min_distancia:
                    min_distancia = distancia
                    mejor_cluster = j
            
            grupos[i] = mejor_cluster
        
        return grupos
    
    def _calcular_nuevos_centroides(self, grupos: np.ndarray, k: int) -> List[PuntoImagen]:
        """
        Calcula nuevos centroides como el punto más cercano al color promedio del cluster.
        
        Args:
            grupos: Asignación actual de puntos a clusters
            k: Número de clusters
            
        Returns:
            Lista de nuevos centroides
        """
        nuevos_centroides = []
        
        for cluster_id in range(k):
            # Obtener puntos del cluster
            indices_cluster = np.where(grupos == cluster_id)[0]
            
            if len(indices_cluster) == 0:
                # Cluster vacío: mantener centroide anterior o elegir punto aleatorio
                punto_aleatorio = random.choice(self.puntos)
                nuevos_centroides.append(punto_aleatorio)
                continue
            
            # Calcular color promedio del cluster
            puntos_cluster = [self.puntos[i] for i in indices_cluster]
            colores_rgb = np.array([p.color_RGB for p in puntos_cluster])
            color_promedio = np.mean(colores_rgb, axis=0)
            
            # Encontrar el punto más cercano al color promedio
            min_distancia = float('inf')
            mejor_punto = puntos_cluster[0]
            
            for punto in puntos_cluster:
                distancia = np.linalg.norm(punto.color_RGB - color_promedio)
                if distancia < min_distancia:
                    min_distancia = distancia
                    mejor_punto = punto
            
            nuevos_centroides.append(mejor_punto)
        
        return nuevos_centroides
    
    @cronometro
    def ejecutar(self, k: int, max_iteraciones: int = 50, 
                 tolerancia: float = 1e-4) -> ResultadosKMeans:
        """
        Ejecuta el algoritmo K-means.
        
        Args:
            k: Número de clusters
            max_iteraciones: Número máximo de iteraciones
            tolerancia: Cambio mínimo en centroides para continuar
            
        Returns:
            ResultadosKMeans con el historial completo y resultados finales
        """
        if not self.puntos:
            raise ValueError("No hay puntos generados. Use generar_puntos_aleatorios() primero.")
        
        print(f"\nEjecutando K-means con k={k}")
        print(f"Número de puntos: {len(self.puntos)}")
        
        # Crear matriz de distancias
        print("Calculando matriz de distancias...")
        self.matriz_distancias = MatrizDistancias(self.puntos, metrica='euclidean')
        
        # Inicializar resultados
        self.resultados = ResultadosKMeans(k)
        
        # Inicializar centroides
        print("Inicializando centroides con K-means++...")
        centroides = self._inicializar_centroides(k)
        
        # Estado inicial
        grupos = self._asignar_puntos_a_clusters(centroides)
        self.resultados.agregar_iteracion(centroides, grupos)
        
        # Iteraciones del algoritmo
        convergio = False
        iteracion = 0
        
        while iteracion < max_iteraciones and not convergio:
            iteracion += 1
            print(f"Iteración {iteracion}...")
            
            # Guardar centroides anteriores para verificar convergencia
            centroides_anteriores = centroides.copy()
            
            # Paso 1: Asignar puntos a clusters
            grupos = self._asignar_puntos_a_clusters(centroides)
            
            # Paso 2: Recalcular centroides
            centroides = self._calcular_nuevos_centroides(grupos, k)
            
            # Guardar iteración
            self.resultados.agregar_iteracion(centroides, grupos)
            
            # Verificar convergencia
            cambio_total = 0
            for i in range(k):
                if i < len(centroides_anteriores):
                    cambio = self.matriz_distancias.obtener_distancia(
                        centroides[i], centroides_anteriores[i]
                    )
                    cambio_total += cambio
            
            if cambio_total < tolerancia:
                convergio = True
                print(f"Convergencia alcanzada en iteración {iteracion}")
        
        # Finalizar
        self.resultados.finalizar(centroides, grupos)
        
        # Mostrar estadísticas
        stats = self.resultados.obtener_estadisticas()
        print(f"\nK-means completado:")
        print(f"- Iteraciones: {stats['iteraciones']}")
        print(f"- Clusters formados: {stats['k']}")
        
        for i, info in stats['clusters'].items():
            print(f"  Cluster {i+1}: {info['puntos']} puntos ({info['porcentaje']}%) - "
                  f"RGB: {info['color_rgb']}")
        
        return self.resultados