# Mahalanobis Classification

This module implements a classification system using **Mahalanobis distance**, which accounts for the data distribution and improves classification in datasets with varying variance. Euclidean distance is also included for comparison.

## Module Structure

```text
mahalanobis_classification/
├── README.md                   # Documentation and execution guide
├── clasificador.py             # Mahalanobis distance classifier implementation
|── requirements.txt            # Module dependencies
└── resultado.png               # Scatter plot showing covariance and classification
```

## How it works

The classifier follows these steps:

1. Select the number of dimensions (2D or 3D)  
2. Define the number of classes  
3. Input centroid coordinates and dispersion for each class  
4. Generate synthetic data for each class  
5. Input a new point to classify  
6. Choose a distance metric:
   - Euclidean distance  
   - Mahalanobis distance  
7. Compute distances and assign the point to the nearest class

   
## Mahalanobis Distance

$$
d(x,\mu)=\sqrt{(x-\mu)^T S^{-1} (x-\mu)}
$$

Where:

- x: input point  
- μ: class centroid  
- S⁻¹: inverse covariance matrix

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
- Assign the point to a class
- Generate and save a visualization (resultado.png)


## Status 
Completed





