#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import roslib
import yaml
from subprocess import Popen
import rospy
import rosparam

room_location_list = ["bedroom", "kitchen", "living_room", "lobby"]
robot_pos = ""
bedroom_patrol_list = []
kitchen_patrol_list = []
living_room_patrol_list = []
lobby_patrol_list = []
bedroom_data_list = []
kitchen_data_list = []
living_data_list = []
lobby_data_list = []
destination_list = []


# 巡回用のLocationを読み込み
def read_patrol_list():
    global bedroom_patrol_list, kitchen_patrol_list, living_room_patrol_list, lobby_patrol_list
    bedroom_patrol_list = []
    kitchen_patrol_list = []
    living_room_patrol_list = []
    lobby_patrol_list = []
    furniture_list_yaml = rosparam.get_param("/location_pose")#マップの中のyamlファイル（例：Layout2019HM01_objects.yaml)
    for i, furniture in enumerate(furniture_list_yaml):
        if furniture["object_type"] == "graspable":
            if not "#" in furniture["location_name"]:
                furniture["location_name"] = furniture["location_name"]
            if "{}#".format(room_location_list[0]) in furniture["location_name"]:
                bedroom_patrol_list.append(furniture["location_name"])
            elif "{}#".format(room_location_list[1]) in furniture["location_name"]:
                kitchen_patrol_list.append(furniture["location_name"])
            elif "{}#".format(room_location_list[2]) in furniture["location_name"]:
                living_room_patrol_list.append(furniture["location_name"])
            elif "{}#".format(room_location_list[3]) in furniture["location_name"]:
                lobby_patrol_list.append(furniture["location_name"])
    rospy.loginfo('bedroom_patrol_list: ' + str(bedroom_patrol_list))
    rospy.loginfo('kitchen_patrol_list: ' + str(kitchen_patrol_list))
    rospy.loginfo('living_room_patrol_list: ' + str(living_room_patrol_list))
    rospy.loginfo('lobby_patrol_list: ' + str(lobby_patrol_list))


# 把持できるLocation以外の場所のリストを作成
def read_room_data_list():
    global bedroom_data_list, kitchen_data_list, living_data_list, lobby_data_list, destination_list
    bedroom_data_list = []
    kitchen_data_list = []
    living_data_list = []
    lobby_data_list = []
    destination_list = []
    room_data_list = []

    furniture_list_yaml = rosparam.get_param("/location_pose")
    for furniture in furniture_list_yaml:
        if furniture["object_type"] == "destination" or furniture["object_type"] == "other":
            room_data_list.append(furniture)
        if furniture["object_type"] == "destination":
            destination_list.append(furniture['location_name'])

    for i, room_data in enumerate(room_data_list):
        if "{}#".format(room_location_list[0]) in room_data['location_name']:
            bedroom_data_list.append(room_data['location_name'])
        elif "{}#".format(room_location_list[1]) in room_data['location_name']:
            kitchen_data_list.append(room_data['location_name'])
        elif "{}#".format(room_location_list[2]) in room_data['location_name']:
            living_data_list.append(room_data['location_name'])
        elif "{}#".format(room_location_list[3]) in room_data['location_name']:
            lobby_data_list.append(room_data['location_name'])
    rospy.loginfo('destination_list: ' + str(destination_list))
    rospy.loginfo('bedroom_data_list: ' + str(bedroom_data_list))
    rospy.loginfo('kitchen_data_list: ' + str(kitchen_data_list))
    rospy.loginfo('living_data_list: ' + str(living_data_list))
    rospy.loginfo('lobby_data_list: ' + str(lobby_data_list))


# SLAMを起動
def launch_slam(map_id):
    print (map_id)
    pkg_dir = roslib.packages.get_pkg_dir("robocup_simopl_handyman")
    room_data_dir = os.path.join(pkg_dir, "map/{}".format(map_id))
    launch_file_name = "{}.launch".format(map_id)
    Popen(["roslaunch", "robocup_simopl_handyman", launch_file_name])
    rospy.loginfo('Loading environment information')
    rospy.sleep(10)
    read_patrol_list()
    read_room_data_list()
    rospy.sleep(5)


# 巡回用に家具のリストを取得
def get_furniture_patrol_list():
    return bedroom_patrol_list, kitchen_patrol_list, living_room_patrol_list, lobby_patrol_list


# 文章解析用に家具のリストを取得
def get_furniture_name_list():
    bed_room_furniture_list = []
    kitchen_furniture_list = []
    living_room_furniture_list = []
    lobby_furniture_list = []
    for furniture in bedroom_data_list:
        furniture = furniture.replace("{}#".format(room_location_list[0]), "").replace("@", "").replace("$", "")
        bed_room_furniture_list.append(furniture)
    for furniture in kitchen_data_list:
        furniture = furniture.replace("{}#".format(room_location_list[1]), "").replace("@", "").replace("$", "")
        kitchen_furniture_list.append(furniture)
    for furniture in living_data_list:
        furniture = furniture.replace("{}#".format(room_location_list[2]), "").replace("@", "").replace("$", "")
        living_room_furniture_list.append(furniture)
    for furniture in lobby_data_list:
        furniture = furniture.replace("{}#".format(room_location_list[3]), "").replace("@", "").replace("$", "")
        lobby_furniture_list.append(furniture)
    return bed_room_furniture_list, kitchen_furniture_list, living_room_furniture_list, lobby_furniture_list


# 現在の場所を取得
def get_room_location_list():
    return room_location_list


# 現在いる部屋を保存
def set_robot_pos(room_name):
    global robot_pos
    robot_pos = room_name


# 巡回する部屋のlocationを取得
def get_now_room_patrol_list():
    if robot_pos == room_location_list[0]:
        return bedroom_patrol_list
    elif robot_pos == room_location_list[1]:
        return kitchen_patrol_list
    elif robot_pos == room_location_list[2]:
        return living_room_patrol_list
    elif robot_pos == room_location_list[3]:
        return lobby_patrol_list
    return []


# 把持できるLocation以外の場所を取得
def get_now_room_data_list():
    if robot_pos == room_location_list[0]:
        return bedroom_data_list
    elif robot_pos == room_location_list[1]:
        return kitchen_data_list
    elif robot_pos == room_location_list[2]:
        return living_data_list
    elif robot_pos == room_location_list[3]:
        return lobby_data_list
    return []


# 物体の乗っている家具は部屋にあるかの確認
def is_existed_furniture_obj(target):
    furniture_list = get_now_room_data_list()
    for furniture in furniture_list:
        if target in furniture:
            return True
    return False


# 対象物体のtfを取得
def get_target_furniture_obj_tf_list(target, furniture_list=[]):
    tf_list = []
    if len(furniture_list) == 0:
        furniture_list = get_now_room_data_list()
    for furniture in furniture_list:
        if target in furniture and len(furniture) <= (len(robot_pos + "#" + target) + 2):
            tf_list.append(furniture)
    return tf_list


# 対象目的地のリストを取得
def get_target_destination_list(target):
    target_list = []
    for destination in destination_list:
        if target in destination:
            target_list.append(destination)
    return target_list


# 対象目的地の部屋リストを取得
def get_target_room_data_list(target):
    if target == room_location_list[0]:
        return bedroom_data_list
    elif target == room_location_list[1]:
        return kitchen_data_list
    elif target == room_location_list[2]:
        return living_data_list
    elif target == room_location_list[3]:
        return lobby_data_list
    rospy.logerr("target room data list not found")
    return []


# 全ての物体のリストを作成
def get_all_furniture_obj_tf_list():
    all_data_list = []
    for furniture_list in [bedroom_data_list, kitchen_data_list, living_data_list, lobby_data_list]:
        for furniture_name in furniture_list:
            all_data_list.append(furniture_name)
    return all_data_list


# この部分は「$ python  room_data_manager.py」の時には実行される
if __name__ == "__main__":
    rospy.init_node("debug_room_data_manager")
    read_room_data_list("/home/rg-dell-04/catkin_ws/src/robocup_simopl_handyman/map/LayoutHM01/saved_location_LayoutHM01_other_object.json")