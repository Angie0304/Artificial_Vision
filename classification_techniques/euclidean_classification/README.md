# Euclidean Classification
This module implements a Euclidean distance-based classifier for 2D data. It assigns a class to a new point based on its distance to predefined class centroids.

## Module Structure

```text
meuclidean_classification/
├── README.md                   # Documentation and execution guide
├── clasificador.py             # Euclidean distance classifier implementation
├── requirements.txt            # Module dependencies 
└── resultado.png               # Scatter plot showing centroids and classification
```

## How it works
The classifier follows these steps:

1. Define multiple classes with sample points  
2. Compute the centroid of each class  
3. Input a new point  
4. Calculate the Euclidean distance to each centroid  
5. Assign the point to the nearest class (if within threshold)

The classification includes a threshold (15): if the minimum distance exceeds this value, the point is not assigned to any class.

## Euclidean distance
$$
d(x,y)=\sqrt{\sum_{i=1}^{n}(x_i - y_i)^2}
$$

Where:
- x, y: feature vectors  
- n: number of dimensions  


## Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the program
```bash
python clasificador.py
```

### 3. Output
The program will:
- Display distances to each class
- Indicate the assigned class (or none)
- Generate and save a visualization (resultado.png)

## Status
Completed




