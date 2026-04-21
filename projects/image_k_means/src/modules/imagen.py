""" 
Clase Imagen refactorizada con función dibujar_imagen optimizada
y funcionalidad de guardado.

DECISIONES DE DISEÑO:
1. Almacenamiento de puntos en memoria: ELEGIDO
   - Los puntos se almacenan permanentemente en self.puntos_seleccionados
   - Ventajas: Mayor rendimiento, evita recálculos, facilita manipulación
   - Desventajas: Uso de memoria (mínimo para aplicaciones típicas)
   - Justificación: Los puntos raramente cambian y el costo de memoria es despreciable

2. Factor de escala basado en resolución:
   - Se calcula dinámicamente según pantalla y imagen
   - Mantiene proporción original (aspect ratio)
   - Límite del 80% de pantalla para usabilidad
"""

import platform
from typing import List, Optional, Union, Tuple
import numpy as np
from utils.funciones_estandar_V2 import cargar_enlace_imagen, seleccionar_carpeta
import cv2 as cv
import tkinter as tk
from pathlib import Path
from modules.punto import Punto
import os
import threading
import time	    

def configurar_opencv_multiplataforma():
    """
    Configura OpenCV para funcionar óptimamente en cualquier sistema operativo
    evitando warnings de DPI y problemas de compatibilidad.
    """
    sistema = platform.system().lower()
    
    try:
        if sistema == 'windows':
            # Configuración específica para Windows
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
            os.environ['QT_SCALE_FACTOR'] = '1'
            os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
            
            # Intentar configurar DPI awareness nativo de Windows
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # System DPI aware
            except:
                pass
                
        elif sistema == 'darwin':  # macOS
            # Configuración para macOS
            os.environ['QT_MAC_WANTS_LAYER'] = '1'
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
            
        elif sistema == 'linux':
            # Configuración para Linux
            os.environ['QT_X11_NO_MITSHM'] = '1'  # Evita problemas con algunos drivers
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
            
        # Configuraciones generales para todos los sistemas
        os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'  # Reduce logs verbosos
        
        # Verificar que OpenCV funciona correctamente
        test_window = "opencv_test"
        cv.namedWindow(test_window, cv.WINDOW_NORMAL)
        cv.destroyWindow(test_window)
        
        print(f"OpenCV configurado para {sistema.capitalize()}")
        return True
        
    except Exception as e:
        print(f"Advertencia: No se pudo configurar OpenCV óptimamente: {e}")
        return False

# Función para llamar al inicio de tu aplicación
def inicializar_aplicacion():
    """
    Función para llamar una sola vez al inicio de tu aplicación.
    """
    print(f"Iniciando aplicación en {platform.system()} {platform.release()}")
    configurar_opencv_multiplataforma()
    
    # Verificar versión de OpenCV
    print(f"Versión de OpenCV: {cv.__version__}")
    
    # Verificar backends disponibles
    try:
        backends = cv.getBuildInformation()
        if 'Qt' in backends:
            print("Backend Qt disponible")
        if 'GTK' in backends:
            print("Backend GTK disponible")
    except:
        pass

# Configurar OpenCV al inicio del módulo
configurar_opencv_multiplataforma()
inicializar_aplicacion()

class Imagen:
    """Clase para manejar la imagen seleccionada con funcionalidades avanzadas."""
    
    def __init__(self):
        self.seleccionada = False
        self.imagen_original = None
        self.imagen_actual = None  # Imagen con modificaciones (puntos, rectángulos, etc.)
        self.puntos_seleccionados: List[Punto] = []
        self.alto = 0
        self.ancho = 0
        self.nombre: Optional[str] = None
        self.factor_escala = 1.0  # Factor de escala actual para mostrar
        self.dimensiones_pantalla = None  # Se calculará dinámicamente

    def seleccionar_imagen(self) -> bool:
        """Lógica para seleccionar una imagen."""
        ruta = cargar_enlace_imagen()
        if not ruta:
            return None

        # Cargar imagen y crear una copia para trabajar
        self.imagen_original = cv.imread(str(ruta))
        self.imagen_actual = self.imagen_original.copy() if self.imagen_original is not None else None

        if self.imagen_original is not None:
            self.seleccionada = True
            self.nombre = ruta.name
            # Obtener información sobre las dimensiones
            self.alto = self.imagen_original.shape[0]
            self.ancho = self.imagen_original.shape[1]
            print(f"Imagen cargada con éxito. Dimensiones: {self.ancho}x{self.alto}")
            return True
        else:
            print("Error: No se pudo cargar la imagen.")
            return False
        return None

    def _obtener_dimensiones_pantalla(self) -> Tuple[int, int]:
        """
        Obtiene las dimensiones de la pantalla de forma segura.
        
        Returns:
            Tuple con (ancho, alto) de la pantalla
        """
        try:
            if self.dimensiones_pantalla is None:
                root = tk.Tk()
                root.withdraw()  # Ocultar ventana
                ancho_pantalla = root.winfo_screenwidth()
                alto_pantalla = root.winfo_screenheight()
                root.destroy()
                self.dimensiones_pantalla = (ancho_pantalla, alto_pantalla)
            return self.dimensiones_pantalla
        except Exception as e:
            print(f"Error al obtener dimensiones de pantalla: {e}")
            # Valores por defecto comunes
            return (1920, 1080)

    def _calcular_factor_escala(self, porcentaje_pantalla: float = 0.8) -> float:
        """
        Calcula el factor de escala para que la imagen no exceda el porcentaje
        especificado del tamaño de pantalla, manteniendo las proporciones.
        
        Args:
            porcentaje_pantalla: Porcentaje de pantalla a usar (0.0 a 1.0)
            
        Returns:
            Factor de escala a aplicar
            
        Algoritmo:
        1. Obtener dimensiones de pantalla y imagen
        2. Calcular límites máximos (pantalla * porcentaje)
        3. Calcular factor para ancho y alto por separado
        4. Usar el menor factor para mantener proporciones
        """
        if not self.seleccionada or self.imagen_original is None:
            return 1.0
            
        ancho_pantalla, alto_pantalla = self._obtener_dimensiones_pantalla()
        
        # Límites máximos basados en porcentaje de pantalla
        max_ancho = int(ancho_pantalla * porcentaje_pantalla)
        max_alto = int(alto_pantalla * porcentaje_pantalla)
        
        # Calcular factores de escala para cada dimensión
        factor_ancho = max_ancho / self.ancho
        factor_alto = max_alto / self.alto
        
        # Usar el menor factor para mantener proporciones
        factor_escala = min(factor_ancho, factor_alto, 1.0)  # No agrandar si ya es pequeña
        
        return factor_escala

    def aplicar_puntos_a_imagen(self, imagen: np.ndarray, 
                                puntos_adicionales: Optional[List[Punto]] = None,
                                factor_escala: float = 1.0,
                                incluir_etiquetas: bool = False
                                ) -> np.ndarray:
        """
        Aplica todos los puntos (almacenados y adicionales) a una imagen.
        
        Args:
            imagen: Imagen base donde dibujar
            puntos_adicionales: Puntos temporales adicionales
            factor_escala: Factor de escala para ajustar coordenadas
            
        Returns:
            Imagen con puntos dibujados
        """
        imagen_con_puntos = imagen.copy()
        
        # Dibujar puntos almacenados permanentemente
        for punto in self.puntos_seleccionados:
            self._dibujar_punto_escalado(imagen_con_puntos, punto, factor_escala, incluir_etiquetas)
        
        # Dibujar puntos adicionales temporales
        if puntos_adicionales:
            for punto in puntos_adicionales:
                self._dibujar_punto_escalado(imagen_con_puntos, punto, factor_escala, incluir_etiquetas)
                
        return imagen_con_puntos

    def _dibujar_punto_escalado(self, imagen: np.ndarray, punto: Punto, factor_escala: float, incluir_etiquetas: bool):
        """
        Dibuja un punto en la imagen considerando el factor de escala.
        
        Args:
            imagen: Imagen donde dibujar
            punto: Punto a dibujar
            factor_escala: Factor de escala aplicado
        """
        # Ajustar coordenadas según escala
        x_escalado = int(punto.x * factor_escala)
        y_escalado = int(punto.y * factor_escala)
        
        # Ajustar grosor según escala (mínimo 2 píxeles)
        grosor = max(2, int(5 * factor_escala))
        
        # Color por defecto o del punto
        color = punto.color if punto.color else (0, 0, 255)  # Rojo por defecto
        
        # Dibujar punto
        cv.circle(imagen, (x_escalado, y_escalado), grosor, color, -1)
        
        # Dibujar etiqueta si existe
        if punto.etiqueta and incluir_etiquetas:
            font = cv.FONT_HERSHEY_SIMPLEX
            font_scale = max(0.4, 0.5 * factor_escala)
            color_texto = (255, 255, 255)  # Blanco
            thickness = max(1, int(2 * factor_escala))
            
            # Posición del texto (ligeramente desplazado del punto)
            pos_texto = (x_escalado + grosor + 2, y_escalado - grosor)
            cv.putText(imagen, punto.etiqueta, pos_texto, font, font_scale, color_texto, thickness)

    def dibujar_imagen(self, 
                    mostrar_original: bool = False,
                    puntos_adicionales: Optional[List[Punto]] = None,
                    porcentaje_pantalla: float = 0.8,
                    titulo_ventana: str = "Imagen",
                    guardar_automaticamente: bool = False,
                    incluir_etiquetas: bool = False,
                    timeout_segundos: int = 0  # 0 = sin timeout
                    ) -> bool:
        """
        Función principal para mostrar la imagen con compatibilidad multiplataforma mejorada.
        
        Mejoras implementadas:
        - Corrección en el cálculo de coordenadas para imágenes horizontales
        - Manejo robusto del cierre de ventana
        - Sistema de timeout opcional
        - Mejor manejo de errores
        
        Args:
            mostrar_original: Si mostrar imagen original sin modificaciones
            puntos_adicionales: Lista de puntos temporales adicionales
            porcentaje_pantalla: Porcentaje de pantalla a usar (0.1 a 1.0)
            titulo_ventana: Título de la ventana
            guardar_automaticamente: Si guardar automáticamente la imagen
            incluir_etiquetas: Si mostrar etiquetas de los puntos
            timeout_segundos: Tiempo límite en segundos (0 = sin límite)
            
        Returns:
            True si se mostró correctamente, False en caso de error
        """
        
        # Configurar OpenCV para el sistema actual
        configurar_opencv_multiplataforma()
        
        # Validaciones de entrada
        if not self.seleccionada or self.imagen_original is None:
            print("Error: No hay ninguna imagen cargada. Use seleccionar_imagen() primero.")
            return False
            
        if not 0.1 <= porcentaje_pantalla <= 1.0:
            print("Error: porcentaje_pantalla debe estar entre 0.1 y 1.0")
            return False
            
        if mostrar_original and puntos_adicionales:
            print("Advertencia: Se especificaron puntos_adicionales con mostrar_original=True.")
            print("Los puntos adicionales serán ignorados.")
            puntos_adicionales = None
        
        try:
            # Cálculo mejorado de factor de escala
            self.factor_escala = self._calcular_factor_escala(porcentaje_pantalla)
            nuevo_ancho = int(self.ancho * self.factor_escala)
            nuevo_alto = int(self.alto * self.factor_escala)
            
            print(f"Factor de escala aplicado: {self.factor_escala:.3f}")
            print(f"Dimensiones originales: {self.ancho}x{self.alto}")
            print(f"Dimensiones escaladas: {nuevo_ancho}x{nuevo_alto}")
            
            # Preparación de imagen ANTES del escalado
            if mostrar_original:
                imagen_base = self.imagen_original.copy()
            else:
                # CORRECCIÓN 1: Aplicar puntos a imagen original y luego escalar
                imagen_base = self.imagen_original.copy()
                
                # Dibujar puntos permanentes en escala original
                for punto in self.puntos_seleccionados:
                    self._dibujar_punto_original(imagen_base, punto, incluir_etiquetas)
                
                # Dibujar puntos adicionales en escala original
                if puntos_adicionales:
                    for punto in puntos_adicionales:
                        self._dibujar_punto_original(imagen_base, punto, incluir_etiquetas)
            
            # Redimensionar después de dibujar los puntos
            if self.factor_escala != 1.0:
                imagen_a_mostrar = cv.resize(
                    imagen_base, 
                    (nuevo_ancho, nuevo_alto), 
                    interpolation=cv.INTER_AREA
                )
            else:
                imagen_a_mostrar = imagen_base
            
            # Crear ventana con configuración robusta
            ventana_flags = cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO
            
            try:
                cv.namedWindow(titulo_ventana, ventana_flags)
            except:
                # Fallback a configuración básica
                cv.namedWindow(titulo_ventana, cv.WINDOW_NORMAL)
            
            # Configurar tamaño de ventana de forma segura
            try:
                cv.resizeWindow(titulo_ventana, nuevo_ancho, nuevo_alto)
            except:
                pass
            
            # Mostrar imagen
            cv.imshow(titulo_ventana, imagen_a_mostrar)
            
            # Información en consola
            tipo_vista = "original" if mostrar_original else "con modificaciones"
            num_puntos = len(self.puntos_seleccionados)
            num_adicionales = len(puntos_adicionales) if puntos_adicionales else 0
            
            print(f"Mostrando imagen {tipo_vista}")
            print(f"Puntos permanentes: {num_puntos}")
            if num_adicionales > 0:
                print(f"Puntos temporales: {num_adicionales}")
            
            if timeout_segundos > 0:
                print(f"Presione cualquier tecla o espere {timeout_segundos} segundos...")
            else:
                print("Presione cualquier tecla para cerrar la imagen...")
            
            # CORRECCIÓN 2: Manejo robusto del cierre de ventana
            # Enfoque híbrido: polling + timeout adaptativo
            print("NOTA: Para cerrar la ventana use ESC, ESPACIO o cualquier tecla.")
            print("      El cierre con X puede no funcionar en todos los sistemas.")
            
            tiempo_inicio = cv.getTickCount() if timeout_segundos > 0 else None
            ultimo_check = cv.getTickCount()
            intervalo_check = 0.1  # Verificar cada 100ms
            
            while True:
                # Esperar tecla con timeout muy corto
                tecla = cv.waitKey(1) & 0xFF
                
                # Si se presionó una tecla, salir inmediatamente
                if tecla != 255:
                    if tecla == 27:  # ESC
                        print("Cerrado con tecla ESC")
                    elif tecla == 32:  # ESPACIO
                        print("Cerrado con tecla ESPACIO")
                    else:
                        print(f"Cerrado con tecla: {chr(tecla) if 32 <= tecla <= 126 else f'código {tecla}'}")
                    break
                
                # Verificar cierre de ventana cada cierto intervalo
                tiempo_actual = cv.getTickCount()
                if (tiempo_actual - ultimo_check) / cv.getTickFrequency() >= intervalo_check:
                    ultimo_check = tiempo_actual
                    
                    try:
                        # Verificar múltiples propiedades para detectar cierre
                        props_ok = 0
                        
                        # Test 1: Propiedad de visibilidad
                        try:
                            visible = cv.getWindowProperty(titulo_ventana, cv.WND_PROP_VISIBLE)
                            if visible > 0:
                                props_ok += 1
                        except:
                            pass
                        
                        # Test 2: Propiedad de aspect ratio  
                        try:
                            aspect = cv.getWindowProperty(titulo_ventana, cv.WND_PROP_ASPECT_RATIO)
                            if aspect >= 0:
                                props_ok += 1
                        except:
                            pass
                        
                        # Test 3: Propiedad de fullscreen
                        try:
                            fullscreen = cv.getWindowProperty(titulo_ventana, cv.WND_PROP_FULLSCREEN)
                            if fullscreen >= 0:
                                props_ok += 1
                        except:
                            pass
                        
                        # Si ninguna propiedad es accesible, probablemente la ventana fue cerrada
                        if props_ok == 0:
                            print("Ventana cerrada por el usuario (detectado por pérdida de propiedades)")
                            break
                            
                    except Exception as e:
                        print("Ventana cerrada por el usuario (detectado por excepción)")
                        break
                
                # Verificar timeout si está configurado
                if timeout_segundos > 0 and tiempo_inicio is not None:
                    tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / cv.getTickFrequency()
                    if tiempo_transcurrido >= timeout_segundos:
                        print(f"Timeout alcanzado ({timeout_segundos} segundos)")
                        break
            
            # Limpiar ventanas de forma segura
            try:
                cv.destroyWindow(titulo_ventana)
                cv.destroyAllWindows()
            except:
                pass
            
            # Guardado automático si se solicita
            if guardar_automaticamente:
                self.guardar_imagen(imagen_a_mostrar, f"{titulo_ventana}_{tipo_vista}")
            
            return True
            
        except Exception as e:
            print(f"Error al mostrar la imagen: {e}")
            # Limpiar ventanas en caso de error
            try:
                cv.destroyAllWindows()
            except:
                pass
            return False

    def _dibujar_punto_original(self, imagen: np.ndarray, punto: Punto, incluir_etiquetas: bool):
        """
        Dibuja un punto en la imagen en coordenadas originales (sin escalar).
        
        Esta función reemplaza _dibujar_punto_escalado para corregir el problema
        de coordenadas en imágenes horizontales.
        
        Args:
            imagen: Imagen donde dibujar (en escala original)
            punto: Punto a dibujar
            incluir_etiquetas: Si incluir etiquetas de texto
        """
        # Usar coordenadas originales directamente
        x = int(punto.x)
        y = int(punto.y)
        
        # Validar que las coordenadas estén dentro de la imagen
        if x < 0 or x >= self.ancho or y < 0 or y >= self.alto:
            print(f"Advertencia: Punto ({x}, {y}) fuera de los límites de la imagen ({self.ancho}x{self.alto})")
            return
        
        # Calcular grosor proporcional al tamaño de la imagen
        # Para imágenes grandes, puntos más grandes
        dimension_mayor = max(self.ancho, self.alto)
        grosor = max(3, int(dimension_mayor * 0.003))  # 0.3% de la dimensión mayor
        
        # Color por defecto o del punto
        color = punto.color if punto.color else (0, 0, 255)  # Rojo por defecto
        
        # Dibujar punto
        cv.circle(imagen, (x, y), grosor, color, -1)
        
        # Dibujar etiqueta si existe
        if punto.etiqueta and incluir_etiquetas:
            font = cv.FONT_HERSHEY_SIMPLEX
            # Escala de fuente proporcional a la imagen
            font_scale = max(0.5, dimension_mayor * 0.0008)
            color_texto = (255, 255, 255)  # Blanco
            thickness = max(1, int(dimension_mayor * 0.001))
            
            # Posición del texto (ligeramente desplazado del punto)
            pos_texto = (x + grosor + 5, y - grosor - 5)
            
            # Verificar que el texto no se salga de la imagen
            text_size = cv.getTextSize(punto.etiqueta, font, font_scale, thickness)[0]
            if pos_texto[0] + text_size[0] > self.ancho:
                pos_texto = (x - text_size[0] - 5, pos_texto[1])
            if pos_texto[1] - text_size[1] < 0:
                pos_texto = (pos_texto[0], y + grosor + text_size[1] + 5)
            
            cv.putText(imagen, punto.etiqueta, pos_texto, font, font_scale, color_texto, thickness)

    def agregar_punto(self, coordenadas: Union[Tuple[float, float], List[float]], 
                     color: Optional[Tuple[int, int, int]] = None,
                     etiqueta: Optional[str] = None) -> bool:
        """
        Agrega un punto permanente a la imagen.
        
        Args:
            coordenadas: Coordenadas (x, y) del punto
            color: Color RGB del punto (opcional)
            etiqueta: Etiqueta del punto (opcional)
            
        Returns:
            True si se agregó correctamente
        """
        if not self.seleccionada:
            print("Error: No hay imagen cargada")
            return False
            
        try:
            punto = Punto(coordenadas, color, etiqueta)
            self.puntos_seleccionados.append(punto)
            print(f"Punto agregado: {punto}")
            return True
        except Exception as e:
            print(f"Error al agregar punto: {e}")
            return False

    def limpiar_puntos(self):
        """Elimina todos los puntos permanentes."""
        self.puntos_seleccionados.clear()
        print("Todos los puntos han sido eliminados")

    def resetear_cambios(self):
        """Resetea la imagen a su estado original."""
        if self.imagen_original is not None:
            self.imagen_actual = self.imagen_original.copy()
            self.puntos_seleccionados.clear()
            print("Imagen reseteada a su estado original")
        else:
            print("Error: No hay imagen original para resetear")

    def guardar_imagen(self, imagen_personalizada: Optional[np.ndarray] = None, 
                      nombre_sugerido: Optional[str] = None) -> bool:
        """
        Guarda la imagen actual o una imagen personalizada.
        
        Args:
            imagen_personalizada: Imagen específica a guardar (opcional)
            nombre_sugerido: Nombre sugerido para el archivo (opcional)
            
        Returns:
            True si se guardó correctamente
        """
        if not self.seleccionada and imagen_personalizada is None:
            print("Error: No hay imagen para guardar")
            return False
            
        try:
            # Seleccionar carpeta de destino
            carpeta_destino = seleccionar_carpeta("Seleccionar carpeta para guardar imagen")
            if not carpeta_destino:
                print("Guardado cancelado por el usuario")
                return False
            
            # Determinar imagen a guardar
            if imagen_personalizada is not None:
                imagen_guardar = imagen_personalizada
            else:
                imagen_guardar = self.imagen_actual if self.imagen_actual is not None else self.imagen_original
            
            # Generar nombre de archivo
            if nombre_sugerido:
                nombre_base = nombre_sugerido
            else:
                nombre_base = f"{Path(self.nombre).stem}_modificada" if self.nombre else "imagen_guardada"
            
            # Crear ruta completa
            ruta_guardado = carpeta_destino / f"{nombre_base}.png"
            
            # Evitar sobreescribir archivos
            contador = 1
            while ruta_guardado.exists():
                ruta_guardado = carpeta_destino / f"{nombre_base}_{contador}.png"
                contador += 1
            
            # Guardar imagen
            exito = cv.imwrite(str(ruta_guardado), imagen_guardar)
            
            if exito:
                print(f"Imagen guardada exitosamente en: {ruta_guardado}")
                return True
            else:
                print("Error: No se pudo guardar la imagen")
                return False
                
        except Exception as e:
            print(f"Error al guardar imagen: {e}")
            return False

    def obtener_color_pixel(self, coordenadas):
        """Obtener color RGB de un pixel"""
        try:
            # Asegurar que las coordenadas están dentro de los límites de la imagen
            x, y = int(coordenadas[0]), int(coordenadas[1])
            x = max(0, min(x, self.ancho - 1))
            y = max(0, min(y, self.alto - 1))
            
            # Convertir de BGR a RGB
            color_bgr = self.imagen_original[y, x]
            return np.array(list(reversed(color_bgr)))
        except Exception as e:
            print(f"Error al obtener color del pixel: {e}")
            return np.array([0, 0, 0])  # Negro por defecto

    def mostrar_imagen(self):
        """Función legacy - se recomienda usar dibujar_imagen()"""
        print("Función obsoleta. Use dibujar_imagen() para funcionalidad completa.")
        if self.seleccionada:
            return self.dibujar_imagen()
        else:
            print("No hay ninguna imagen seleccionada.")
            return False

    def dibujar_imagen_con_thread(self, 
                                mostrar_original: bool = False,
                                puntos_adicionales: Optional[List[Punto]] = None,
                                porcentaje_pantalla: float = 0.8,
                                titulo_ventana: str = "Imagen",
                                guardar_automaticamente: bool = False,
                                incluir_etiquetas: bool = False,
                                timeout_segundos: int = 0,
                                auto_cerrar_segundos: int = 0
                                ) -> bool:
        """
        Versión alternativa que usa threading para garantizar que siempre se puede cerrar.
        
        Esta función crea un hilo separado que monitorea la ventana y fuerza el cierre
        si es necesario, evitando que el programa se quede colgado.
        """
        
        # Configurar OpenCV para el sistema actual
        configurar_opencv_multiplataforma()
        
        # Validaciones (mismas que antes)
        if not self.seleccionada or self.imagen_original is None:
            print("Error: No hay ninguna imagen cargada. Use seleccionar_imagen() primero.")
            return False
            
        if not 0.1 <= porcentaje_pantalla <= 1.0:
            print("Error: porcentaje_pantalla debe estar entre 0.1 y 1.0")
            return False
        
        if mostrar_original and puntos_adicionales:
            print("Advertencia: Se especificaron puntos_adicionales con mostrar_original=True.")
            puntos_adicionales = None
        
        # Flag compartido para controlar el cierre
        debe_cerrar = threading.Event()
        ventana_mostrada = threading.Event()
        
        def monitor_ventana():
            """Hilo que monitorea la ventana y fuerza el cierre si es necesario"""
            # Esperar a que la ventana se muestre
            ventana_mostrada.wait(timeout=5)
            
            tiempo_inicio = time.time()
            
            while not debe_cerrar.is_set():
                try:
                    # Verificar si la ventana existe
                    prop = cv.getWindowProperty(titulo_ventana, cv.WND_PROP_VISIBLE)
                    if prop <= 0:
                        print("🔍 Ventana cerrada detectada por monitor")
                        debe_cerrar.set()
                        break
                except:
                    print("🔍 Ventana cerrada detectada por excepción en monitor")
                    debe_cerrar.set()
                    break
                
                # Auto-cerrar después del tiempo especificado
                if auto_cerrar_segundos > 0:
                    tiempo_transcurrido = time.time() - tiempo_inicio
                    if tiempo_transcurrido >= auto_cerrar_segundos:
                        print(f"⏰ Auto-cerrando después de {auto_cerrar_segundos} segundos")
                        debe_cerrar.set()
                        break
                
                time.sleep(0.1)  # Verificar cada 100ms
        
        try:
            # Preparar imagen (mismo código que antes)
            self.factor_escala = self._calcular_factor_escala(porcentaje_pantalla)
            nuevo_ancho = int(self.ancho * self.factor_escala)
            nuevo_alto = int(self.alto * self.factor_escala)
            
            print(f"Factor de escala aplicado: {self.factor_escala:.3f}")
            print(f"Dimensiones originales: {self.ancho}x{self.alto}")
            print(f"Dimensiones escaladas: {nuevo_ancho}x{nuevo_alto}")
            
            # Preparar imagen
            if mostrar_original:
                imagen_base = self.imagen_original.copy()
            else:
                imagen_base = self.imagen_original.copy()
                
                # Dibujar puntos permanentes
                for punto in self.puntos_seleccionados:
                    self._dibujar_punto_original(imagen_base, punto, incluir_etiquetas)
                
                # Dibujar puntos adicionales
                if puntos_adicionales:
                    for punto in puntos_adicionales:
                        self._dibujar_punto_original(imagen_base, punto, incluir_etiquetas)
            
            # Redimensionar
            if self.factor_escala != 1.0:
                imagen_a_mostrar = cv.resize(
                    imagen_base, 
                    (nuevo_ancho, nuevo_alto), 
                    interpolation=cv.INTER_AREA
                )
            else:
                imagen_a_mostrar = imagen_base
            
            # Crear ventana
            cv.namedWindow(titulo_ventana, cv.WINDOW_NORMAL | cv.WINDOW_KEEPRATIO)
            try:
                cv.resizeWindow(titulo_ventana, nuevo_ancho, nuevo_alto)
            except:
                pass
            
            # Mostrar imagen
            cv.imshow(titulo_ventana, imagen_a_mostrar)
            ventana_mostrada.set()  # Señalar que la ventana ya se mostró
            
            # Iniciar hilo monitor
            monitor_thread = threading.Thread(target=monitor_ventana, daemon=True)
            monitor_thread.start()
            
            # Información en consola
            tipo_vista = "original" if mostrar_original else "con modificaciones"
            num_puntos = len(self.puntos_seleccionados)
            num_adicionales = len(puntos_adicionales) if puntos_adicionales else 0
            
            print(f"📷 Mostrando imagen {tipo_vista}")
            print(f"📍 Puntos permanentes: {num_puntos}")
            if num_adicionales > 0:
                print(f"📍 Puntos temporales: {num_adicionales}")
            
            print("🎹 Presione cualquier tecla para cerrar")
            print("❌ O cierre con la X de la ventana")
            if auto_cerrar_segundos > 0:
                print(f"⏱️  Auto-cierre en {auto_cerrar_segundos} segundos")
            
            # Loop principal con múltiples métodos de salida
            tiempo_inicio = time.time()
            
            while not debe_cerrar.is_set():
                # Método 1: Detectar tecla presionada
                tecla = cv.waitKey(30) & 0xFF
                if tecla != 255:
                    if tecla == 27:  # ESC
                        print("⌨️  Cerrado con ESC")
                    elif tecla == 32:  # ESPACIO
                        print("⌨️  Cerrado con ESPACIO")
                    else:
                        print(f"⌨️  Cerrado con tecla: {chr(tecla) if 32 <= tecla <= 126 else f'código {tecla}'}")
                    break
                    
                # Método 2: Verificar timeout manual
                if timeout_segundos > 0:
                    tiempo_transcurrido = time.time() - tiempo_inicio
                    if tiempo_transcurrido >= timeout_segundos:
                        print(f"⏰ Timeout alcanzado ({timeout_segundos} segundos)")
                        break
                
                # Método 3: Verificar flag del monitor
                if debe_cerrar.is_set():
                    break
            
            # Señalar cierre y esperar un momento para que el hilo termine
            debe_cerrar.set()
            time.sleep(0.1)
            
            # Limpiar ventanas
            try:
                cv.destroyWindow(titulo_ventana)
                cv.destroyAllWindows()
            except:
                pass
            
            # Guardado automático
            if guardar_automaticamente:
                self.guardar_imagen(imagen_a_mostrar, f"{titulo_ventana}_{tipo_vista}")
            
            print("✅ Imagen cerrada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al mostrar la imagen: {e}")
            debe_cerrar.set()
            try:
                cv.destroyAllWindows()
            except:
                pass
            return False

# ═══════════════════════════════════════════════════════════════════════════════════
# EJEMPLOS DE USO
# ═══════════════════════════════════════════════════════════════════════════════════

def ejemplo_uso_basico():
    """Ejemplo básico de uso de la clase Imagen refactorizada."""
    print("=== Ejemplo de uso básico ===")
    
    # Crear instancia y cargar imagen
    img = Imagen()
    
    if img.seleccionar_imagen():
        # Mostrar imagen original
        print("1. Mostrando imagen original...")
        img.dibujar_imagen(mostrar_original=True)
        
        # Agregar algunos puntos
        img.agregar_punto((100, 100), color=(255, 0, 0), etiqueta="Punto 1")
        img.agregar_punto((200, 150), color=(0, 255, 0), etiqueta="Punto 2")
        
        # Mostrar imagen con puntos
        print("2. Mostrando imagen con puntos...")
        img.dibujar_imagen(mostrar_original=False)
        
        # Guardar imagen modificada
        img.guardar_imagen()


def ejemplo_uso_avanzado():
    """Ejemplo avanzado con puntos temporales y opciones."""
    print("=== Ejemplo de uso avanzado ===")
    
    img = Imagen()
    
    if img.seleccionar_imagen():
        # Puntos permanentes
        img.agregar_punto((50, 50), color=(255, 0, 0), etiqueta="Permanente")
        
        # Puntos temporales para esta visualización
        puntos_temp = [
            Punto((150, 150), color=(0, 0, 255), etiqueta="Temporal 1"),
            Punto((250, 200), color=(255, 255, 0), etiqueta="Temporal 2")
        ]
        
        # Mostrar con diferentes configuraciones
        print("1. Con 50% de pantalla...")
        img.dibujar_imagen(
            mostrar_original=False,
            puntos_adicionales=puntos_temp,
            porcentaje_pantalla=0.5,
            titulo_ventana="Vista 50%"
        )
        
        print("2. Con 90% de pantalla y guardado automático...")
        img.dibujar_imagen(
            mostrar_original=False,
            porcentaje_pantalla=0.9,
            titulo_ventana="Vista completa",
            guardar_automaticamente=True
        )


if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_uso_basico()
    # ejemplo_uso_avanzado()  # Descomenta para probar ejemplo avanzado