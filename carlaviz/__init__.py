"""
CarlaViz - CARLA 3D Visualization Tool

A comprehensive visualization tool for CARLA simulator that provides:
- Real-time 3D rendering using Pygame and OpenGL
- Web-based visualization via Flask
- Automatic detection of CARLA environment and vehicles
- Support for multiple camera modes (follow, free view)
- Rendering of roads, buildings, vehicles, and traffic lights
"""

__version__ = "0.1.0"
__author__ = "CarlaViz Team"

from .core.visualizer import CarlaViz
from .core.camera import CarlaVizCamera
from .web.server import CarlaVizWebServer

__all__ = ['CarlaViz', 'CarlaVizCamera', 'CarlaVizWebServer']