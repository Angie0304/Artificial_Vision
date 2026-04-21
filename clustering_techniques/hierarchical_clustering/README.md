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


### How it works

The algorithm starts by treating each point as an individual cluster and iteratively merges clusters based on their similarity.

The process involves:
- Computing distances between clusters  
- Merging the closest clusters using **single linkage**  
- Repeating until a single cluster remains  
- Storing the merge history to build a **dendrogram**  


During execution, the clustering process is visualized step by step, and the final result is represented with a dendrogram.

### Distance metric

Single linkage: the distance between two clusters is defined as the minimum distance between any pair of points belonging to those clusters.
