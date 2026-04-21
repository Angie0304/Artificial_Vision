# Image Chain Code

This project implements an image processing system based on chain code representation, allowing the analysis and description of object boundaries within images. The system is structured in a modular way, separating the user interface, core algorithms, and utility functions to ensure clarity and scalability.

## Project structure
```text
image_chain_code/
├── README.md                    # Documentation and execution guide
├── requeriments.txt             # Project dependencies
└── src/
    ├── modules/                 # Core algorithm logic
    │   ├── algoritmo_cadena.py
    │   ├── color.py
    │   ├── imagen.py
    │   ├── matriz_distancia.py
    │   └── punto.py
    ├── ui/                      # User interaction
    │   └── menu.py
    ├── utils/                   # Helper functions
    │   └── funciones_estandar_V2.py
    └── main.py                  # Entry point             
```
## How works it

The system processes images to extract boundary information. After loading and preprocessing the image, boundary points are identified and represented as connected pixels. The core algorithm computes the chain code, encoding the direction between consecutive points to provide a compact representation of the object’s shape.

The system is organized into modules that handle:

- Image processing and representation  
- Point and distance calculations  
- Chain code computation  
- User interaction through a menu-driven interface  
