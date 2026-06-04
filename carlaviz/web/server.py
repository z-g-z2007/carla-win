"""
Web server module for CarlaViz
Provides HTTP-based visualization streaming
"""

import threading

# 尝试导入Flask
try:
    from flask import Flask, render_template_string, Response
    flask_available = True
except ImportError:
    flask_available = False

# 导入模块而不是具体变量，确保共享同一个对象
import carlaviz.core.visualizer as visualizer_module


class CarlaVizWebServer:
    """
    CarlaViz Web服务器 - 可选功能
    提供HTTP服务，将Pygame渲染的画面通过网页展示
    """

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CarlaViz Web - CARLA 3D Visualization</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: Arial, sans-serif;
        }
        #video-container {
            border: 2px solid #333;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        #video {
            display: block;
            max-width: 100%;
            height: auto;
        }
        .info {
            position: fixed;
            bottom: 20px;
            left: 20px;
            color: #fff;
            font-size: 14px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 4px;
        }
        .controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            color: #fff;
            font-size: 12px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div id="video-container">
        <img id="video" src="/stream" />
    </div>
    <div class="info">
        <strong>CarlaViz Web</strong><br>
        Press ESC to quit | Refresh page if disconnected
    </div>
    <div class="controls">
        <strong>Controls:</strong><br>
        Left Click: Rotate<br>
        Right Click: Pan<br>
        Mouse Wheel: Zoom<br>
        TAB: Toggle Follow Mode
    </div>
</body>
</html>
"""

    def __init__(self, port=8080):
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()
        self.server_thread = None
        self.running = False

    def _setup_routes(self):
        """设置Flask路由"""
        @self.app.route('/')
        def index():
            return render_template_string(self.HTML_TEMPLATE)

        @self.app.route('/stream')
        def stream():
            """返回视频流（multipart格式）"""
            print("Stream connection established")
            def generate():
                while True:
                    with visualizer_module.frame_lock:
                        if visualizer_module.frame_data:
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + visualizer_module.frame_data + b'\r\n')
            
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def _get_black_image(self):
        """生成一个黑色占位图片"""
        try:
            from PIL import Image
            import io
            img = Image.new('RGB', (800, 600), color=(0, 0, 0))
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            return buffer.getvalue()
        except ImportError:
            return b''

    def start(self):
        """启动Web服务器"""
        if not flask_available:
            print("Error: flask is not available. Cannot start web server.")
            return False

        self.running = True

        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"Web server started at http://localhost:{self.port}")
        return True

    def stop(self):
        """停止Web服务器"""
        self.running = False