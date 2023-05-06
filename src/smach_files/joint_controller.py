#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
from hsr_ros.srv import robot_motion
from hsr_ros.srv import gripper_ctrl
from hsr_ros.srv import gripper_move
from hsr_ros.srv import is_grasped

# エンドエフェクタを開ける処理
def open_gripper():
    rospy.wait_for_service("/robot_ctrl/gripper_open_and_close", 3.0)
    try:
        gripper_open_service = rospy.ServiceProxy("/robot_ctrl/gripper_open_and_close", gripper_ctrl)
        res = gripper_open_service(0.92)
        return res.is_moved
    except rospy.ServiceException as e:
        rospy.logerr("Gripper_open Service call failed: %s", e)
    return False


# エンドエフェクタを閉める処理
def close_gripper():
    rospy.wait_for_service("/robot_ctrl/gripper_open_and_close", 3.0)
    try:
        gripper_open_service = rospy.ServiceProxy("/robot_ctrl/gripper_open_and_close", gripper_ctrl)
        res = gripper_open_service(0.00)
        return res.is_moved
    except rospy.ServiceException as e:
        rospy.logerr("Gripper_close Service call failed: %s", e)
    return False


# エンドエフェクタが目標物に移動する処理（game_controller対象外）
def move_gripper_to_target(target_frame_name, shift):
    rospy.wait_for_service('/robot_ctrl/gripper_move_to_target', 3.0)
    try:
        gripper_move_to_target_service = rospy.ServiceProxy('/robot_ctrl/gripper_move_to_target', gripper_move)
        res = gripper_move_to_target_service(target_frame_name, shift)
        return res.is_moved
    except rospy.ServiceException as e:
        rospy.logerr("Gripper_move Service call failed: %s", e)
    return False


# エンドエフェクタが目標物に移動する処理（game_controller対象）
def move_gripper_to_target_for_game_controller(target_frame_name, shift):
    rospy.wait_for_service('/robot_ctrl/gripper_move_to_target_for_game_controller', 3.0)
    try:
        gripper_move_to_target_service = rospy.ServiceProxy('/robot_ctrl/gripper_move_to_target_for_game_controller', gripper_move)
        res = gripper_move_to_target_service(target_frame_name, shift)
        return res.is_moved
    except rospy.ServiceException as e:
        rospy.logerr("Gripper_move Service call failed: %s", e)
    return False


# 登録された動きを実行する処理
def move_to_registered_motion(motion_type):
    rospy.wait_for_service("/robot_ctrl/motion_ctrl", 3.0)
    try:
        motion = rospy.ServiceProxy("/robot_ctrl/motion_ctrl", robot_motion)
        res = motion(motion_type)
        return res.is_moved
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed : {}".format(e))
    return False


# 把持が成功かどうかの処理
def is_grasped_target():
    rospy.wait_for_service("/robot_ctrl/is_grasped", 3.0)
    try:
        is_grasped_client = rospy.ServiceProxy("/robot_ctrl/is_grasped", is_grasped)
        res = is_grasped_client()
        return res.is_grasped
    except rospy.ServiceException as e:
        rospy.logerr("Is grasped service call failed : %s", e)
    return False


# この部分は「$ python  joint_controller.py」の時には実行される
if __name__ == "__main__":
    rospy.init_node("debug_joint_controller")