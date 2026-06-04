"""
Example usage with web server
"""

from carlaviz import CarlaViz, CarlaVizWebServer


def main():
    """Example with web server"""
    # Create web server
    web_server = CarlaVizWebServer(port=8080)
    web_server.start()
    
    # Create CarlaViz instance - 不使用headless模式，测试窗口模式是否正常
    viz = CarlaViz(host='0.0.0.0', port=2000, headless=False)
    viz.run(web_server=web_server)
    
    # Stop web server when done
    web_server.stop()


if __name__ == '__main__':
    main()