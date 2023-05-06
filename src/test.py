#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
from smach_files import obj_data_manager, obj_recog, overlaytext
import numpy as np
rospy.init_node("aa")

target_obj = "toy_penguin"
close_obj_list = ["rabbit_doll", "pink_cup"]
for i in range(100):
    furniture = input("Please Enter furniture: ")
    obj_recog.start_object_recognition(furniture)
    res_detect, target_obj_pose = obj_recog.is_detected_target_obj(target_obj, close_objs=close_obj_list)
    print(res_detect)
    print(target_obj_pose)
    detect_obj_dict = obj_recog.get_detect_obj_pose_dict()
    overlaytext.write_detect_obj(detect_obj_dict)
