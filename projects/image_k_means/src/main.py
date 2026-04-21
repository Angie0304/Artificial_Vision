"""
Programa principal para ejecutar K-means con interfaz de menú.

Integra todos los módulos existentes y nuevos para proporcionar
una experiencia completa de agrupamiento por K-means.

"Los errores nunca deberían pasar silenciosamente."
"Ante la ambigüedad, rechaza la tentación de adivinar."
"""

from ui.menu import Menu, Opcion
from utils.funciones_estandar_V2 import input_validado, eleccion
from modules.imagen import Imagen
from modules.algoritmo_kmeans import AlgoritmoKMeans, ResultadosKMeans
from modules.visualizador_kmeans_matplotlib import VisualizadorKMeansMatplotlib
from typing import Optional, List
from modules.punto import PuntoImagen
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


class EstadoAplicacion:
    """Mantiene el estado global de la aplicación."""
    
    def __init__(self):
        self.imagen: Imagen = Imagen()
        self.algoritmo: Optional[AlgoritmoKMeans] = None
        self.puntos: List[PuntoImagen] = []
        self.resultados: Optional[ResultadosKMeans] = None
        self.visualizador: Optional[VisualizadorKMeansMatplotlib] = None
    
    def reset_algoritmo(self):
        """Resetea el estado del algoritmo."""
        self.algoritmo = None
        self.puntos = []
        self.resultados = None
        self.visualizador = None
    
    def tiene_imagen(self) -> bool:
        """Verifica si hay una imagen cargada."""
        return self.imagen.seleccionada
    
    def tiene_puntos(self) -> bool:
        """Verifica si hay puntos generados."""
        return len(self.puntos) > 0
    
    def tiene_resultados(self) -> bool:
        """Verifica si hay resultados de K-means."""
        return self.resultados is not None


# Opciones del menú

class OpcionSeleccionarImagen(Opcion):
    """Opción para seleccionar una imagen."""
    
    def __init__(self, estado: EstadoAplicacion):
        super().__init__(
            'Seleccionar imagen',
            'Carga una imagen para aplicar K-means'
        )
        self.estado = estado
    
    def ejecutar(self):
        print("\n=== SELECCIONAR IMAGEN ===")
        
        if self.estado.tiene_imagen():
            if not eleccion("Ya hay una imagen cargada. ¿Desea cargar otra?"):
                return
        
        if self.estado.imagen.seleccionar_imagen():
            print(f"✓ Imagen cargada exitosamente")
            print(f"  Dimensiones: {self.estado.imagen.ancho}x{self.estado.imagen.alto}")
            print(f"  Nombre: {self.estado.imagen.nombre}")
            
            # Reset del algoritmo al cargar nueva imagen
            self.estado.reset_algoritmo()
            
            # Mostrar imagen
            if eleccion("¿Desea ver la imagen cargada?", por_defecto=True):
                self.estado.imagen.dibujar_imagen(
                    mostrar_original=True,
                    titulo_ventana="Imagen Original"
                )
        else:
            print("✗ No se pudo cargar la imagen")


class OpcionGenerarPuntos(Opcion):
    """Opción para generar puntos aleatorios."""
    
    def __init__(self, estado: EstadoAplicacion):
        super().__init__(
            'Generar puntos aleatorios',
            'Genera puntos aleatorios para el algoritmo K-means'
        )
        self.estado = estado
    
    def ejecutar(self):
        print("\n=== GENERAR PUNTOS ALEATORIOS ===")
        
        if not self.estado.tiene_imagen():
            print("✗ Primero debe cargar una imagen")
            return
        
        if self.estado.tiene_puntos():
            print(f"Ya hay {len(self.estado.puntos)} puntos generados")
            if not eleccion("¿Desea generar nuevos puntos?"):
                return
        
        # Solicitar número de puntos
        n_puntos = input_validado(
            "Número de puntos a generar (recomendado: 50-200)",
            'entero'
        )
        
        if n_puntos < 10:
            print("⚠ Advertencia: Pocos puntos pueden no representar bien la imagen")
            if not eleccion("¿Continuar de todos modos?"):
                return
        
        # Generar puntos
        print(f"\nGenerando {n_puntos} puntos aleatorios...")
        self.estado.algoritmo = AlgoritmoKMeans(self.estado.imagen)
        self.estado.puntos = self.estado.algoritmo.generar_puntos_aleatorios(n_puntos)
        
        print(f"✓ {n_puntos} puntos generados exitosamente")
        
        # Mostrar puntos en la imagen
        if eleccion("¿Desea ver los puntos generados?", por_defecto=True):
            # Convertir PuntoImagen a Punto para visualización
            puntos_viz = []
            for p in self.estado.puntos:
                puntos_viz.append(p)  # PuntoImagen hereda de Punto
            
            self.estado.imagen.dibujar_imagen_con_thread(
                mostrar_original=False,
                puntos_adicionales=puntos_viz,
                titulo_ventana="Puntos Aleatorios Generados"
            )


class OpcionEjecutarKMeans(Opcion):
    """Opción para ejecutar el algoritmo K-means."""
    
    def __init__(self, estado: EstadoAplicacion):
        super().__init__(
            'Ejecutar K-means',
            'Ejecuta el algoritmo de agrupamiento K-means'
        )
        self.estado = estado
    
    def ejecutar(self):
        print("\n=== EJECUTAR ALGORITMO K-MEANS ===")
        
        if not self.estado.tiene_imagen():
            print("✗ Primero debe cargar una imagen")
            return
        
        if not self.estado.tiene_puntos():
            print("✗ Primero debe generar puntos aleatorios")
            return
        
        # Solicitar valor de k
        max_k = min(10, len(self.estado.puntos) // 5)  # Máximo razonable
        print(f"\nNúmero de puntos disponibles: {len(self.estado.puntos)}")
        print(f"Rango recomendado de k: 2-{max_k}")
        
        k = input_validado(
            "Ingrese el valor de k (número de clusters)",
            'entero'
        )
        
        if k < 2:
            print("✗ k debe ser al menos 2")
            return
        
        if k > len(self.estado.puntos):
            print(f"✗ k no puede ser mayor que el número de puntos ({len(self.estado.puntos)})")
            return
        
        if k > max_k:
            print(f"⚠ Advertencia: k={k} es alto para {len(self.estado.puntos)} puntos")
            if not eleccion("¿Continuar de todos modos?"):
                return
        
        # Opciones avanzadas
        max_iter = 50
        if eleccion("¿Desea configurar opciones avanzadas?", por_defecto=False):
            max_iter = input_validado(
                "Número máximo de iteraciones (default: 50)",
                'entero'
            )
        
        # Ejecutar algoritmo
        print(f"\nEjecutando K-means con k={k}...")
        try:
            self.estado.resultados = self.estado.algoritmo.ejecutar(
                k=k,
                max_iteraciones=max_iter
            )
            
            print("\n✓ K-means completado exitosamente")
            
            # Crear visualizador mejorado
            self.estado.visualizador = VisualizadorKMeansMatplotlib(
                self.estado.imagen,
                self.estado.resultados
            )
            
        except Exception as e:
            print(f"✗ Error al ejecutar K-means: {e}")


class OpcionVisualizarResultados(Opcion):
    """Opción para visualizar los resultados."""
    
    def __init__(self, estado: EstadoAplicacion):
        super().__init__(
            'Visualizar resultados',
            'Muestra las visualizaciones de los resultados K-means'
        )
        self.estado = estado
    
    def ejecutar(self):
        print("\n=== VISUALIZAR RESULTADOS ===")
        
        if not self.estado.tiene_resultados():
            print("✗ No hay resultados para mostrar. Ejecute K-means primero")
            return
        
        opciones = [
            "Ver evolución completa (interactiva)",
            "Ver solo iteración específica",
            "Ver resumen de todas las iteraciones",
            "Ver estadísticas finales detalladas",
            "Generar GIF animado",
            "Todas las visualizaciones automáticas"
        ]
        
        print("\nOpciones de visualización:")
        for i, opcion in enumerate(opciones, 1):
            print(f"{i}. {opcion}")
        print("0. Volver")
        
        eleccion_viz = input_validado(
            "Seleccione una opción",
            'rango_entero',
            (0, len(opciones))
        )[1]
        
        if eleccion_viz == 0:
            return
        elif eleccion_viz == 1:
            # Evolución completa interactiva
            self.estado.visualizador.mostrar_evolucion_completa(
                self.estado.puntos,
                pausar_entre_iteraciones=True,
                generar_gif=False
            )
        elif eleccion_viz == 2:
            # Iteración específica
            max_iter = len(self.estado.resultados.historial_centroides) - 1
            print(f"\nIteraciones disponibles: 0 (inicial) a {max_iter} (final)")
            iter_num = input_validado(
                "Número de iteración a visualizar",
                'rango_entero',
                (0, max_iter)
            )[1]
            self.estado.visualizador.visualizar_iteracion(
                iter_num, 
                self.estado.puntos, 
                mostrar=True
            )
        elif eleccion_viz == 3:
            # Resumen de iteraciones
            self.estado.visualizador.crear_resumen_iteraciones(
                self.estado.puntos,
                mostrar=True
            )
        elif eleccion_viz == 4:
            # Estadísticas finales
            self.estado.visualizador.crear_visualizacion_estadisticas(
                self.estado.puntos,
                mostrar=True
            )
        elif eleccion_viz == 5:
            # Generar GIF
            incluir_stats = eleccion(
                "¿Incluir estadísticas en el GIF?",
                por_defecto=True
            )
            nombre_gif = self.estado.visualizador.generar_gif_mejorado(
                self.estado.puntos, 
                mostrar_estadisticas=incluir_stats
            )
            print(f"✓ GIF generado: {nombre_gif}")
        elif eleccion_viz == 6:
            # Todas las visualizaciones
            self.estado.visualizador.mostrar_evolucion_completa(
                self.estado.puntos,
                pausar_entre_iteraciones=False,
                generar_gif=True
            )


class OpcionComparacionMultipleK(Opcion):
    """Opción para comparar resultados con diferentes valores de k."""
    
    def __init__(self, estado: EstadoAplicacion):
        super().__init__(
            'Comparar múltiples valores de k',
            'Ejecuta K-means con diferentes k y compara resultados'
        )
        self.estado = estado
    
    def ejecutar(self):
        print("\n=== COMPARACIÓN DE MÚLTIPLES K ===")
        
        if not self.estado.tiene_imagen():
            print("✗ Primero debe cargar una imagen")
            return
        
        if not self.estado.tiene_puntos():
            print("✗ Primero debe generar puntos aleatorios")
            return
        
        # Solicitar rango de k
        print(f"Número de puntos: {len(self.estado.puntos)}")
        k_min = input_validado("Valor mínimo de k", 'entero')
        k_max = input_validado("Valor máximo de k", 'entero')
        
        if k_min < 2:
            k_min = 2
        if k_max > min(10, len(self.estado.puntos) // 5):
            k_max = min(10, len(self.estado.puntos) // 5)
        
        if k_min > k_max:
            k_min, k_max = k_max, k_min
        
        print(f"\nComparando k desde {k_min} hasta {k_max}")
        
        resultados_comparacion = []
        
        for k in range(k_min, k_max + 1):
            print(f"\nEjecutando K-means con k={k}...")
            try:
                resultado = self.estado.algoritmo.ejecutar(k=k, max_iteraciones=30)
                resultados_comparacion.append((k, resultado))
                
                # Mostrar estadísticas rápidas
                stats = resultado.obtener_estadisticas()
                print(f"  Iteraciones: {stats['iteraciones']}")
                print(f"  Distribución: ", end="")
                for i in range(k):
                    info = stats['clusters'][i]
                    print(f"{info['porcentaje']}% ", end="")
                print()
                
            except Exception as e:
                print(f"  Error: {e}")
        
        # Mostrar comparación visual
        if eleccion("\n¿Desea ver una comparación visual?", por_defecto=True):
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(1, len(resultados_comparacion), 
                                   figsize=(5*len(resultados_comparacion), 5))
            
            if len(resultados_comparacion) == 1:
                axes = [axes]
            
            for idx, (k, resultado) in enumerate(resultados_comparacion):
                ax = axes[idx]
                ax.imshow(self.estado.imagen.imagen_original)
                ax.set_title(f'k = {k}', fontsize=14, fontweight='bold')
                ax.axis('off')
                
                # Dibujar puntos coloreados
                grupos_finales = resultado.grupos_finales
                for cluster_id in range(k):
                    indices = np.where(grupos_finales == cluster_id)[0]
                    if len(indices) > 0:
                        xs = [self.estado.puntos[i].x for i in indices]
                        ys = [self.estado.puntos[i].y for i in indices]
                        color = resultado.colores_clusters[cluster_id]
                        ax.scatter(xs, ys, c=color, s=20, alpha=0.7)
            
            plt.tight_layout()
            plt.show()


def crear_menu_principal():
    """Crea el menú principal de la aplicación."""
    estado = EstadoAplicacion()
    
    opciones = [
        OpcionSeleccionarImagen(estado),
        OpcionGenerarPuntos(estado),
        OpcionEjecutarKMeans(estado),
        OpcionVisualizarResultados(estado),
        OpcionComparacionMultipleK(estado)
    ]
    
    menu = Menu(
        titulo='K-means - Agrupamiento por Color',
        opciones=opciones,
        texto_eleccion='Seleccione una opción',
        opcion_salir=True,
        confirmacion_salir=True
    )
    
    return menu


def main():
    """Función principal del programa."""
    print("="*60)
    print("ALGORITMO K-MEANS - AGRUPAMIENTO POR COLOR")
    print("="*60)
    print("\nEste programa aplica K-means para agrupar píxeles")
    print("según la similitud de sus colores RGB.")
    print("\nPasos:")
    print("1. Cargar una imagen")
    print("2. Generar puntos aleatorios")
    print("3. Ejecutar K-means")
    print("4. Visualizar resultados")
    
    menu = crear_menu_principal()
    menu.iniciar()
    
    print("\n¡Gracias por usar K-means!")


if __name__ == '__main__':
    # Asegurar que matplotlib no bloquee
    import matplotlib
    matplotlib.use('TkAgg')
    
    main()