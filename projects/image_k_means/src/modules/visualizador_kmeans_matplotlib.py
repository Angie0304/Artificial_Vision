"""
Módulo de visualización mejorado para K-means usando matplotlib.

Este módulo reemplaza el visualizador anterior problemático con uno más robusto
que usa matplotlib para todas las visualizaciones, asegurando consistencia
y mejor control sobre el renderizado.

Características:
- Visualización clara de cada iteración con estadísticas
- Resumen en grid de todas las iteraciones
- Generación de GIF animado mejorado
- Estadísticas detalladas con gráficos de barras
- Impresión de información de clusters en cada iteración
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.gridspec import GridSpec
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from pathlib import Path
import cv2 as cv

from modules.imagen import Imagen
from modules.punto import PuntoImagen
from modules.algoritmo_kmeans import ResultadosKMeans


class VisualizadorKMeansMatplotlib:
    """
    Visualizador mejorado para K-means usando matplotlib.
    
    Reemplaza el visualizador anterior con problemas de OpenCV por uno
    más robusto basado completamente en matplotlib.
    """
    
    def __init__(self, imagen: Imagen, resultados: ResultadosKMeans):
        """
        Inicializa el visualizador.
        
        Args:
            imagen: Imagen base sobre la cual se ejecutó K-means
            resultados: Resultados del algoritmo K-means
        """
        self.imagen = imagen
        self.resultados = resultados
        # Convertir imagen BGR a RGB para matplotlib
        self.imagen_rgb = cv.cvtColor(imagen.imagen_original, cv.COLOR_BGR2RGB)
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def _hex_a_rgb_normalizado(self, hex_color: str) -> Tuple[float, float, float]:
        """Convierte color hex a RGB normalizado (0-1) para matplotlib."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return tuple(c/255.0 for c in rgb)
    
    def _imprimir_estadisticas_iteracion(self, iteracion: int, 
                                       centroides: List[PuntoImagen], 
                                       grupos: np.ndarray,
                                       puntos: List[PuntoImagen]):
        """
        Imprime estadísticas detalladas de una iteración específica.
        """
        print(f"\n{'='*60}")
        if iteracion == 0:
            print(f"ESTADO INICIAL - Asignación aleatoria")
        else:
            print(f"ITERACIÓN {iteracion}")
        print(f"{'='*60}")
        
        total_puntos = len(grupos)
        
        for cluster_id in range(self.resultados.k):
            # Obtener puntos del cluster
            indices_cluster = np.where(grupos == cluster_id)[0]
            num_puntos = len(indices_cluster)
            porcentaje = (num_puntos / total_puntos * 100) if total_puntos > 0 else 0
            
            # Color del cluster
            color_hex = self.resultados.colores_clusters[cluster_id]
            
            # Centroide
            centroide = centroides[cluster_id]
            
            print(f"\nCluster {cluster_id + 1} ({color_hex}):")
            print(f"  - Puntos: {num_puntos} ({porcentaje:.1f}%)")
            print(f"  - Centroide: ({centroide.x:.1f}, {centroide.y:.1f})")
            print(f"  - Color RGB centroide: {centroide.color_RGB.astype(int)}")
            
            # Mostrar algunos puntos del cluster (primeros 5)
            if num_puntos > 0:
                print(f"  - Primeros puntos (máx 5):")
                for i, idx in enumerate(indices_cluster[:5]):
                    punto = puntos[idx]
                    print(f"    · {punto.etiqueta}: ({punto.x:.0f}, {punto.y:.0f}) "
                          f"RGB: {punto.color_RGB.astype(int)}")
                if num_puntos > 5:
                    print(f"    · ... y {num_puntos - 5} puntos más")
    
    def visualizar_iteracion(self, iteracion: int, puntos: List[PuntoImagen], 
                           mostrar: bool = True, guardar: bool = False) -> plt.Figure:
        """
        Visualiza una iteración específica del algoritmo con matplotlib.
        
        Args:
            iteracion: Número de iteración (0 = estado inicial)
            puntos: Lista de puntos utilizados
            mostrar: Si mostrar la figura inmediatamente
            guardar: Si guardar la figura como imagen
            
        Returns:
            Figure de matplotlib con la visualización
        """
        if iteracion >= len(self.resultados.historial_centroides):
            raise ValueError(f"Iteración {iteracion} no existe en el historial")
        
        # Obtener datos de la iteración
        centroides = self.resultados.historial_centroides[iteracion]
        grupos = self.resultados.historial_grupos[iteracion]
        
        # Imprimir estadísticas en consola
        self._imprimir_estadisticas_iteracion(iteracion, centroides, grupos, puntos)
        
        # Crear figura con subplots
        fig = plt.figure(figsize=(14, 8))
        gs = GridSpec(2, 2, figure=fig, width_ratios=[3, 1], height_ratios=[4, 1])
        
        # Subplot principal: imagen con clusters
        ax_main = fig.add_subplot(gs[0, 0])
        ax_main.imshow(self.imagen_rgb)
        
        # Dibujar puntos por cluster
        for cluster_id in range(self.resultados.k):
            color_hex = self.resultados.colores_clusters[cluster_id]
            color_rgb = self._hex_a_rgb_normalizado(color_hex)
            
            # Obtener puntos del cluster
            indices_cluster = np.where(grupos == cluster_id)[0]
            
            if len(indices_cluster) > 0:
                xs = [puntos[idx].x for idx in indices_cluster]
                ys = [puntos[idx].y for idx in indices_cluster]
                
                ax_main.scatter(xs, ys, c=[color_rgb], s=30, alpha=0.7, 
                              edgecolors='white', linewidth=0.5,
                              label=f'Cluster {cluster_id+1}')
        
        # Dibujar centroides
        for i, centroide in enumerate(centroides):
            color_rgb = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i])
            
            # Cruz grande para el centroide
            ax_main.scatter(centroide.x, centroide.y, c='black', 
                          marker='x', s=300, linewidths=4, zorder=10)
            ax_main.scatter(centroide.x, centroide.y, c=[color_rgb], 
                          marker='x', s=250, linewidths=3, zorder=11)
            
            # Número del cluster
            ax_main.annotate(str(i+1), (centroide.x, centroide.y),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='white', alpha=0.8))
        
        # Configurar título y ejes
        titulo = f"K-means (k={self.resultados.k}) - "
        titulo += "Estado inicial" if iteracion == 0 else f"Iteración {iteracion}"
        ax_main.set_title(titulo, fontsize=16, fontweight='bold')
        ax_main.set_xlabel('X')
        ax_main.set_ylabel('Y')
        #ax_main.invert_yaxis()  # Para que Y=0 esté arriba como en imágenes
        
        # Subplot derecho: distribución de puntos por cluster
        ax_dist = fig.add_subplot(gs[0, 1])
        
        # Calcular distribución
        distribuciones = []
        etiquetas = []
        colores = []
        
        for cluster_id in range(self.resultados.k):
            num_puntos = np.sum(grupos == cluster_id)
            distribuciones.append(num_puntos)
            etiquetas.append(f'C{cluster_id+1}')
            colores.append(self._hex_a_rgb_normalizado(self.resultados.colores_clusters[cluster_id]))
        
        # Gráfico de barras
        bars = ax_dist.bar(etiquetas, distribuciones, color=colores, 
                          edgecolor='black', linewidth=1)
        
        # Agregar valores encima de las barras
        for bar, valor in zip(bars, distribuciones):
            altura = bar.get_height()
            ax_dist.text(bar.get_x() + bar.get_width()/2., altura + 0.5,
                       f'{valor}', ha='center', va='bottom', fontweight='bold')
        
        ax_dist.set_title('Distribución de puntos', fontsize=12)
        ax_dist.set_ylabel('Número de puntos')
        ax_dist.set_xlabel('Cluster')
        
        # Subplot inferior: información de centroides
        ax_info = fig.add_subplot(gs[1, :])
        ax_info.axis('off')
        
        # Crear tabla con información de centroides
        info_text = "Información de centroides:\n"
        for i, centroide in enumerate(centroides):
            color_hex = self.resultados.colores_clusters[i]
            info_text += f"Cluster {i+1} ({color_hex}): "
            info_text += f"Posición=({centroide.x:.1f}, {centroide.y:.1f}), "
            info_text += f"Color RGB={centroide.color_RGB.astype(int).tolist()}\n"
        
        ax_info.text(0.05, 0.5, info_text, transform=ax_info.transAxes,
                    fontsize=10, fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.5))
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar si se solicita
        if guardar:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kmeans_iter{iteracion}_{timestamp}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Figura guardada como: {filename}")
        
        # Mostrar si se solicita
        if mostrar:
            plt.show()
        
        return fig
    
    def crear_resumen_iteraciones(self, puntos: List[PuntoImagen], 
                                 mostrar: bool = True) -> plt.Figure:
        """
        Crea un resumen visual de todas las iteraciones en un grid.
        """
        num_iteraciones = len(self.resultados.historial_centroides)
        
        # Calcular dimensiones del grid
        cols = min(4, num_iteraciones)  # Máximo 4 columnas
        rows = int(np.ceil(num_iteraciones / cols))
        
        # Crear figura grande
        fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
        
        # Convertir a array 2D si es necesario
        if num_iteraciones == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = axes.reshape(1, -1)
        elif cols == 1:
            axes = axes.reshape(-1, 1)
        
        # Dibujar cada iteración
        for iter_idx in range(num_iteraciones):
            row = iter_idx // cols
            col = iter_idx % cols
            ax = axes[row, col]
            
            # Obtener datos
            centroides = self.resultados.historial_centroides[iter_idx]
            grupos = self.resultados.historial_grupos[iter_idx]
            
            # Mostrar imagen de fondo
            ax.imshow(self.imagen_rgb, alpha=0.3)
            
            # Dibujar puntos por cluster
            for cluster_id in range(self.resultados.k):
                indices_cluster = np.where(grupos == cluster_id)[0]
                if len(indices_cluster) > 0:
                    xs = [puntos[idx].x for idx in indices_cluster]
                    ys = [puntos[idx].y for idx in indices_cluster]
                    color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[cluster_id])
                    ax.scatter(xs, ys, c=[color], s=20, alpha=0.7)
            
            # Dibujar centroides
            for i, centroide in enumerate(centroides):
                color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i])
                ax.scatter(centroide.x, centroide.y, c='black', 
                         marker='x', s=150, linewidths=3)
                ax.scatter(centroide.x, centroide.y, c=[color], 
                         marker='x', s=120, linewidths=2)
            
            # Configurar título y ejes
            titulo = "Inicial" if iter_idx == 0 else f"Iter {iter_idx}"
            ax.set_title(titulo, fontsize=12, fontweight='bold')
            ax.set_xticks([])
            ax.set_yticks([])
            ax.invert_yaxis()
        
        # Ocultar subplots vacíos
        for iter_idx in range(num_iteraciones, rows * cols):
            row = iter_idx // cols
            col = iter_idx % cols
            axes[row, col].axis('off')
        
        # Título general
        fig.suptitle(f'Evolución K-means (k={self.resultados.k})', 
                    fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if mostrar:
            plt.show()
        
        return fig
    
    def crear_visualizacion_estadisticas(self, puntos: List[PuntoImagen], 
                                       mostrar: bool = True) -> plt.Figure:
        """
        Crea una visualización completa con estadísticas finales.
        """
        # Datos finales
        centroides_finales = self.resultados.centroides_finales
        grupos_finales = self.resultados.grupos_finales
        stats = self.resultados.obtener_estadisticas()
        
        # Crear figura con layout personalizado
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, 
                     width_ratios=[2, 1, 1],
                     height_ratios=[2, 1, 1])
        
        # 1. Imagen principal con resultado final
        ax_main = fig.add_subplot(gs[:2, 0])
        ax_main.imshow(self.imagen_rgb)
        
        # Dibujar clusters finales
        for cluster_id in range(self.resultados.k):
            indices_cluster = np.where(grupos_finales == cluster_id)[0]
            if len(indices_cluster) > 0:
                xs = [puntos[idx].x for idx in indices_cluster]
                ys = [puntos[idx].y for idx in indices_cluster]
                color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[cluster_id])
                ax_main.scatter(xs, ys, c=[color], s=40, alpha=0.8,
                              edgecolors='white', linewidth=0.5)
        
        # Dibujar centroides finales
        for i, centroide in enumerate(centroides_finales):
            color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i])
            ax_main.scatter(centroide.x, centroide.y, c='black', 
                          marker='X', s=400, linewidths=4)
            ax_main.scatter(centroide.x, centroide.y, c=[color], 
                          marker='X', s=350, linewidths=3)
            ax_main.annotate(f'C{i+1}', (centroide.x, centroide.y),
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=14, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.5", 
                                   facecolor='yellow', alpha=0.7))
        
        ax_main.set_title('Resultado Final K-means', fontsize=16, fontweight='bold')
        ax_main.set_xlabel('X')
        ax_main.set_ylabel('Y')
        #ax_main.invert_yaxis()
        
        # 2. Gráfico de torta con distribución
        ax_pie = fig.add_subplot(gs[0, 1])
        sizes = [stats['clusters'][i]['puntos'] for i in range(self.resultados.k)]
        colors = [self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i]) 
                 for i in range(self.resultados.k)]
        labels = [f"C{i+1}\n({stats['clusters'][i]['porcentaje']}%)" 
                 for i in range(self.resultados.k)]
        
        ax_pie.pie(sizes, labels=labels, colors=colors, autopct='%d',
                  startangle=90, wedgeprops={'edgecolor': 'black'})
        ax_pie.set_title('Distribución de Puntos', fontsize=12)
        
        # 3. Gráfico de barras con colores RGB promedio
        ax_rgb = fig.add_subplot(gs[0, 2])
        
        # Calcular color RGB promedio por cluster
        rgb_promedios = []
        for cluster_id in range(self.resultados.k):
            indices_cluster = np.where(grupos_finales == cluster_id)[0]
            if len(indices_cluster) > 0:
                colores_cluster = [puntos[idx].color_RGB for idx in indices_cluster]
                rgb_promedio = np.mean(colores_cluster, axis=0).astype(int)
            else:
                rgb_promedio = np.array([0, 0, 0])
            rgb_promedios.append(rgb_promedio)
        
        # Crear gráfico de barras apiladas para RGB
        cluster_names = [f'C{i+1}' for i in range(self.resultados.k)]
        r_values = [rgb[0] for rgb in rgb_promedios]
        g_values = [rgb[1] for rgb in rgb_promedios]
        b_values = [rgb[2] for rgb in rgb_promedios]
        
        x = np.arange(len(cluster_names))
        width = 0.6
        
        ax_rgb.bar(x, r_values, width, label='R', color='red', alpha=0.7)
        ax_rgb.bar(x, g_values, width, bottom=r_values, label='G', color='green', alpha=0.7)
        ax_rgb.bar(x, b_values, width, bottom=np.array(r_values)+np.array(g_values), 
                  label='B', color='blue', alpha=0.7)
        
        ax_rgb.set_ylabel('Valor RGB')
        ax_rgb.set_title('Color RGB Promedio por Cluster')
        ax_rgb.set_xticks(x)
        ax_rgb.set_xticklabels(cluster_names)
        ax_rgb.legend()
        ax_rgb.set_ylim(0, 770)  # Máximo posible: 255*3
        
        # 4. Tabla con información detallada
        ax_table = fig.add_subplot(gs[1:, 1:])
        ax_table.axis('off')
        
        # Preparar datos para la tabla
        table_data = []
        table_data.append(['Cluster', 'Puntos', '%', 'Centroide (X,Y)', 'Color RGB'])
        
        for i in range(self.resultados.k):
            cluster_stats = stats['clusters'][i]
            centroide = centroides_finales[i]
            row = [
                f'C{i+1}',
                str(cluster_stats['puntos']),
                f"{cluster_stats['porcentaje']}%",
                f"({centroide.x:.0f}, {centroide.y:.0f})",
                str(cluster_stats['color_rgb'])
            ]
            table_data.append(row)
        
        # Crear tabla
        table = ax_table.table(cellText=table_data, loc='center',
                             cellLoc='center', colWidths=[0.15, 0.15, 0.15, 0.25, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Colorear las celdas de la primera columna
        for i in range(1, len(table_data)):
            cell = table[(i, 0)]
            color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i-1])
            cell.set_facecolor(color)
            cell.set_text_props(weight='bold')
        
        # 5. Información general
        ax_info = fig.add_subplot(gs[2, 0])
        ax_info.axis('off')
        
        info_text = f"""
        RESUMEN K-MEANS
        ===============
        Total de puntos: {stats['total_puntos']}
        Número de clusters (k): {stats['k']}
        Iteraciones hasta convergencia: {stats['iteraciones']}
        
        Cluster más grande: C{max(stats['clusters'].items(), key=lambda x: x[1]['puntos'])[0]+1} ({max(stats['clusters'].items(), key=lambda x: x[1]['puntos'])[1]['puntos']} puntos)
        Cluster más pequeño: C{min(stats['clusters'].items(), key=lambda x: x[1]['puntos'])[0]+1} ({min(stats['clusters'].items(), key=lambda x: x[1]['puntos'])[1]['puntos']} puntos)
        """
        
        ax_info.text(0.05, 0.5, info_text, transform=ax_info.transAxes,
                    fontsize=12, fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", 
                            facecolor='lightblue', alpha=0.5))
        
        # Título general
        fig.suptitle(f'Análisis Completo K-means (k={self.resultados.k})', 
                    fontsize=18, fontweight='bold')
        
        plt.tight_layout()
        
        if mostrar:
            plt.show()
        
        return fig
    
    def generar_gif_mejorado(self, puntos: List[PuntoImagen], 
                           nombre_archivo: Optional[str] = None,
                           fps: int = 2,
                           duracion_inicial: float = 1.5,
                           duracion_final: float = 2.5,
                           mostrar_estadisticas: bool = True) -> str:
        """
        Genera un GIF animado mejorado con estadísticas en cada frame.
        """
        print("\n🎬 Generando GIF animado del proceso K-means...")
        
        # Generar nombre de archivo
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"kmeans_k{self.resultados.k}_{timestamp}.gif"
        
        # Preparar frames
        frames = []
        num_iteraciones = len(self.resultados.historial_centroides)
        
        # Frames para cada estado
        frames_iniciales = int(duracion_inicial * fps)
        frames.extend([0] * frames_iniciales)
        
        for i in range(1, num_iteraciones):
            frames.append(i)
        
        if num_iteraciones > 1:
            frames_finales = int(duracion_final * fps)
            frames.extend([num_iteraciones - 1] * frames_finales)
        
        # Crear figura para animación
        if mostrar_estadisticas:
            fig = plt.figure(figsize=(12, 8))
            gs = GridSpec(2, 2, figure=fig, width_ratios=[3, 1], height_ratios=[3, 1])
            ax_main = fig.add_subplot(gs[0, 0])
            ax_stats = fig.add_subplot(gs[0, 1])
            ax_info = fig.add_subplot(gs[1, :])
        else:
            fig, ax_main = plt.subplots(figsize=(10, 8))
        
        def update(frame_idx):
            # Limpiar axes
            ax_main.clear()
            if mostrar_estadisticas:
                ax_stats.clear()
                ax_info.clear()
            
            iteracion = frames[frame_idx]
            centroides = self.resultados.historial_centroides[iteracion]
            grupos = self.resultados.historial_grupos[iteracion]
            
            # Imagen principal
            ax_main.imshow(self.imagen_rgb)
            
            # Dibujar puntos
            for cluster_id in range(self.resultados.k):
                indices_cluster = np.where(grupos == cluster_id)[0]
                if len(indices_cluster) > 0:
                    xs = [puntos[idx].x for idx in indices_cluster]
                    ys = [puntos[idx].y for idx in indices_cluster]
                    color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[cluster_id])
                    ax_main.scatter(xs, ys, c=[color], s=30, alpha=0.7,
                                  label=f'Cluster {cluster_id+1}')
            
            # Dibujar centroides
            for i, centroide in enumerate(centroides):
                color = self._hex_a_rgb_normalizado(self.resultados.colores_clusters[i])
                ax_main.scatter(centroide.x, centroide.y, c='black', 
                              marker='x', s=200, linewidths=3)
                ax_main.scatter(centroide.x, centroide.y, c=[color], 
                              marker='x', s=150, linewidths=2)
            
            # Configurar título
            titulo = f'K-means (k={self.resultados.k}) - '
            titulo += 'Estado inicial' if iteracion == 0 else f'Iteración {iteracion}'
            ax_main.set_title(titulo, fontsize=14, fontweight='bold')
            ax_main.set_xlabel('X')
            ax_main.set_ylabel('Y')
            #ax_main.invert_yaxis()
            
            if mostrar_estadisticas:
                # Gráfico de barras
                distribuciones = []
                etiquetas = []
                colores = []
                
                for cluster_id in range(self.resultados.k):
                    num_puntos = np.sum(grupos == cluster_id)
                    distribuciones.append(num_puntos)
                    etiquetas.append(f'C{cluster_id+1}')
                    colores.append(self._hex_a_rgb_normalizado(self.resultados.colores_clusters[cluster_id]))
                
                bars = ax_stats.bar(etiquetas, distribuciones, color=colores)
                ax_stats.set_title('Distribución')
                ax_stats.set_ylabel('Puntos')
                
                # Información de progreso
                ax_info.axis('off')
                progreso = f"Frame {frame_idx + 1}/{len(frames)} | "
                progreso += f"Iteración {iteracion}/{num_iteraciones-1}"
                ax_info.text(0.5, 0.5, progreso, transform=ax_info.transAxes,
                           ha='center', va='center', fontsize=12,
                           bbox=dict(boxstyle="round,pad=0.5", 
                                   facecolor='yellow', alpha=0.5))
            
            plt.tight_layout()
        
        # Crear animación
        anim = FuncAnimation(fig, update, frames=len(frames), 
                           interval=1000/fps, repeat=True)
        
        # Guardar GIF
        writer = PillowWriter(fps=fps)
        anim.save(nombre_archivo, writer=writer)
        plt.close(fig)
        
        print(f"✅ GIF guardado como: {nombre_archivo}")
        return nombre_archivo
    
    def mostrar_evolucion_completa(self, puntos: List[PuntoImagen],
                                  pausar_entre_iteraciones: bool = True,
                                  generar_gif: bool = True):
        """
        Muestra la evolución completa del algoritmo de forma interactiva.
        """
        print("\n" + "="*70)
        print("VISUALIZACIÓN COMPLETA DE K-MEANS")
        print("="*70)
        
        # 1. Mostrar cada iteración
        print("\n📊 Mostrando evolución iteración por iteración...")
        
        for i in range(len(self.resultados.historial_centroides)):
            if pausar_entre_iteraciones and i > 0:
                input(f"\nPresione ENTER para ver iteración {i}...")
            
            # Mostrar iteración
            self.visualizar_iteracion(i, puntos, mostrar=True)
        
        # 2. Mostrar resumen de todas las iteraciones
        if pausar_entre_iteraciones:
            input("\n📈 Presione ENTER para ver el resumen de iteraciones...")
        
        print("\n📈 Mostrando resumen de todas las iteraciones...")
        self.crear_resumen_iteraciones(puntos, mostrar=True)
        
        # 3. Mostrar estadísticas finales
        if pausar_entre_iteraciones:
            input("\n📊 Presione ENTER para ver las estadísticas finales...")
        
        print("\n📊 Mostrando análisis completo con estadísticas...")
        self.crear_visualizacion_estadisticas(puntos, mostrar=True)
        
        # 4. Generar GIF si se solicita
        if generar_gif:
            if pausar_entre_iteraciones:
                respuesta = input("\n🎬 ¿Desea generar un GIF animado? (s/n): ")
                if respuesta.lower() != 's':
                    generar_gif = False
            
            if generar_gif:
                self.generar_gif_mejorado(puntos, mostrar_estadisticas=True)
        
        print("\n" + "="*70)
        print("✅ Visualización completa finalizada")
        print("="*70)