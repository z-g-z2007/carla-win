"""
CARLA utility functions
"""

import sys

try:
    import carla
    carla_available = True
except ImportError:
    carla_available = False


def connect_carla(host='127.0.0.1', port=2000, timeout=2.0):
    """
    连接到CARLA服务器
    
    Args:
        host (str): CARLA服务器地址
        port (int): CARLA服务器端口
        timeout (float): 连接超时时间（秒）
    
    Returns:
        tuple: (client, world, map) 如果连接成功
        None: 如果连接失败
    """
    if not carla_available:
        print("Error: CARLA module not available")
        return None

    try:
        client = carla.Client(host, port)
        client.set_timeout(timeout)
        world = client.get_world()
        carla_map = world.get_map()
        print(f"Successfully connected to CARLA server: {host}:{port}")
        return client, world, carla_map
    except Exception as e:
        print(f"Failed to connect to CARLA: {e}")
        return None


def get_ego_vehicle(world):
    """
    从CARLA场景中获取自车
    
    Args:
        world: CARLA World对象
    
    Returns:
        carla.Actor: 自车Actor
    """
    if not carla_available or world is None:
        return None

    role_names = ['ego', 'hero', 'autopilot', 'player', 'agent']
    actors = world.get_actors()

    # 首先查找具有特定role_name的车辆
    for actor in actors:
        if 'vehicle' in actor.type_id:
            for attr_id, attr_value in actor.attributes.items():
                if attr_id == 'role_name' and attr_value.lower() in role_names:
                    return actor

    # 查找启用了autopilot的车辆
    for actor in actors:
        if 'vehicle' in actor.type_id:
            try:
                if actor.is_autopilot_enabled():
                    return actor
            except:
                pass

    # 返回第一个找到的车辆
    for actor in actors:
        if 'vehicle' in actor.type_id:
            return actor

    return None


def get_all_vehicles(world):
    """
    获取场景中所有车辆
    
    Args:
        world: CARLA World对象
    
    Returns:
        list: 车辆Actor列表
    """
    if not carla_available or world is None:
        return []

    actors = world.get_actors()
    return [actor for actor in actors if 'vehicle' in actor.type_id]


def get_traffic_lights(world):
    """
    获取场景中所有交通灯
    
    Args:
        world: CARLA World对象
    
    Returns:
        list: 交通灯Actor列表
    """
    if not carla_available or world is None:
        return []

    actors = world.get_actors()
    return [actor for actor in actors if 'traffic_light' in actor.type_id]


def get_buildings(world):
    """
    获取场景中所有建筑物
    
    Args:
        world: CARLA World对象
    
    Returns:
        list: 建筑物信息列表
    """
    if not carla_available or world is None:
        return []

    buildings = []
    actors = world.get_actors()
    
    for actor in actors:
        if 'building' in actor.type_id:
            transform = actor.get_transform()
            bbox = actor.bounding_box
            buildings.append({
                'id': actor.id,
                'location': transform.location,
                'extent': bbox.extent,
            })
    
    return buildings


def generate_waypoints(carla_map, distance=2.0):
    """
    生成道路路点
    
    Args:
        carla_map: CARLA Map对象
        distance (float): 路点间距
    
    Returns:
        list: 路点列表
    """
    if not carla_available or carla_map is None:
        return []

    return carla_map.generate_waypoints(distance)