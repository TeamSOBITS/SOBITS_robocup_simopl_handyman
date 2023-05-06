#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import roslib
import json
import rospy
import collections as cl

room_location_list = ["bedroom", "kitchen", "living room", "lobby"]
bedroom_data_list = []
kitchen_data_list = []
living_data_list = []
lobby_data_list = []


def write_json(list_json, label_list, room_data_dir, option):
    ok_dict = cl.OrderedDict()
    no_dict = cl.OrderedDict()
    for room_data in list_json:
        is_get = False
        for label in label_list:
            if label in room_data:
                is_get = True
                ok_dict[room_data] = list_json[room_data]
        if not is_get:
            print (room_data)
            no_dict[room_data] = list_json[room_data]
    """
    write_json_dir = os.path.join(room_data_dir, "check")
    if not os.path.isdir(write_json_dir):
        os.mkdir(write_json_dir)
    ok_file_path = os.path.join(write_json_dir, "{}_ok.json".format(option))
    no_file_path = os.path.join(write_json_dir, "{}_no.json".format(option))
    ok_f = open(ok_file_path, "w")
    no_f = open(no_file_path, "w")
    json.dump(ok_dict, ok_f, indent=4, skipkeys=True, sort_keys=True)
    json.dump(no_dict, no_f, indent=4, skipkeys=True, sort_keys=True)
    """


def read_room_data_list(non_grasp_obj_list_path, destination_list_path, room_data_dir):
    global bedroom_data_list, kitchen_data_list, living_data_list, lobby_data_list
    bedroom_data_list = []
    kitchen_data_list = []
    living_data_list = []
    lobby_data_list = []
    label_list = []
    with open("/home/rg-leader/catkin_ws/src/robocup_simopl_handyman/config/destination_label.txt") as f:
        destination_list = f.readlines()
    destination_label_list = [line.strip() for line in destination_list]
    with open("/home/rg-leader/catkin_ws/src/robocup_simopl_handyman/config/other_label.txt") as f:
        other_list = f.readlines()
    other_label_list = [line.strip() for line in other_list]
    for data_list in [destination_label_list, other_label_list]:
        for data in data_list:
            label_list.append(data)

    with open(non_grasp_obj_list_path) as f:
        non_grasp_obj_list_json = json.load(f)
    with open(destination_list_path) as f:
        destination_list_json = json.load(f)

    # write_json(non_grasp_obj_list_json, label_list, room_data_dir, "other")
    write_json(destination_list_json, label_list, room_data_dir, "destination")


if __name__ == "__main__":
    rospy.init_node("debug_check")
    map_id = "LayoutHM02"
    pkg_dir = roslib.packages.get_pkg_dir("robocup_simopl_handyman")
    room_data_dir = os.path.join(pkg_dir, "map/{}".format(map_id))
    non_grasp_obj_list_file_name = "{}_other.json".format(map_id)
    destination_list_file_name = "{}_destination.json".format(map_id)
    non_grasp_obj_list_path = os.path.join(room_data_dir, non_grasp_obj_list_file_name)
    destination_list_path = os.path.join(room_data_dir, destination_list_file_name)
    read_room_data_list(non_grasp_obj_list_path, destination_list_path, room_data_dir)
