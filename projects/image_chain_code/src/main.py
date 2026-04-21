from modules.punto import PuntoImagen as Punto
from ui.menu import Menu, Opcion
from utils.funciones_estandar_V2 import input_validado, eleccion
from typing import List, Dict, Tuple
from modules.imagen import Imagen
from modules.algoritmo_cadena import AlgoritmoCadena, Resultados

class SeleccionarImagen(Opcion):
    """Opción para seleccionar una imagen."""
    
    def __init__(self, imagen: Imagen):
        super().__init__('Seleccionar imagen', 'Selecciona una imagen para procesar.')
        self.imagen = imagen

    def ejecutar(self):
        # Lógica para seleccionar una imagen
        print("Selecciona una imagen.")
        if self.imagen.seleccionar_imagen():
            print("Imagen seleccionada correctamente.")
        else:
            print("No se pudo seleccionar la imagen.")
        


class EjecutarAlgoritmoCadena(Opcion):
    """Opción para ejecutar el algoritmo de cadena."""
    
    def __init__(self, imagen: Imagen, resultados: Resultados):
        super().__init__('Ejecutar algoritmo de cadena', 'Ejecuta el algoritmo de cadena en la imagen seleccionada.')
        self.imagen = imagen
        self.resultados = resultados
        self.algoritmo = AlgoritmoCadena(self.imagen, self.resultados)

    def ejecutar(self) -> None:
            """Ejecuta el algoritmo con parámetros solicitados al usuario."""
            if not self.imagen.seleccionada:
                print("Primero debes seleccionar una imagen.")
                return
            
            # Solicitar parámetros al usuario
            from utils.funciones_estandar_V2 import input_validado, eleccion
            
            print("Configuración del algoritmo de cadena:")
            
            # Número de puntos
            num_puntos = input_validado(
                "Número de puntos aleatorios a generar (recomendado: 20-100)", 
                'entero'
            )
            
            """ # Rango de grupos
            min_grupos = input_validado(
                "Número mínimo de grupos deseados", 
                'entero'
            )
            max_grupos = input_validado(
                "Número máximo de grupos deseados", 
                'entero'
            )
            
            if min_grupos > max_grupos:
                min_grupos, max_grupos = max_grupos, min_grupos
                print(f"Rango corregido: {min_grupos} - {max_grupos} grupos") """
            min_grupos = 3
            max_grupos = 5

            """ # Métrica de distancia
            usar_manhattan = eleccion(
                "¿Usar distancia Manhattan en lugar de Euclidiana?", 
                por_defecto=False
            )
            metrica = 'manhattan' if usar_manhattan else 'euclidean' """
            
            metrica = 'euclidean'  # Solo se usa la métrica euclidiana
            
            print(f"\nEjecutando algoritmo...")
            print(f"- Puntos: {num_puntos}")
            print(f"- Grupos buscados: {min_grupos} - {max_grupos}")
            print(f"- Métrica: {metrica}")
            print("-" * 50)
            
            # Ejecutar algoritmo
            self.algoritmo.ejecutar(
                num_puntos=num_puntos,
                grupos_buscados=(min_grupos, max_grupos),
                metrica_distancia=metrica
            )
            
            print("-" * 50)
            print("Algoritmo completado. Use 'Mostrar resultados' para ver los grupos.")



class MostrarResultados(Opcion):
    """Opción para mostrar los resultados del algoritmo."""
    
    def __init__(self, resultados: Resultados):
        super().__init__('Mostrar resultados', 'Muestra los resultados del algoritmo de cadena.')
        self.resultados = resultados

    def _elegir_grupo(self):
        """Permite al usuario elegir el número de grupos a mostrar."""
        while True:
            diccionario = self.resultados.obtener_resultados()
            for i, (grupo, umbral_imagen) in enumerate(diccionario.items()):
                print(f"{i+1}. Grupo: {grupo}")

            grupos_elegidos = input_validado(
                "Introduce el número de grupos a mostrar",
                'entero'
            )

            grupos = list(diccionario.keys())
            if grupos_elegidos in grupos:
                return grupos_elegidos
            else:
                print(f"El grupo {grupos_elegidos} no existe. Por favor, elige un grupo válido.")
    
    @staticmethod
    def _grupos_puntos(puntos: List[Punto]):
        colores = [Punto.color_RGB for Punto in puntos]
        grupos = set(colores)
        cantidad_puntos = {}
        for color_unico in grupos:
            cantidad = 0
            for color in colores:
                if color == color_unico:
                    cantidad += 1
                cantidad_puntos[color_unico] = cantidad
        return cantidad_puntos
            
        

    def _mostrar_resultados(self, grupo_elegido: int, resultados: Dict[int, Tuple[int, Imagen]]):
            print(f'\n', '='*50)
            print(f'Grupos: {grupo_elegido}')
            #print(f'Umbral: {resultados[grupo_elegido][0]}')
            imagen = resultados[grupo_elegido][1]
            imagen.dibujar_imagen(porcentaje_pantalla=1)
            puntos_por_grupo = self.resultados.obtener_todas_las_estadisticas_por_grupos()
            # Imprimimos los puntos por grupo
            diccionario = puntos_por_grupo[grupo_elegido]
            for color, cantidad in diccionario.items():
                print(f"Color: {color}, Cantidad de puntos: {cantidad}")
            print('='*50)
    
    def ejecutar(self):
        # Lógica para mostrar los resultados
        if not self.resultados.tiene_resultados():
            print("No hay resultados para mostrar. Ejecuta el algoritmo primero.")
            return

        resultados: Dict[int, Tuple[int, Imagen]] = self.resultados.obtener_resultados()

        if self.resultados.tiene_un_resultado():
            grupo_elegido = list(resultados.keys())[0]

            self._mostrar_resultados(grupo_elegido, resultados)
            return
        else:
            print("Hay múltiples grupos disponibles. Por favor, elige uno para mostrar sus resultados.")
    
            while True:
                grupo_elegido = self._elegir_grupo()

                self._mostrar_resultados(grupo_elegido, resultados)
                if not eleccion('¿Deseas ver otro grupo?', por_defecto=False):
                    break
            print("Resultados mostrados. Regresando al menú principal.\n")	


def crear_menu():
    """
    Crea el menú con el que accesará el usuario a las funcionalidades del programa.
    
    Las opciones del menú son:
    * Seleccionar imagen
    * Ejecutar algoritmo de cadena (no se ejecuta hasta que el usuario seleccione una imagen)
    * Mostrar resultados (no se ejecuta hasta que el usuario ejecute el algoritmo)
    """
    imagen = Imagen() 
    resultados = Resultados() 
    lista_opciones = [
        SeleccionarImagen(imagen),
        EjecutarAlgoritmoCadena(imagen, resultados),
        MostrarResultados(resultados)
    ]
    menu = Menu(
        titulo='Menú Principal',
        opciones=lista_opciones,
        opcion_salir=True,
        confirmacion_salir=True,
        texto_eleccion='Seleccione una opción: '
    )
    return menu


if __name__ == '__main__':
    menu = crear_menu()
    menu.iniciar()

