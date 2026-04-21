# Mahalanobis Classification

This module implements a classification system using **Mahalanobis distance**, which accounts for the data distribution and improves classification in datasets with varying variance. Euclidean distance is also included for comparison.

### Module Structure

```text
mahalanobis_classification/
├── README.md                   # Documentation and execution guide
├── clasificador.py             # Mahalanobis distance classifier implementation
|── requirements.txt            # Module dependencies
└── resultado.png               # Scatter plot showing covariance and classification
```

### How it works

The classifier follows these steps:

1. Select the number of dimensions (2D or 3D)
2. Define the number of classes
3. Input centroid coordinates and dispersion for each class
4. Generate synthetic data for each class
5. Input a new point to classify
6. Choose a distance metric:
7. Euclidean distance
8. Mahalanobis distance
9. Compute distances and assign the point to the nearest class

### Mahalanobis Distance

$$
d(x,\mu)=\sqrt{(x-\mu)^T S^{-1} (x-\mu)}
$$

Where:

- x: input point  
- μ: class centroid  
- S⁻¹: inverse covariance matrix  

