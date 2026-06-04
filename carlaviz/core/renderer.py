"""
Renderer module for CarlaViz
Handles OpenGL rendering of CARLA scene elements
"""

import math
import numpy as np
from OpenGL.GL import *


class CarlaRenderer:
    """OpenGL渲染器"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buildings = []

    def init_opengl(self):
        """初始化OpenGL设置"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLightfv(GL_LIGHT0, GL_POSITION, [100, 100, 200, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])

        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        from OpenGL.GLU import gluPerspective
        gluPerspective(60.0, float(self.width) / self.height, 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClearColor(0.1, 0.1, 0.15, 1.0)

    def draw_ground(self):
        """绘制地面网格"""
        glDisable(GL_LIGHTING)

        grid_size = 500
        grid_step = 20

        glColor4f(0.3, 0.3, 0.3, 0.5)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for i in range(-grid_size, grid_size + 1, grid_step):
            glVertex3f(i, 0, -grid_size)
            glVertex3f(i, 0, grid_size)
            glVertex3f(-grid_size, 0, i)
            glVertex3f(grid_size, 0, i)
        glEnd()

        glEnable(GL_LIGHTING)

    def draw_box(self, width, height, depth):
        """绘制盒子"""
        w, h, d = width / 2, height / 2, depth / 2

        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)

        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)

        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)

        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)

        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)

        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        glEnd()

    def draw_circle(self, cx, cy, cz, radius, segments):
        """绘制圆"""
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            z = cz + radius * math.sin(angle)
            glVertex3f(x, cy, z)
        glEnd()

    def draw_sensor_range(self, x, y, z):
        """绘制传感器范围"""
        glDisable(GL_LIGHTING)

        # 内圈
        glColor4f(0.0, 1.0, 0.0, 0.3)
        glLineWidth(1.0)
        self.draw_circle(x, z + 1, y, 50, 32)

        # 外圈
        glColor4f(0.0, 1.0, 0.0, 0.2)
        self.draw_circle(x, z + 1, y, 80, 32)

        # 点云
        glColor4f(1.0, 0.4, 0.8, 0.8)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for _ in range(200):
            angle = np.random.uniform(0, 2 * math.pi)
            dist = np.random.uniform(10, 80)
            px = x + dist * math.cos(angle)
            pz = z + np.random.uniform(-0.5, 0.5)
            py = y + dist * math.sin(angle)
            glVertex3f(px, pz, py)
        glEnd()

        glEnable(GL_LIGHTING)

    def draw_traffic_light(self, x, y, z, color, yaw=0):
        """绘制单个交通灯 - 简单垂直结构"""
        glPushMatrix()
        
        # 位置和朝向
        glTranslatef(x, z, y)  # 坐标转换: CARLA(x,y,z) -> OpenGL(x,z,y)
        glRotatef(-yaw, 0, 1, 0)  # 根据朝向旋转

        # 灯杆（灰色，竖直，从地面到灯头底部）
        glColor4f(0.35, 0.35, 0.35, 1.0)
        glPushMatrix()
        glTranslatef(0, 4.0, 0)  # 灯杆底部在地面，顶部在8米高度
        self.draw_box(0.2, 8.0, 0.2)  # 竖直灯杆
        glPopMatrix()

        # 灯头外壳（黑色，包含三个灯）
        glColor4f(0.15, 0.15, 0.15, 1.0)
        glPushMatrix()
        glTranslatef(0, 7.5, 0.3)  # 灯头在灯杆顶部
        self.draw_box(0.5, 1.8, 0.3)  # 灯头外壳
        glPopMatrix()

        # 三个灯（红、黄、绿垂直排列）
        lights = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # 红、黄、绿
        glDisable(GL_LIGHTING)
        
        for i, light_color in enumerate(lights):
            glPushMatrix()
            # 灯的位置：垂直排列，间距0.5米
            glTranslatef(0, 8.1 - i * 0.6, 0.4)  
            
            # 发光效果
            if light_color == color:
                # 亮着的灯
                glColor4f(*light_color, 1.0)
                glPointSize(18.0)
                glBegin(GL_POINTS)
                glVertex3f(0, 0, 0)
                glEnd()
                # 添加光晕
                glColor4f(*light_color, 0.25)
                glPointSize(35.0)
                glBegin(GL_POINTS)
                glVertex3f(0, 0, 0)
                glEnd()
            else:
                # 未亮的灯
                glColor4f(0.3, 0.3, 0.3, 1.0)
                glPointSize(10.0)
                glBegin(GL_POINTS)
                glVertex3f(0, 0, 0)
                glEnd()
            
            glPopMatrix()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def draw_demo_roads(self):
        """绘制演示道路"""
        glColor4f(0.5, 0.5, 0.5, 1.0)
        glLineWidth(8.0)
        glBegin(GL_LINES)

        # 主干道
        glVertex3f(-100, 0.1, -50)
        glVertex3f(100, 0.1, -50)
        glVertex3f(-100, 0.1, 50)
        glVertex3f(100, 0.1, 50)

        # 交叉路
        glVertex3f(-50, 0.1, -100)
        glVertex3f(-50, 0.1, 100)
        glVertex3f(50, 0.1, -100)
        glVertex3f(50, 0.1, 100)

        glEnd()

        # 车道线
        glColor4f(1.0, 1.0, 0.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)

        for i in range(-100, 101, 20):
            glVertex3f(i, 0.15, -50)
            glVertex3f(i + 10, 0.15, -50)
            glVertex3f(i, 0.15, 50)
            glVertex3f(i + 10, 0.15, 50)

        for i in range(-100, 101, 20):
            glVertex3f(-50, 0.15, i)
            glVertex3f(-50, 0.15, i + 10)
            glVertex3f(50, 0.15, i)
            glVertex3f(50, 0.15, i + 10)

        glEnd()

    def draw_carla_roads(self, waypoints, carla_module):
        """绘制CARLA道路 - 使用连续线条"""
        if not waypoints:
            return

        # 按道路ID分组路点
        road_segments = {}
        for waypoint in waypoints:
            road_id = waypoint.road_id
            if road_id not in road_segments:
                road_segments[road_id] = []
            road_segments[road_id].append(waypoint)

        # 对每个道路分段按s值排序并绘制连续线条
        for road_id, wps in road_segments.items():
            # 按s值排序确保顺序正确
            wps.sort(key=lambda wp: wp.s)
            
            # 按车道类型分组
            lanes = {}
            for wp in wps:
                lane_key = (wp.lane_id, wp.lane_type)
                if lane_key not in lanes:
                    lanes[lane_key] = []
                lanes[lane_key].append(wp)
            
            # 绘制每个车道
            for (lane_id, lane_type), lane_wps in lanes.items():
                if lane_type == carla_module.LaneType.Driving:
                    glColor4f(0.5, 0.5, 0.5, 1.0)
                    width = 3.0
                elif lane_type == carla_module.LaneType.Sidewalk:
                    glColor4f(0.4, 0.4, 0.45, 1.0)
                    width = 2.0
                else:
                    glColor4f(0.35, 0.35, 0.35, 1.0)
                    width = 2.0

                glLineWidth(width)
                glBegin(GL_LINE_STRIP)  # 使用连续线条
                for wp in lane_wps:
                    loc = wp.transform.location
                    glVertex3f(loc.x, loc.z + 0.1, loc.y)
                glEnd()

        # 绘制车道线
        for waypoint in waypoints:
            next_wps = waypoint.next(5.0)
            for next_wp in next_wps:
                self._draw_lane_markings(waypoint, next_wp, carla_module)

    def _draw_lane_markings(self, wp1, wp2, carla_module):
        """绘制车道线"""
        glColor4f(1.0, 1.0, 0.0, 1.0)
        glLineWidth(2.0)

        loc1 = wp1.transform.location
        loc2 = wp2.transform.location
        yaw1 = math.radians(wp1.transform.rotation.yaw)

        lane_width = wp1.lane_width
        perp_x = math.sin(yaw1)
        perp_y = -math.cos(yaw1)

        # 左侧车道线
        left_marking = wp1.left_lane_marking
        if left_marking and left_marking.type != carla_module.LaneMarkingType.NONE:
            loc1_left_x = loc1.x + perp_x * lane_width / 2
            loc1_left_y = loc1.y + perp_y * lane_width / 2
            loc2_left_x = loc2.x + perp_x * lane_width / 2
            loc2_left_y = loc2.y + perp_y * lane_width / 2

            if left_marking.type == carla_module.LaneMarkingType.Solid:
                glBegin(GL_LINES)
                glVertex3f(loc1_left_x, loc1.z + 0.15, loc1_left_y)
                glVertex3f(loc2_left_x, loc2.z + 0.15, loc2_left_y)
                glEnd()
            elif left_marking.type == carla_module.LaneMarkingType.Broken:
                segment_length = 10.0
                total_length = math.hypot(loc2.x - loc1.x, loc2.y - loc1.y)
                num_segments = int(total_length / (segment_length * 2))

                for i in range(num_segments):
                    t1 = i * 2.0 / num_segments
                    t2 = (i * 2 + 1) / num_segments

                    start_x = loc1_left_x + (loc2_left_x - loc1_left_x) * t1
                    start_y = loc1_left_y + (loc2_left_y - loc1_left_y) * t1
                    end_x = loc1_left_x + (loc2_left_x - loc1_left_x) * t2
                    end_y = loc1_left_y + (loc2_left_y - loc1_left_y) * t2

                    glBegin(GL_LINES)
                    glVertex3f(start_x, loc1.z + 0.15, start_y)
                    glVertex3f(end_x, loc2.z + 0.15, end_y)
                    glEnd()

        # 右侧车道线
        right_marking = wp1.right_lane_marking
        if right_marking and right_marking.type != carla_module.LaneMarkingType.NONE:
            loc1_right_x = loc1.x - perp_x * lane_width / 2
            loc1_right_y = loc1.y - perp_y * lane_width / 2
            loc2_right_x = loc2.x - perp_x * lane_width / 2
            loc2_right_y = loc2.y - perp_y * lane_width / 2

            if right_marking.type == carla_module.LaneMarkingType.Solid:
                glBegin(GL_LINES)
                glVertex3f(loc1_right_x, loc1.z + 0.15, loc1_right_y)
                glVertex3f(loc2_right_x, loc2.z + 0.15, loc2_right_y)
                glEnd()
            elif right_marking.type == carla_module.LaneMarkingType.Broken:
                segment_length = 10.0
                total_length = math.hypot(loc2.x - loc1.x, loc2.y - loc1.y)
                num_segments = int(total_length / (segment_length * 2))

                for i in range(num_segments):
                    t1 = i * 2.0 / num_segments
                    t2 = (i * 2 + 1) / num_segments

                    start_x = loc1_right_x + (loc2_right_x - loc1_right_x) * t1
                    start_y = loc1_right_y + (loc2_right_y - loc1_right_y) * t1
                    end_x = loc1_right_x + (loc2_right_x - loc1_right_x) * t2
                    end_y = loc1_right_y + (loc2_right_y - loc1_right_y) * t2

                    glBegin(GL_LINES)
                    glVertex3f(start_x, loc1.z + 0.15, start_y)
                    glVertex3f(end_x, loc2.z + 0.15, end_y)
                    glEnd()

    def update_buildings(self, world):
        """更新建筑物列表"""
        self.buildings = []
        if world:
            actors = world.get_actors()
            for actor in actors:
                if 'building' in actor.type_id:
                    transform = actor.get_transform()
                    bbox = actor.bounding_box
                    self.buildings.append({
                        'location': transform.location,
                        'extent': bbox.extent,
                    })

    def draw_buildings(self):
        """绘制建筑物"""
        glDisable(GL_LIGHTING)

        glColor4f(0.35, 0.35, 0.4, 1.0)
        for building in self.buildings:
            loc = building['location']
            extent = building['extent']

            glPushMatrix()
            glTranslatef(loc.x, loc.z, loc.y)
            glTranslatef(0, extent.z, 0)
            self.draw_box(extent.x * 2, extent.z * 2, extent.y * 2)
            glPopMatrix()

        glEnable(GL_LIGHTING)