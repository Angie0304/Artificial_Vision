from typing import List, Tuple, Union, Optional
import numpy as np


class Punto:
    """Representación unificada de un punto en el espacio."""
    
    def __init__(self, 
                 coordenadas: Union[List[float], Tuple[float, ...], np.ndarray], 
                 color: Optional[Tuple[int, int, int]] = None,
                 etiqueta: Optional[str] = None):
        """
        Inicializa un punto con coordenadas y metadatos opcionales.
        
        Args:
            coordenadas: Las coordenadas del punto (x, y) o (x, y, z)
            color: Color RGB opcional para visualización
            etiqueta: Etiqueta opcional para identificar el punto
        """
        if isinstance(coordenadas, np.ndarray):
            self.coordenadas = coordenadas.astype(float)
        else:
            self.coordenadas = np.array(coordenadas, dtype=float)
        self.color = color
        self.etiqueta = etiqueta
    
    @property
    def dimension(self) -> int:
        """Retorna la dimensionalidad del punto."""
        return len(self.coordenadas)
    
    @property
    def x(self) -> float:
        """Retorna la coordenada x."""
        return self.coordenadas[0]
    
    @property
    def y(self) -> float:
        """Retorna la coordenada y."""
        return self.coordenadas[1]
    
    @property
    def z(self) -> Optional[float]:
        """Retorna la coordenada z si existe."""
        if self.dimension > 2:
            return self.coordenadas[2]
        return None
    
    def distancia_a(self, otro_punto: 'Punto') -> float:
        """Calcula la distancia euclidiana a otro punto."""
        return np.linalg.norm(self.coordenadas - otro_punto.coordenadas)
    
    def __repr__(self) -> str:
        """Representación en string del punto."""
        coord_str = ", ".join(f"{c:.2f}" for c in self.coordenadas)
        return f"Punto({coord_str})"
    
    def __eq__(self, other):
        """Igualdad basada en coordenadas"""
        if not isinstance(other, Punto):
            return False
        return np.allclose(self.coordenadas, other.coordenadas)
    
    def __hash__(self):
        """Hash para usar como clave en diccionarios"""
        return hash(tuple(self.coordenadas.round(decimals=10)))

class PuntoImagen(Punto):
    """Extensión de Punto para incluir metadatos de imagen."""
    
    def __init__(self, 
                 coordenadas: Union[List[float], Tuple[float, ...], np.ndarray], 
                 color_RGB: Union[List[float], Tuple[float, ...], np.ndarray], 
                 color_visualizacion: Optional[Tuple[int, int, int]] = None,
                 etiqueta: Optional[str] = None):
        """
        Inicializa un punto con coordenadas y metadatos de imagen.
        
        Args:
            coordenadas: Las coordenadas del punto (x, y) o (x, y, z)
            color_visualizacion: Color RGB opcional para visualización
            etiqueta: Etiqueta opcional para identificar el punto
            color_RGB: Identificador de la imagen asociada
        """
        # Validación para las coordenadas 2D y color 3D
        if len(coordenadas) != 2 or len(color_RGB) != 3:
            raise ValueError("Las coordenadas deben ser 2D y el color_RGB debe ser 3D.")
        
        super().__init__(coordenadas, color_visualizacion, etiqueta)
        if isinstance(color_RGB, np.ndarray):
            self.color_RGB = color_RGB.astype(float)
        else:
            self.color_RGB = np.array(color_RGB, dtype=float)