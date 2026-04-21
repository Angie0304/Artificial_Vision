import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
import random
import matplotlib.cm as cm
import matplotlib.patches as patches

# ---------- Parámetros ----------
n_puntos = int(input("¿Cuántos puntos aleatorios quieres usar? "))
points = np.array([[random.uniform(0, 100), random.uniform(0, 100)] for _ in range(n_puntos)])
labels = [f'P{i}' for i in range(len(points))]

# ---------- Generar colores únicos ----------
total_clusters = 2 * n_puntos - 1  # número total de clusters posibles en clustering jerárquico
color_list = [cm.get_cmap('tab20b')(i / total_clusters) for i in range(total_clusters)]
color_map = {}  # Mapa de cluster_id a color
color_index = 0

# ---------- Inicializar clusters con colores únicos ----------
clusters = {}
cluster_members = {}
label_map = {}
for i in range(len(points)):
    clusters[i] = [i]
    cluster_members[i] = [i]
    label_map[i] = f'P{i}'
    color_map[i] = color_list[color_index]
    color_index += 1

history = []
next_cluster = len(points)
step = 1

# ---------- Mostrar puntos con elipses ----------
def mostrar_puntos_coloreados(points, clusters, step):
    plt.figure(figsize=(6, 6))
    ax = plt.gca()

    for cluster_id, indices in clusters.items():
        color = color_map[cluster_id]
        cluster_pts = points[indices]

        # Dibujar puntos
        for i in indices:
            x, y = points[i]
            plt.scatter(x, y, color=color, edgecolors='black')
            plt.text(x + 1, y + 1, f'P{i}', fontsize=9, color='black')

        # Dibujar elipse
        if len(cluster_pts) > 1:
            x_mean = cluster_pts[:, 0].mean()
            y_mean = cluster_pts[:, 1].mean()
            x_range = cluster_pts[:, 0].max() - cluster_pts[:, 0].min()
            y_range = cluster_pts[:, 1].max() - cluster_pts[:, 1].min()
            width = x_range + 10
            height = y_range + 10

            ellipse = patches.Ellipse(
                (x_mean, y_mean), width, height,
                edgecolor=color, facecolor='none', lw=2, linestyle='--'
            )
            ax.add_patch(ellipse)

    plt.title(f"Puntos agrupados - Paso {step}")
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.xlim(0, 110)
    plt.ylim(0, 110)
    plt.show()

# ---------- Distancia entre clusters ----------
def cluster_distance(c1, c2):
    return min([
        euclidean(points[i], points[j])
        for i in clusters[c1]
        for j in clusters[c2]
    ])

# ---------- Matriz de distancias ----------
def imprimir_matriz_distancias(clusters, label_map):
    keys = list(clusters.keys())
    matriz = np.zeros((len(keys), len(keys)))
    print("Matriz de distancias entre clusters actuales:")
    header = "       " + "".join([f"{label_map[k]:>6}" for k in keys])
    print(header)
    for i in range(len(keys)):
        fila = f"{label_map[keys[i]]:>6} "
        for j in range(len(keys)):
            if i == j:
                valor = 0.0
            else:
                valor = cluster_distance(keys[i], keys[j])
            matriz[i, j] = valor
            fila += f"{valor:6.2f}"
        print(fila)
    print()

# ---------- Agrupamiento jerárquico ----------
while len(clusters) > 1:
    imprimir_matriz_distancias(clusters, label_map)
    mostrar_puntos_coloreados(points, clusters, step)

    keys = list(clusters.keys())
    min_dist = float('inf')
    best_pair = (None, None)

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            c1, c2 = keys[i], keys[j]
            dist = cluster_distance(c1, c2)
            if dist < min_dist:
                min_dist = dist
                best_pair = (c1, c2)

    c1, c2 = best_pair
    name1 = label_map.get(c1, f'C{c1}')
    name2 = label_map.get(c2, f'C{c2}')

    new_cluster = next_cluster
    clusters[new_cluster] = clusters[c1] + clusters[c2]
    cluster_members[new_cluster] = cluster_members[c1] + cluster_members[c2]
    label_map[new_cluster] = f'P{new_cluster}'
    color_map[new_cluster] = color_list[color_index]
    color_index += 1
    history.append((c1, c2, min_dist))

    print(f"Paso {step}: Agrupar {name1} y {name2} (distancia mínima = {min_dist:.2f}), nuevo cluster: P{new_cluster}\n")

    del clusters[c1]
    del clusters[c2]
    next_cluster += 1
    step += 1

# ---------- Dendrograma ----------
leaf_order = cluster_members[next_cluster - 1]
reordered_labels = [labels[i] for i in leaf_order]

def plot_dendrogram(history, reordered_labels, leaf_order, label_map_final):
    heights = {}
    positions = {}

    # Inicializar posiciones de hojas
    for i, leaf_id in enumerate(leaf_order):
        positions[leaf_id] = i

    fig, ax = plt.subplots(figsize=(10, 6))

    for paso, (c1, c2, dist) in enumerate(history):
        # Cluster ID del nuevo grupo formado en este paso
        cluster_id = paso + len(reordered_labels)
        color = color_map.get(cluster_id, 'black')

        x1, x2 = positions[c1], positions[c2]
        h1 = heights.get(c1, 0)
        h2 = heights.get(c2, 0)

        # Dibujar líneas de unión (en color del nuevo cluster)
        ax.plot([x1, x1], [h1, dist], c=color, lw=2)  # línea vertical c1
        ax.plot([x2, x2], [h2, dist], c=color, lw=2)  # línea vertical c2
        ax.plot([x1, x2], [dist, dist], c=color, lw=2)  # línea horizontal que los une

        # Etiqueta del nuevo cluster (opcional)
        etiqueta = label_map_final.get(cluster_id, f'P{cluster_id}')
        ax.text((x1 + x2) / 2, dist + 1, etiqueta, ha='center', fontsize=8, color=color)

        # Guardar nueva posición y altura
        positions[cluster_id] = (x1 + x2) / 2
        heights[cluster_id] = dist

    # Dibujar etiquetas para las hojas (abajo)
    for i, label in zip(range(len(reordered_labels)), reordered_labels):
        ax.text(i, -5, label, ha='center', rotation=90)

    ax.set_ylim(-10, max(heights.values()) + 10)
    ax.set_xlim(-1, len(reordered_labels))
    ax.set_xticks([])
    ax.set_title("Dendrograma con color por agrupamiento")
    plt.tight_layout()
    plt.show()



plot_dendrogram(history, reordered_labels, leaf_order, label_map)




