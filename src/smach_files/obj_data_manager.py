#!/usr/bin/env python3
# coding:utf-8
import roslib
import os

graspable_obj_list = []
non_graspable_obj_list = []

# graspable_object_list読み込み
def read_graspable_obj_list():
    global graspable_obj_list
    pkg_dir = roslib.packages.get_pkg_dir("robocup_simopl_handyman")
    path = os.path.join(pkg_dir, "config/handyman_graspable_object_list.yaml")
    with open(path) as f:
        lines = f.readlines()
    graspable_obj_list = [line.strip() for line in lines]


# non_graspable_object_list読み込み
def read_non_graspable_obj_list():
    global non_graspable_obj_list
    pkg_dir = roslib.packages.get_pkg_dir("robocup_simopl_handyman")
    path = os.path.join(pkg_dir, "config/handyman_non_graspable_object_list.yaml")
    with open(path) as f:
        lines = f.readlines()
    non_graspable_obj_list = [line.strip() for line in lines]


# graspable_obj_list書き込み
def get_graspable_obj_list():
    return graspable_obj_list


# non_graspable_obj_list書き込み
def get_non_graspable_obj_list():
    return non_graspable_obj_list


# 目的の物体が存在するかの処理
def is_existed_obj(target):
    for obj in graspable_obj_list:
        if target == obj:
            return True  # , obj
    return False  # , ""


# この部分は「$ python obj_data_manager.py」の時には実行される
if __name__ == "__main__":
    read_graspable_obj_list()
    print (get_graspable_obj_list())