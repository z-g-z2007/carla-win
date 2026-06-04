"""
Camera module for CarlaViz
Handles camera control and view transformations
"""

import math


class CarlaVizCamera:
    """3D相机控制类"""

    def __init__(self):
        self.distance = 20.0
        self.height = 8.0
        self.rotation_x = 60.0  # 俯视角度
        self.rotation_z = 0.0  # 水平旋转角度
        self.target = [0.0, 0.0, 0.0]
        self.target_yaw = 0.0
        self.fov = 60.0
        self.follow_mode = True  # 默认跟随模式

    def rotate(self, dx, dy):
        """旋转相机 - 切换到自由视角"""
        self.follow_mode = False
        self.rotation_z += dx * 0.3
        self.rotation_x += dy * 0.3
        self.rotation_x = max(5, min(85, self.rotation_x))

    def zoom(self, delta):
        """缩放相机距离"""
        self.distance *= (1.0 + delta * 0.1)
        self.distance = max(10, min(200, self.distance))

    def pan(self, dx, dy):
        """平移相机"""
        scale = self.distance * 0.002
        self.target[0] -= dx * scale * math.sin(math.radians(self.rotation_z))
        self.target[1] += dx * scale * math.cos(math.radians(self.rotation_z))
        self.target[0] -= dy * scale * math.cos(math.radians(self.rotation_z))
        self.target[1] -= dy * scale * math.sin(math.radians(self.rotation_z))
        self.target[2] = 0

    def apply(self):
        """应用相机变换到OpenGL"""
        from OpenGL.GL import glLoadIdentity
        from OpenGL.GLU import gluLookAt

        glLoadIdentity()

        if self.follow_mode:
            # 跟随模式 - 车后视角
            yaw_rad = math.radians(self.target_yaw)

            cam_x = self.target[0] - self.distance * math.cos(yaw_rad)
            cam_y = self.target[2] + self.height
            cam_z = self.target[1] - self.distance * math.sin(yaw_rad)

            look_at_x = self.target[0]
            look_at_y = self.target[2] + 1.0
            look_at_z = self.target[1]
        else:
            # 自由视角 - 鸟瞰图
            rad_x = math.radians(self.rotation_x)
            rad_z = math.radians(self.rotation_z)

            cam_x = self.target[0] + self.distance * math.cos(rad_x) * math.sin(rad_z)
            cam_y = self.target[2] + self.distance * math.sin(rad_x)
            cam_z = self.target[1] + self.distance * math.cos(rad_x) * math.cos(rad_z)

            look_at_x = self.target[0]
            look_at_y = self.target[2]
            look_at_z = self.target[1]

        gluLookAt(cam_x, cam_y, cam_z,
                  look_at_x, look_at_y, look_at_z,
                  0.0, 1.0, 0.0)

    def set_target(self, x, y, z, yaw=0.0):
        """设置相机跟踪目标"""
        self.target = [x, y, z]
        self.target_yaw = yaw

    def reset(self):
        """重置相机到默认状态"""
        self.distance = 20.0
        self.height = 8.0
        self.rotation_x = 60.0
        self.rotation_z = 0.0
        self.target = [0.0, 0.0, 0.0]
        self.target_yaw = 0.0
        self.follow_mode = True