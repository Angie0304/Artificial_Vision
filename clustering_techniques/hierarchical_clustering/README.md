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


## ⚙️ How it works

This module applies an **agglomerative (bottom-up) clustering** approach.

Random 2D data points are generated, and each point is initially treated as its own cluster. The algorithm then computes pairwise distances between clusters and iteratively merges the two closest clusters.

Cluster similarity is defined using **single linkage**, meaning the distance between two clusters is the minimum distance between any pair of their points.

This process is repeated until all points are merged into a single cluster. During execution, the clustering process is visualized step by step, showing how clusters are progressively grouped.

The merge history is stored and later used to construct a **dendrogram**, which represents the hierarchical relationships between clusters and the distances at which they were merged.


## 📐 Distance Metric

Single linkage: the distance between two clusters is defined as the minimum distance between any pair of points belonging to those clusters.
