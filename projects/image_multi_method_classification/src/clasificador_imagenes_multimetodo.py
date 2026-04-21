from tkinter import Tk, filedialog
import numpy as np
import random
import matplotlib.pyplot as plt
import cv2

punto_seleccionado = None

# ---------- Selección de imagen ----------
def seleccionar_imagen():
    root = Tk() 
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True) #
    image_path = filedialog.askopenfilename() #Cuadro para seleccionar archivo, se guarda en image_path
    root.destroy()

    if not image_path: #Si image_path está vacía 
        print("No se seleccionó ninguna imagen.")
        return None

    imagen = cv2.imread(image_path) #Si no se pudo cargar la imagen en image_path
    if imagen is None:
        print("No se pudo cargar la imagen.")
    return imagen #Si si se cargó la imagen correctamente, devuelve la imagen 


# ---------- Selección de rangos ----------
def seleccionar_rango_imagen(imagen):
    cv2.namedWindow("Selecciona un rango", cv2.WINDOW_NORMAL) #Creamos ventana con capacidad para redimensionarla
    cv2.imshow("Selecciona un rango", imagen) # Mostramos imagen en la ventana de la linea anterior 
    cv2.waitKey(100)

    roi = cv2.selectROI("Selecciona un rango", imagen, showCrosshair=True, fromCenter=False) #Usuario puede seleccionar una region rectangular en img                                                                             
    cv2.destroyAllWindows() #Cerramos la ventana de selección de la región 

    x1, y1, w, h = roi # Coordenadas del punto superior de la region seleccionada. Alto y ancho de la region seleccionada 
   
    if w == 0 or h == 0: #Si no hay ancho ni alto 
        print("❌ Selección vacía.")
        return None
    return (x1, y1, x1 + w, y1 + h) #Si la selección es correcta devuelve coordenadas de borde inf. derecho


# ---------- Selección de clases ----------
def seleccionar_clases(imagen, num_clases, representantes_por_clase):
    clases = []
    nombres = []

    for i in range(num_clases): #Permite que usuario seleccione rengos de las clases n veces (no. clases)
        print(f"\nSelecciona el rango para la clase {i + 1}")
        rango = seleccionar_rango_imagen(imagen)
        if rango is None:
            return None, None

        representantes = [] #Almacenar los pixeles seleccionados como representantes
        for _ in range(representantes_por_clase):
            x = random.randint(rango[0], rango[2] - 1)
            y = random.randint(rango[1], rango[3] - 1)
            pixel_rgb = imagen[y, x]
            representantes.append((x, y, pixel_rgb))


        clases.append(representantes) #Añade la lista de representantes de la clase a la lista clases
        nombre = input(f"Nombre para la clase {i + 1}: ")
        nombres.append(nombre)

    return clases, nombres #Devuelve la lista de clases y la lista de nombres 

# ---------- Cálculo de centroides ----------
def calcular_centroides(clases):
    centroides = []
    for i, clase in enumerate(clases):
        valores_rgb = [pixel[2] for pixel in clase]  # extrae solo los RGB
        centroide = np.mean(valores_rgb, axis=0)
        centroide = np.round(centroide).astype(int)
        centroides.append(centroide)
        print(f"Centroide clase {i + 1}: {centroide}")
    return centroides


# ---------- Clasificación ----------
def calcular_distancia_euclidiana(punto, centroides):
    distancias = [np.linalg.norm(punto - np.array(centroide)) for centroide in centroides]
    return np.min(distancias), np.argmin(distancias), distancias

def calcular_distancia_mahalanobis(punto, centroide, clase):
    centroide = np.array(centroide)
    dif = clase - centroide[:, np.newaxis] 
    cov_matrix = (1/4) * np.dot(dif, dif.T)
    inv_cov_matrix = np.linalg.inv(cov_matrix)
    dif_punto = punto - centroide
    return np.sqrt(np.dot(np.dot(dif_punto.T, inv_cov_matrix), dif_punto))

def maxima_probabilidad(x, mat, dim):
    media = np.mean(mat, axis=1, keepdims=True)
    c = mat - media
    covMat = np.cov(mat, bias=True)
    covMat += np.eye(dim) * 1e-6
    covInvMat = np.linalg.inv(covMat)
    d = x.reshape(dim, 1) - media
    e = np.dot(np.dot(d.T, covInvMat), d)
    prob = (2 * np.pi) ** (-dim / 2) * (np.linalg.det(covMat) ** -0.5) * np.exp(-0.5 * e)
    return prob.squeeze()


# ---------- Selección de punto ----------
def seleccionar_punto(event, x, y, flags, param):
    global punto_seleccionado
    if event == cv2.EVENT_LBUTTONDOWN:
        punto_seleccionado = (x, y)
        print(f"Punto seleccionado: ({x}, {y})")
        cv2.destroyWindow("Imagen para clasificación")  # Cierra solo esa ventana, no todas




def graficar_en_imagen(clases, punto_rgb, nombres_clases, imagen):
    imagen_con_puntos = imagen.copy()

    for i, clase in enumerate(clases):
        # Dibuja los puntos de cada clase
        for x, y, _ in clase:
            cv2.circle(imagen_con_puntos, (x, y), 5, (238, 107, 243), -1)  # Puntos de la clase en verde

        # Extraer las coordenadas de los puntos representativos de cada clase (usamos el primer punto)
        x, y, _ = clase[0]  # Tomamos el primer punto de la clase como referencia

        # Calcular una posición para el nombre de la clase fuera de la región de puntos
        nombre_x = x + 15  # Colocamos el nombre a la derecha de la región
        nombre_y = y - 10  # O un poco por encima de la región

        # Mostrar el nombre de la clase al lado de su región
        cv2.putText(imagen_con_puntos, nombres_clases[i], (nombre_x, nombre_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

    # Dibuja el punto clasificado en rojo
    x, y = punto_seleccionado
    cv2.circle(imagen_con_puntos, (x, y), 10, (0, 0, 255), -1)  # Punto clasificado en rojo

    # Mostrar la imagen con los puntos clasificados y los nombres de las clases
    cv2.imshow("Clasificación de puntos", imagen_con_puntos)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




# ---------- Programa principal ----------
def ejecutar_programa():
    global punto_seleccionado

    print("Selecciona una imagen...")
    imagen = seleccionar_imagen()
    if imagen is None:
        return

    num_clases = int(input("Número de clases: "))
    representantes_por_clase = int(input("Número de representantes por clase: "))
    clases, nombres = seleccionar_clases(imagen, num_clases, representantes_por_clase)
    if clases is None:
        return

    centroides = calcular_centroides(clases)

    while True:
        punto_seleccionado = None
        ventana = "Imagen para clasificación"
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
        cv2.imshow(ventana, imagen)
        cv2.setMouseCallback(ventana, seleccionar_punto)
        print("\nHaz clic en un punto de la imagen para clasificarlo...")

        while punto_seleccionado is None:
            if cv2.getWindowProperty(ventana, cv2.WND_PROP_VISIBLE) < 1:
                print("❌ Cerraste la ventana. Intenta de nuevo.")
                return
            cv2.waitKey(1)


        x, y = punto_seleccionado
        pixel_rgb = imagen[y, x]
        print(f"Punto seleccionado: ({x}, {y})")
        print(f"Valor RGB del punto: R={pixel_rgb[2]}, G={pixel_rgb[1]}, B={pixel_rgb[0]}")

        print("\nMétodos de clasificación:") #Menú 
        print("1. Distancia Euclidiana")
        print("2. Distancia Mahalanobis")
        print("3. Máxima Probabilidad")
        metodo = input("Selecciona un método: ")

        if metodo == "1": #Método de distancia euclidiana 
            menor, idx, distancias = calcular_distancia_euclidiana(pixel_rgb, centroides)
            print("Distancias Euclidianas:")
            for i, d in enumerate(distancias):
                print(f"Clase {i + 1} ({nombres[i]}): {d:.2f}")
            print(f"Clase asignada: {nombres[idx]} (distancia mínima: {menor:.2f})")
            graficar_en_imagen(clases, pixel_rgb, nombres, imagen)


        elif metodo == "2": #Método de distancia mahalanobis 
            distancias = [
                calcular_distancia_mahalanobis(pixel_rgb, centroides[i], np.array(clases[i]).T)
                for i in range(num_clases)
            ]
            menor = np.min(distancias)
            idx = np.argmin(distancias)
            print("Distancias Mahalanobis:")
            for i, d in enumerate(distancias):
                print(f"Clase {i + 1} ({nombres[i]}): {d:.2f}")
            print(f"Clase asignada: {nombres[idx]}")
            graficar_en_imagen(clases, pixel_rgb, nombres, imagen)


        elif metodo == "3": #Método de máxima probbilidad 
            pixel_reshape = pixel_rgb.reshape(3, 1)
            probabilidades = [
                maxima_probabilidad(pixel_reshape, np.array([p[2] for p in clases[i]]).T, 3)
                for i in range(num_clases)
            ]
            total = sum(probabilidades)
            porcentajes = [(p / total * 100) for p in probabilidades]
            for i, porcentaje in enumerate(porcentajes):
                print(f"Clase {i + 1} ({nombres[i]}): {porcentaje:.2f}%")
            idx = np.argmax(probabilidades)
            print(f"Clase asignada: {nombres[idx]}")
            graficar_en_imagen(clases, pixel_rgb, nombres, imagen)


        otra = input("\n¿Quieres clasificar otro punto? (s/n): ")
        if otra.lower() != 's': 
            break

    print("\nPrograma finalizado.")

if __name__ == "__main__":
    ejecutar_programa() 





