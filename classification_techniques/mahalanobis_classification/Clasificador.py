import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import mahalanobis


#----- Funciones para distancia mahalanobis -----


# Varianza
def calcular_varianza(datos):
    media = np.mean(datos)
    varianza = np.sum((datos - media) ** 2) / (len(datos) - 1)  # Normalizamos por n-1
    return varianza

# Matriz de covarianza
def calcular_covarianza(datos):
    # Datos: matriz de dimensiones (n_variables, n_muestras)
    n_muestras = datos.shape[1]  # Número de muestras
    media = np.mean(datos, axis=1).reshape(-1, 1)  # Media de cada variable
    cov_matrix = np.zeros((datos.shape[0], datos.shape[0])) 

    for i in range(n_muestras):
        # Restamos la media de cada muestra
        diff = datos[:, i] - media[:, 0]
        cov_matrix += np.outer(diff, diff)  # Producto externo de la diferencia
    
    cov_matrix /= (n_muestras - 1)  # Normalizamos entre n-1
    return cov_matrix

# Inversa de la matriz de covarianza
def calcular_inversa(cov_matrix):
    # Determinante
    det = np.linalg.det(cov_matrix)
    if det == 0:
        raise ValueError("La matriz de covarianza no es invertible.")
    
    # Matriz adjunta (matriz de cofactores)
    adjunta = np.zeros_like(cov_matrix)
    n = cov_matrix.shape[0]
    
    for i in range(n):
        for j in range(n):
            # Submatriz que excluye la fila i y columna j
            submatriz = np.delete(np.delete(cov_matrix, i, axis=0), j, axis=1)
            adjunta[i, j] = ((-1) ** (i + j)) * np.linalg.det(submatriz)
    
    # Transponemos la matriz de cofactores para obtener la adjunta
    adjunta = adjunta.T
    
    # Inversa
    inversa = adjunta / det
    return inversa


# ----- Funciones de distancias -----


# Distancia euclidiana 
def calcular_distancia_euclidiana(punto, centroides):
    return [np.linalg.norm(punto - centroide) for centroide in centroides]

# Distancia mahalanobis
def calcular_distancia_mahalanobis(punto, centroide, cov_inv):
    diff = punto - centroide  # Diferencia entre el punto y el centroide
    dist = np.sqrt(np.dot(np.dot(diff.T, cov_inv), diff))  
    return dist



# ----- Clasificar punto -----


def clasificar_punto(dim, centroides, clases, num_clases):
    puntoNuevo = np.array(list(map(float, input(f"Ingrese las coordenadas del punto a clasificar ({'x y' if dim == 2 else 'x y z'}): ").split())))
    
    print('\nCentroides')
    for i, centroide in enumerate(centroides):
        print(f"Centroide de la clase {i+1}: {centroide}")
    
    print("\n¿Qué método deseas usar?")
    print("1. Distancia Euclidiana")
    print("2. Distancia Mahalanobis")
    print("3. Salir")
    
    opcion = input("Ingrese su opción (1, 2 o 3): ")
    
    if opcion == '1':
        distancias = calcular_distancia_euclidiana(puntoNuevo, centroides)
    elif opcion == '2':
        # Calcular la matriz de covarianza y su inversa
        datos_clases = [np.array(clase) for clase in clases]  # Convierto las clases en matrices
        cov_matrices = [calcular_covarianza(datos) for datos in datos_clases]  # Lista de matrices de covarianza
        cov_inversas = [calcular_inversa(cov_matrix) for cov_matrix in cov_matrices]  # Inversas de las matrices de covarianza
        
        # Calcular la distancia de Mahalanobis
        distancias = [calcular_distancia_mahalanobis(puntoNuevo, centroide, cov_inv) for centroide, cov_inv in zip(centroides, cov_inversas)]
    
    
    # Calcular distancias Mahalanobis
        datos_clases = [np.array(clase) for clase in clases]
        cov_matrices = [calcular_covarianza(datos) for datos in datos_clases]
        cov_inversas = [calcular_inversa(cov_matrix) for cov_matrix in cov_matrices]
        distancias = [calcular_distancia_mahalanobis(puntoNuevo, centroide, cov_inv) for centroide, cov_inv in zip(centroides, cov_inversas)]
        for i, distancia in enumerate(distancias):
            print(f"Distancia Mahalanobis a la clase {i+1}: {distancia:.2f}")
        # Seleccionar la clase con la menor distancia
        claseAsignada = np.argmin(distancias) + 1
    
    
    
    elif opcion == '3':
        print("Saliendo...")
        return False
    else:
        print("Opción no válida")
        return True
    
    claseAsignada = np.argmin(distancias) + 1
    print(f"El punto pertenece a la clase {claseAsignada}")
    graficar_datos(dim, clases, centroides, puntoNuevo, num_clases)
    return True


#----- Gráficas 2D y 3D -----


def graficar_datos(dim, clases, centroides, puntoNuevo, num_clases):
    colores = ['blue', 'magenta', 'green', 'purple', 'orange', 'cyan', 'brown', 'pink']
    marcadores = ['x', 'o', '^', 's', 'D', 'v', '<', '>']
    
    if dim == 2:
        plt.figure(figsize=(8, 6))
        for i in range(num_clases):
            plt.scatter(clases[i][0], clases[i][1], color=colores[i % len(colores)], alpha=0.5, label=f'Clase {i+1}')
            plt.scatter(centroides[i][0], centroides[i][1], color='red', marker=marcadores[i % len(marcadores)], s=100, label=f'Centroide {i+1}')
        plt.scatter(puntoNuevo[0], puntoNuevo[1], color='yellow', edgecolors='black', s=100, label='Punto Nuevo')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.grid(True)
        plt.title('Clasificación en 2D')
        plt.savefig("resultado.png", dpi=300)
        plt.show()
    else:
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        for i in range(num_clases):
            ax.scatter(clases[i][0], clases[i][1], clases[i][2], color=colores[i % len(colores)], alpha=0.5, label=f'Clase {i+1}')
            ax.scatter(centroides[i][0], centroides[i][1], centroides[i][2], color='red', marker=marcadores[i % len(marcadores)], s=100, label=f'Centroide {i+1}')
        ax.scatter(puntoNuevo[0], puntoNuevo[1], puntoNuevo[2], color='yellow', edgecolors='black', s=100, label='Punto Nuevo')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        ax.set_title('Clasificación en 3D')
        plt.show()

# Dimensiones
def obtener_dimensiones():
    dim = int(input("Ingrese el número de dimensiones (2 o 3): "))
    if dim not in [2, 3]:
        print("Dimensión no válida. Solo se permiten 2 o 3 dimensiones.")
        exit()
    return dim


#----- Genenar clases -----


def obtener_clases(dim):
    num_clases = int(input("Ingrese el número de clases a generar: "))
    centroides = []
    dispersiones = []
    
    for i in range(num_clases):
        if dim == 2:
            x, y = map(float, input(f"Ingrese las coordenadas del centroide de la clase {i+1} (x y): ").split())
            dx = float(input(f"Ingrese la dispersión en X para la clase {i+1}: "))
            dy = float(input(f"Ingrese la dispersión en Y para la clase {i+1}: "))
            centroides.append([x, y])
            dispersiones.append([dx, dy])
        else:
            x, y, z = map(float, input(f"Ingrese las coordenadas del centroide de la clase {i+1} (x y z): ").split())
            dx = float(input(f"Ingrese la dispersión en X para la clase {i+1}: "))
            dy = float(input(f"Ingrese la dispersión en Y para la clase {i+1}: "))
            dz = float(input(f"Ingrese la dispersión en Z para la clase {i+1}: "))
            centroides.append([x, y, z])
            dispersiones.append([dx, dy, dz])
    
    return num_clases, centroides, dispersiones


#----- Generar datos de clases -----


def generar_datos(dim, num_clases, centroides, dispersiones, num_elementos):
    clases = []
    for i in range(num_clases):
        if dim == 2:
            cx, cy = centroides[i]
            dx, dy = dispersiones[i]
            datos = np.array([np.random.randn(num_elementos) * dx + cx, np.random.randn(num_elementos) * dy + cy])
        else:
            cx, cy, cz = centroides[i]
            dx, dy, dz = dispersiones[i]
            datos = np.array([np.random.randn(num_elementos) * dx + cx, np.random.randn(num_elementos) * dy + cy, np.random.randn(num_elementos) * dz + cz])
        clases.append(datos)
    return clases


#----- Main -----


def main():
    dim = obtener_dimensiones()
    num_clases, centroides, dispersiones = obtener_clases(dim)
    num_elementos = int(input("Ingrese el número de elementos por clase: "))
    
    clases = generar_datos(dim, num_clases, centroides, dispersiones, num_elementos)
    continuar = True
    
    while continuar:
        continuar = clasificar_punto(dim, centroides, clases, num_clases)

# Llamamos a main 
main()


