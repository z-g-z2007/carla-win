"""
Visualizer module for CarlaViz
Main class that handles CARLA connection and visualization
"""

import os
import sys
import pygame
import threading
from io import BytesIO
from OpenGL.GL import *

from .camera import CarlaVizCamera
from .renderer import CarlaRenderer

# 全局变量用于共享图像数据
frame_data = None
frame_lock = threading.Lock()

# 尝试导入可选依赖
try:
    import carla
    carla_available = True
except ImportError:
    carla_available = False

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


class CarlaViz:
    """
    CarlaViz 主类 - 基于 Pygame 的基础可视化工具
    提供3D场景渲染，支持与CARLA仿真环境连接
    """

    def __init__(self, host='127.0.0.1', port=2000, headless=False):
        self.host = host
        self.port = port
        self.headless = headless  # 无头模式 - 不显示pygame窗口
        self.world = None
        self.map = None
        self.player = None
        self.waypoints = []
        self.demo_mode = True
        self.demo_time = 0.0
        self.demo_vehicles = []

        self.camera = CarlaVizCamera()
        self.renderer = CarlaRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.running = True
        self.mouse_pressed = None
        self.last_mouse_pos = (0, 0)

        self._init_pygame()
        if not self.headless:
            self.renderer.init_opengl()
        else:
            self._init_headless_opengl()
        self._connect_carla()
        self._init_demo_mode()

    def _init_pygame(self):
        """初始化Pygame"""
        if self.headless:
            # 无头模式：尝试使用不同的方法来支持OpenGL
            # 在Windows上使用windib但最小化窗口
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        else:
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        pygame.init()
        
        if self.headless:
            # 创建窗口后立即最小化
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
            pygame.display.set_caption("CarlaViz (Headless)")
            # 最小化窗口
            pygame.display.iconify()
        else:
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
            pygame.display.set_caption("CarlaViz")

    def _init_headless_opengl(self):
        """在无头模式下初始化OpenGL"""
        from OpenGL.GL import glEnable, GL_DEPTH_TEST, GL_LIGHTING, GL_LIGHT0
        from OpenGL.GLU import gluPerspective
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def _connect_carla(self):
        """连接CARLA服务器 - 自动检测运行中的CARLA环境"""
        if not carla_available:
            print("CARLA module not available. Running in demo mode.")
            return

        try:
            client = carla.Client(self.host, self.port)
            client.set_timeout(2.0)
            self.world = client.get_world()
            self.map = self.world.get_map()
            self.demo_mode = False
            print(f"Connected to CARLA server: {self.host}:{self.port}")

            self.waypoints = self.map.generate_waypoints(2.0)
            print(f"Loaded {len(self.waypoints)} waypoints")

        except Exception as e:
            print(f"Failed to connect to CARLA: {e}")
            print("Running in demo mode")

    def _init_demo_mode(self):
        """初始化演示模式"""
        self.demo_vehicles = [
            {'x': 0, 'y': 0, 'z': 0.5, 'yaw': 0, 'is_ego': True},
            {'x': -50, 'y': 30, 'z': 0.5, 'yaw': 90, 'is_ego': False},
            {'x': 40, 'y': -20, 'z': 0.5, 'yaw': -45, 'is_ego': False},
        ]

    def draw_road_network(self):
        """绘制道路网络"""
        if not self.waypoints and not self.demo_mode:
            return

        glDisable(GL_LIGHTING)

        if self.demo_mode:
            self.renderer.draw_demo_roads()
        else:
            self.renderer.draw_carla_roads(self.waypoints, carla)

        glEnable(GL_LIGHTING)

    def draw_vehicles(self):
        """绘制车辆"""
        glEnable(GL_LIGHTING)

        if self.demo_mode:
            self._draw_demo_vehicles()
        else:
            self._draw_carla_vehicles()

    def _draw_demo_vehicles(self):
        """绘制演示车辆"""
        import math
        self.demo_time += 0.016

        # 更新自车位置
        self.demo_vehicles[0]['x'] = 30 * math.sin(self.demo_time * 0.3)
        self.demo_vehicles[0]['y'] = 30 * math.cos(self.demo_time * 0.3) - 30
        self.demo_vehicles[0]['yaw'] = math.degrees(self.demo_time * 0.3) + 90

        # 更新相机
        ego = self.demo_vehicles[0]
        self.camera.set_target(ego['x'], ego['y'], ego['z'], ego['yaw'])

        for vehicle in self.demo_vehicles:
            glPushMatrix()
            glTranslatef(vehicle['x'], vehicle['z'], vehicle['y'])
            glRotatef(vehicle['yaw'], 0, 1, 0)

            if vehicle['is_ego']:
                glColor4f(1.0, 0.4, 0.8, 1.0)
            else:
                glColor4f(0.5, 0.5, 0.5, 1.0)

            self.renderer.draw_box(4.5, 2.0, 1.5)

            # 方向指示器
            glDisable(GL_LIGHTING)
            if vehicle['is_ego']:
                glColor4f(0.0, 1.0, 0.0, 1.0)
            else:
                glColor4f(1.0, 1.0, 1.0, 1.0)

            glBegin(GL_TRIANGLES)
            glVertex3f(2.5, 0, 0.5)
            glVertex3f(3.5, -0.3, 0.5)
            glVertex3f(3.5, 0.3, 0.5)
            glEnd()
            glEnable(GL_LIGHTING)

            glPopMatrix()

            if vehicle['is_ego']:
                self.renderer.draw_sensor_range(vehicle['x'], vehicle['y'], 0)

    def _draw_carla_vehicles(self):
        """绘制CARLA车辆"""
        actors = self.world.get_actors()
        ego_count = 0
        total_vehicles = 0

        for actor in actors:
            if 'vehicle' in actor.type_id:
                total_vehicles += 1
                transform = actor.get_transform()
                location = transform.location
                rotation = transform.rotation
                bbox = actor.bounding_box
                extent = bbox.extent

                is_ego = self._is_ego_vehicle(actor)

                if is_ego:
                    ego_count += 1

                glPushMatrix()
                glTranslatef(location.x, location.z, location.y)
                glRotatef(-rotation.yaw, 0, 1, 0)

                if is_ego:
                    glColor4f(1.0, 0.4, 0.8, 1.0)
                else:
                    glColor4f(1.0, 0.0, 0.0, 1.0)

                self.renderer.draw_box(extent.x * 2, extent.y * 2, extent.z * 2)

                # 方向指示器
                glDisable(GL_LIGHTING)
                if is_ego:
                    glColor4f(0.0, 1.0, 0.0, 1.0)
                else:
                    glColor4f(0.8, 0.8, 0.8, 1.0)

                glBegin(GL_TRIANGLES)
                glVertex3f(extent.x + 0.5, 0, 0)
                glVertex3f(extent.x + 1.5, -0.3, 0)
                glVertex3f(extent.x + 1.5, 0.3, 0)
                glEnd()
                glEnable(GL_LIGHTING)

                glPopMatrix()

                if is_ego:
                    self.renderer.draw_sensor_range(location.x, location.y, location.z)
                    self.camera.set_target(location.x, location.y, location.z, rotation.yaw)

        # 打印车辆统计信息
        if not hasattr(self, '_frame_count'):
            self._frame_count = 0
        self._frame_count += 1
        if self._frame_count % 100 == 0:
            print(f"Vehicles in scene: {total_vehicles}, Ego vehicles: {ego_count}")

        if ego_count == 0 and not hasattr(self, '_ego_warning_printed'):
            print("No ego vehicle found. Using first vehicle as ego.")
            self._ego_warning_printed = True

    def _is_ego_vehicle(self, vehicle):
        """智能识别自车"""
        role_names = ['ego', 'hero', 'autopilot', 'player', 'agent']

        # 检查role_name属性
        for attr_id, attr_value in vehicle.attributes.items():
            if attr_id == 'role_name':
                if attr_value.lower() in role_names:
                    return True

        # 检查是否是我们生成的玩家车辆
        if self.player and vehicle.id == self.player.id:
            return True

        # 检查是否启用了autopilot
        try:
            if vehicle.is_autopilot_enabled():
                return True
        except:
            pass

        # 使用第一个车辆
        if not hasattr(self, '_first_vehicle_id'):
            actors = self.world.get_actors()
            for actor in actors:
                if 'vehicle' in actor.type_id:
                    self._first_vehicle_id = actor.id
                    if vehicle.id == self._first_vehicle_id:
                        print(f"Using first vehicle as ego: {actor.type_id}")
                        return True
                    break
        elif hasattr(self, '_first_vehicle_id') and vehicle.id == self._first_vehicle_id:
            return True

        return False

    def draw_traffic_lights(self):
        """绘制交通信号灯"""
        glEnable(GL_LIGHTING)

        if self.demo_mode:
            self._draw_demo_traffic_lights()
        else:
            self._draw_carla_traffic_lights()

    def _draw_demo_traffic_lights(self):
        """绘制演示交通灯"""
        lights = [
            (-50, -50, 0, (1, 0, 0)),
            (50, -50, 0, (0, 1, 0)),
            (-50, 50, 0, (1, 1, 0)),
            (50, 50, 0, (0, 1, 0)),
        ]

        for x, y, z, color in lights:
            self.renderer.draw_traffic_light(x, y, z, color)

    def _draw_carla_traffic_lights(self):
        """绘制CARLA交通灯"""
        actors = self.world.get_actors()

        for actor in actors:
            if 'traffic_light' in actor.type_id:
                transform = actor.get_transform()
                location = transform.location
                rotation = transform.rotation

                state = actor.state
                if state == carla.TrafficLightState.Red:
                    color = (1, 0, 0)
                elif state == carla.TrafficLightState.Yellow:
                    color = (1, 1, 0)
                elif state == carla.TrafficLightState.Green:
                    color = (0, 1, 0)
                else:
                    color = (0.3, 0.3, 0.3)

                self.renderer.draw_traffic_light(
                    location.x, location.y, location.z, 
                    color, rotation.yaw
                )

    def draw_frame(self, capture_for_web=False):
        """绘制一帧"""
        from OpenGL.GLU import gluPerspective

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, float(WINDOW_WIDTH) / WINDOW_HEIGHT, 0.1, 2000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.camera.apply()

        self.renderer.draw_ground()
        self.draw_road_network()
        self.renderer.draw_buildings()
        self.draw_vehicles()
        self.draw_traffic_lights()

        pygame.display.flip()

        # 更新建筑物（每帧检查）
        if self.world and (not hasattr(self.renderer, 'buildings') or not self.renderer.buildings):
            self.renderer.update_buildings(self.world)

        # 如果需要，捕获帧供Web使用
        if capture_for_web:
            self._capture_frame_for_web()

    def _capture_frame_for_web(self):
        """捕获帧数据供Web服务器使用"""
        global frame_data
        import numpy as np

        try:
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            image_data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)

            img_array = np.frombuffer(image_data, dtype=np.uint8)
            img_array = img_array.reshape((WINDOW_HEIGHT, WINDOW_WIDTH, 3))
            img_array = np.flipud(img_array)

            try:
                from PIL import Image
                img = Image.fromarray(img_array, 'RGB')

                with BytesIO() as buffer:
                    img.save(buffer, format='JPEG', quality=85)
                    buffer.seek(0)
                    with frame_lock:
                        frame_data = buffer.read()
            except ImportError:
                print("PIL not available. Web streaming disabled.")
        except Exception as e:
            print(f"Error capturing frame: {e}")

    def handle_events(self):
        """处理事件"""
        if self.headless:
            # 无头模式不处理窗口事件
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    self.camera.follow_mode = not self.camera.follow_mode
                    mode = "follow" if self.camera.follow_mode else "free view"
                    print(f"Switched to {mode} mode")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_pressed = 'rotate'
                elif event.button == 3:
                    self.mouse_pressed = 'pan'
                elif event.button == 4:
                    self.camera.zoom(1)
                elif event.button == 5:
                    self.camera.zoom(-1)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = None
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    if self.mouse_pressed == 'rotate':
                        self.camera.rotate(dx, dy)
                    elif self.mouse_pressed == 'pan':
                        self.camera.pan(dx, dy)
                self.last_mouse_pos = event.pos

    def run(self, web_server=None):
        """主循环"""
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            # 无头模式下强制捕获帧供网页使用
            capture_for_web = (web_server is not None) or self.headless
            self.draw_frame(capture_for_web=capture_for_web)
            clock.tick(30)

        pygame.quit()