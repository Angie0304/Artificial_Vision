from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from utils.funciones_estandar_V2 import input_validado, try_except, eleccion

class Opcion(ABC):
    """Controla las opciones que puede ejecutar un menú."""
    def __init__(self, nombre: str = 'Sin nombre', descripcion: str = "") -> None:
        """
        Inicializa una opción de menú.
        
        Args:
            nombre: Texto que identifica la opción
            descripcion: Descripción de la funcionalidad (opcional)
        """
        self._nombre = nombre
        self._descripcion = descripcion

    def nombre(self) -> str:
        """Retorna el nombre de la opción."""
        return self._nombre
    
    def descripcion(self) -> str:
        """Retorna la descripción de la opción."""
        return self._descripcion
    
    @abstractmethod
    def ejecutar(self) -> None:
        """Ejecuta la acción asociada a la opción."""
        pass

class Menu:
    """Gestiona las diferentes opciones a las que puede acceder el usuario."""
    def __init__(self, 
                 opciones: List[Opcion], 
                 titulo: str = "Menu", 
                 texto_eleccion: str = 'Elige una opción',
                 opcion_salir: bool = True,
                 confirmacion_salir: bool = False
                 ):
        """
        Inicializa un menú.
        
        Args:
            opciones: Lista de opciones disponibles
            titulo: Título del menú
            texto_eleccion: Mensaje para solicitar la elección
            opcion_salir: Si es True, incluye opción para salir
            confirmacion_salir: Si es True, pide confirmación al salir
        """
        self._opciones = opciones
        self.titulo = titulo
        self.seleccionado = 0
        self._opcion_salir = opcion_salir
        self._texto_eleccion = texto_eleccion
        self._confirmacion_salir = confirmacion_salir
    
    @try_except
    def _mostrar_opciones(self) -> None:
        """Muestra las opciones disponibles en un formato de lista."""
        # Imprime el título
        print(f"\n*----------< {self.titulo.upper()} >----------*")
        
        # Imprime las opciones con sus descripciones
        for i, opcion in enumerate(self._opciones):
            nombre = opcion.nombre()
            descripcion = opcion.descripcion()
            
            if descripcion:
                print(f'{i+1}. {nombre} - {descripcion}')
            else:
                print(f'{i+1}. {nombre}')
        
        if self._opcion_salir:
            print('0. Salir')
    
    @try_except
    def _obtener_rango(self) -> Tuple[int, int]:
        """Obtiene el rango de valores que puede ingresar el usuario."""
        lim_inf = 0 if self._opcion_salir else 1
        lim_sup = len(self._opciones)
        return (lim_inf, lim_sup)
    
    @try_except
    def _seleccionar_opcion(self) -> int:
        """Permite al usuario seleccionar la opción deseada."""
        rango = self._obtener_rango()
        _, seleccion = input_validado(self._texto_eleccion, 'rango_entero', rango)
        return seleccion
    
    @try_except
    def _ejecutar_opcion(self, seleccion: int) -> None:
        """Ejecuta la opción seleccionada."""
        if seleccion > 0:  # Si no es la opción de salir
            self._opciones[seleccion - 1].ejecutar()
    
    @try_except
    def iniciar(self) -> None:
        """Ejecuta el menú."""
        while True:
            self._mostrar_opciones()
            seleccion = self._seleccionar_opcion()
            
            if seleccion == 0 and self._opcion_salir:  # Solo salir si seleccionó 0 y opcion_salir es True
                if self._confirmacion_salir:
                    if eleccion("¿Estás seguro que deseas salir?"):
                        break
                else:
                    break
            elif seleccion > 0:  # Ejecutar la opción si no es 0
                self._ejecutar_opcion(seleccion)
                if not self._opcion_salir:  # Si no hay opción de salir, salir después de ejecutar
                    break

class OpcionSubmenu(Opcion):
    """Opción que abre un submenú."""
    def __init__(self, nombre: str, menu: Menu, descripcion: str = ""):
        """
        Inicializa una opción que ejecuta un submenú.
        
        Args:
            nombre: Texto que identifica la opción
            menu: Menú a ejecutar
            descripcion: Descripción de la funcionalidad (opcional)
        """
        super().__init__(nombre, descripcion)
        self._menu = menu
    
    def ejecutar(self) -> None:
        """Ejecuta el menú secundario."""
        self._menu.iniciar()