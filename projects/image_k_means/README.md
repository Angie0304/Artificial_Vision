# Image K Means

This project implements image segmentation using the **K-Means clustering algorithm**, grouping pixels by color similarity to produce simplified representations of images. This approach enables efficient color quantization and visual abstraction.

## Project structure
```text
image_k_means/
├── README.md                  # Documentation and execution guide
├── requeriments.txt           # Project dependencies
└── src/
    ├── modules/               # Core algorithm logic
    │   ├── algoritmo_cadena.py
    │   ├── algoritmo_kmeans.py
    │   ├── color.py
    │   ├── imagen.py
    │   ├── matriz_distancia.py
    │   ├── punto.py
    │   └── visualizador_kmeans_matplotlib.py
    ├── ui/                    # User interaction
    │   └── menu.py
    ├── utils/                 # Helper functions
    │   └── funciones_estandar_V2.py
    └── main.py                # Entry point                       
```

## ⚙️ How it works
The image is first loaded and reshaped into a set of pixel values. The algorithm then initializes K centroids and assigns each pixel to the nearest centroid based on color similarity. Centroids are updated as the mean of their assigned pixels, and this process repeats until convergence. Finally, the image is reconstructed by replacing each pixel with the color of its corresponding cluster, producing a segmented version of the original image.
