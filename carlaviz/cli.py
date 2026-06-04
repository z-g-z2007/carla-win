"""
Command line interface for CarlaViz
"""

import argparse
import sys

from carlaviz.core.visualizer import CarlaViz
from carlaviz.web.server import CarlaVizWebServer


def main():
    """Main entry point for CarlaViz CLI"""
    parser = argparse.ArgumentParser(
        description="CARLA 3D Visualization Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='CARLA server host'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=2000,
        help='CARLA server port'
    )
    
    parser.add_argument(
        '--web',
        nargs='?',
        const=8080,
        type=int,
        help='Enable web server (default port: 8080)'
    )
    
    args = parser.parse_args()

    print("=" * 60)
    print("CarlaViz - CARLA 3D Visualization Tool")
    print("=" * 60)
    print(f"Connecting to CARLA: {args.host}:{args.port}")
    
    # 创建并启动Web服务器（如果需要）
    web_server = None
    if args.web is not None:
        print(f"Web server enabled on port: {args.web}")
        web_server = CarlaVizWebServer(args.web)
        web_server.start()
    
    print("Controls:")
    print("  ESC: Exit")
    print("  TAB: Toggle follow mode")
    print("  Left Click + Drag: Rotate")
    print("  Right Click + Drag: Pan")
    print("  Mouse Wheel: Zoom")
    print("=" * 60)

    try:
        # 创建CarlaViz实例
        app = CarlaViz(args.host, args.port)
        app.run(web_server=web_server)
    except KeyboardInterrupt:
        print("\nExiting CarlaViz...")
    finally:
        # 停止Web服务器
        if web_server:
            web_server.stop()
        
        sys.exit(0)


if __name__ == '__main__':
    main()