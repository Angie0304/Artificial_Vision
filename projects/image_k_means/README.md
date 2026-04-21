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

Each pixel is represented as a point in color space, and the image is reshaped into a set of pixel values. The algorithm initializes K centroids and iteratively updates them based on the mean of assigned pixels until convergence.

The final image is reconstructed using the cluster centroids, producing a segmented version of the original image.


## Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the program
```bash
python src/main.py
```

### 3. Interaction

The system allows you to:
- Load an image
- Select the number of clusters (K)
- Generate a segmented image

## Status 
Completed



