"""
Visión Artificial
Práctica 1
Gutiérrez Sánchez Angélica 
Grupo: 5BM2
"""

import matplotlib.pyplot as plt
import numpy as np

# Clases 
clase1 = np.array([[-1, -1, -3, 1, 2], 
                   [2 , 4 ,  3, 3, 5]])

clase2 = np.array([[7, 6, 7, 7, 9], 
                   [3, 4, 5, 7, 6]])

clase3 = np.array([[-2, -2, -3, -4, -5],
                   [-1, -4, -4, -2, -3]])

clase4 = np.array([[ 1,  2,  3,  3, 3],
                   [-6, -5, -4, -6, -7]])

clase5 = np.array([[ 6,  8,  8,  8, 9],
                   [-3, -2, -4, -6, 0]]) 


print("Ingrese las coordenadas de un punto nuevo para clasificarlo")
x = float(input("x = "))
y = float(input("y= "))
umbral = 15
 #aqui
puntoNuevo = np.array([x, y])

#Centroides
centro1 = np.mean(clase1, axis=1) #promedio a lo largo de las filas 
centro2 = np.mean(clase2, axis=1)
centro3 = np.mean(clase3, axis=1)
centro4 = np.mean(clase4, axis=1)
centro5 = np.mean(clase5, axis=1)

#Distancia euclidiana
dist1 = np.linalg.norm(puntoNuevo - centro1)
dist2 = np.linalg.norm(puntoNuevo - centro2)
dist3 = np.linalg.norm(puntoNuevo - centro3)
dist4 = np.linalg.norm(puntoNuevo - centro4)
dist5 = np.linalg.norm(puntoNuevo - centro5)
distancias = [dist1, dist2, dist3, dist4, dist5]

#Mostrar distancias 
print("Distancia a clase 1: ", dist1)
print("Distancia a clase 2: ", dist2)
print("Distancia a clase 3: ", dist3)
print("Distancia a clase 4: ", dist4)
print("Distancia a clase 5: ", dist5)
print("\n")

#Elegir la menor distancia 
menorDistancia = np.min(distancias)
if menorDistancia > umbral:
    print("No pertenece a ninguna clase")
else:
    print("Menor distancia:",menorDistancia)
    for i in range(len(distancias)): #ver a que clase pertenece 
        if distancias[i] == menorDistancia:
            print("Pertenece a la clase",i+1) #para empatar los indices con num de clase 


#print('Centroide4=', centro4)

# Graficar
plt.figure(figsize=(10, 5))
plt.plot(clase1[0], clase1[1], 'o', color='blue' ,label='Clase 1') #listas internas del arreglo clase 1 
plt.plot(clase2[0], clase2[1], 'o', color='green', label='Clase 2')
plt.plot(clase3[0], clase3[1], 'o', color='purple', label='Clase 3')
plt.plot(clase4[0], clase4[1], 'o', color='orange', label='Clase 4')
plt.plot(clase5[0], clase5[1], 'o', color='magenta', label='Clase 5')

plt.plot(puntoNuevo[0], puntoNuevo[1], 'D', color='yellow', label='Punto Nuevo') #rombo

plt.plot(centro1[0], centro1[1], 's', color='red', label='Centroide 1') #cuadrado
plt.plot(centro2[0], centro2[1], 'o', color='red', label='Centroide 2') #punto
plt.plot(centro3[0], centro3[1], 'p', color='red', label='Centroide 3') #pentagono
plt.plot(centro4[0], centro4[1], '*', color='red', label='Centroide 4') 
plt.plot(centro5[0], centro5[1], '+', color='red', label='Centroide 5')

plt.legend()
plt.title("Clasificador Euclidiano")

#Límites de plano cartesiano
plt.xlim(-10, 10)  
plt.ylim(-10, 10)  

plt.axhline(0, color='black', linewidth=1)  
plt.axvline(0, color='black', linewidth=1)  

plt.grid(True) 

# Guardamos imagen 
plt.savefig('resultado_euclidiano.png', dpi=300, bbox_inches='tight')

plt.show()