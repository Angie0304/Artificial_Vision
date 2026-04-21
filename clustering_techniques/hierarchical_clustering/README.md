# Hierarchical Clustering
This module implements a hierarchical clustering algorithm using a bottom-up (agglomerative) approach. It groups data points based on their similarity and visualizes the clustering process step by step.

### Module Structure

```text
hierarchical_clustering/
├── README.md              # Documentation and usage guide
├── clustering.py          # Hierarchical clustering implementation
├── dendograma.png         # Dendrogram visualization of the clustering process
├── requirements.txt       # Module dependencies
└── resultado_final.png    # Final clustering result visualization
```

## How it works

The algorithm follows an agglomerative (bottom-up) clustering approach:

1. Generate random 2D data points  
2. Initialize each point as its own cluster  
3. Compute pairwise distances between all clusters  
4. Merge the two closest clusters using **single linkage** (minimum distance)  
5. Update clusters and repeat the process  
6. Continue until all points belong to a single cluster  
7. Store the merging history for visualization  

During execution, the clustering process is displayed step by step, showing how clusters are progressively grouped.

Finally, the algorithm builds a **dendrogram**, which represents the hierarchical relationships between clusters and the distances at which they were merged.

### Distance Metric

 **single linkage**, defined as the minimum distance between points of two clusters.
