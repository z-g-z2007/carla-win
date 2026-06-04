"""
Basic usage example for CarlaViz
"""

from carlaviz import CarlaViz


def main():
    """Basic usage example"""
    # Create CarlaViz instance
    viz = CarlaViz(host='127.0.0.1', port=2000)
    
    # Run the visualization
    viz.run()


if __name__ == '__main__':
    main()