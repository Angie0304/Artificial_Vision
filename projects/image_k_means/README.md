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

Each pixel in the image is treated as a data point in color space. The system groups pixels into K clusters based on their similarity, iteratively updating cluster centers until stable groups are formed. The result is a segmented image where each region is represented by its corresponding cluster color.
