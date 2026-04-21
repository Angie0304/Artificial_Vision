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

# ---------- Generar colores ----------
total_clusters = 2 * n_puntos - 1
color_list = [cm.get_cmap('tab20b')(i / total_clusters) for i in range(total_clusters)]
color_map = {}
color_index = 0

# ---------- Inicializar clusters ----------
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

# ---------- Mostrar puntos ----------
def mostrar_puntos_coloreados(points, clusters, step, final=False):
    plt.figure(figsize=(6, 6))
    ax = plt.gca()

    for cluster_id, indices in clusters.items():
        color = color_map[cluster_id]
        cluster_pts = points[indices]

        for i in indices:
            x, y = points[i]
            plt.scatter(x, y, color=color, edgecolors='black')
            plt.text(x + 1, y + 1, f'P{i}', fontsize=9)

        if len(cluster_pts) > 1:
            x_mean = cluster_pts[:, 0].mean()
            y_mean = cluster_pts[:, 1].mean()
            x_range = cluster_pts[:, 0].max() - cluster_pts[:, 0].min()
            y_range = cluster_pts[:, 1].max() - cluster_pts[:, 1].min()

            ellipse = patches.Ellipse(
                (x_mean, y_mean),
                x_range + 10,
                y_range + 10,
                edgecolor=color,
                facecolor='none',
                lw=2,
                linestyle='--'
            )
            ax.add_patch(ellipse)

    plt.title(f"Puntos agrupados - Paso {step}")
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.xlim(0, 110)
    plt.ylim(0, 110)

    # 🔥 Guardar SOLO en el último paso
    if final:
        plt.savefig("resultado_final.png", dpi=300)

    plt.show()

# ---------- Distancia ----------
def cluster_distance(c1, c2):
    return min([
        euclidean(points[i], points[j])
        for i in clusters[c1]
        for j in clusters[c2]
    ])

# ---------- Matriz ----------
def imprimir_matriz_distancias(clusters, label_map):
    keys = list(clusters.keys())
    print("Matriz de distancias:")
    for i in keys:
        fila = ""
        for j in keys:
            if i == j:
                fila += " 0.00 "
            else:
                fila += f"{cluster_distance(i, j):.2f} "
        print(fila)
    print()

# ---------- Clustering ----------
while len(clusters) > 1:
    imprimir_matriz_distancias(clusters, label_map)

    # 🔥 detectar último paso
    es_final = (len(clusters) == 2)

    mostrar_puntos_coloreados(points, clusters, step, final=es_final)

    keys = list(clusters.keys())
    min_dist = float('inf')
    best_pair = (None, None)

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            dist = cluster_distance(keys[i], keys[j])
            if dist < min_dist:
                min_dist = dist
                best_pair = (keys[i], keys[j])

    c1, c2 = best_pair

    new_cluster = next_cluster
    clusters[new_cluster] = clusters[c1] + clusters[c2]
    cluster_members[new_cluster] = cluster_members[c1] + cluster_members[c2]
    label_map[new_cluster] = f'P{new_cluster}'
    color_map[new_cluster] = color_list[color_index]
    color_index += 1

    history.append((c1, c2, min_dist))

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

    for i, leaf_id in enumerate(leaf_order):
        positions[leaf_id] = i

    fig, ax = plt.subplots(figsize=(10, 6))

    for paso, (c1, c2, dist) in enumerate(history):
        cluster_id = paso + len(reordered_labels)
        color = color_map.get(cluster_id, 'black')

        x1, x2 = positions[c1], positions[c2]
        h1 = heights.get(c1, 0)
        h2 = heights.get(c2, 0)

        ax.plot([x1, x1], [h1, dist], c=color, lw=2)
        ax.plot([x2, x2], [h2, dist], c=color, lw=2)
        ax.plot([x1, x2], [dist, dist], c=color, lw=2)

        positions[cluster_id] = (x1 + x2) / 2
        heights[cluster_id] = dist

    for i, label in enumerate(reordered_labels):
        ax.text(i, -5, label, ha='center', rotation=90)

    ax.set_title("Dendrograma")
    plt.tight_layout()

    # 🔥 Guardar dendrograma
    plt.savefig("dendrograma.png", dpi=300)

    plt.show()

plot_dendrogram(history, reordered_labels, leaf_order, label_map)

