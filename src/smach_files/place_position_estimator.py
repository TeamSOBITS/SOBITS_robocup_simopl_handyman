#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
import tf
from placeable_position_estimator.srv import execute_ctrl
from smach_files import handyman_msg_manager

# frameの出現を待機する処理（ここでは、最大限：30秒）
def wait_for_frame_exists(frame_name, timeout_sec):
    listener = tf.TransformListener()
    start_time = rospy.Time.now()
    while rospy.Time.now() < start_time + rospy.Duration(timeout_sec):
        if listener.frameExists(frame_name):
            return True
        else:
            rospy.sleep(1.0)
            if handyman_msg_manager.get_finish_task_flag():
                return False
    return False


# 可能な物体配置の場所を検出する処理
def placeable_position_estimator_ctrl(mode):
    rospy.wait_for_service("/placeable_position_estimator/execute_ctrl", 3.0)
    try:
        estimator_ctrl = rospy.ServiceProxy("/placeable_position_estimator/execute_ctrl", execute_ctrl)
        res = estimator_ctrl(mode)
        return res.response
    except rospy.ServiceException as e:
        rospy.logerr(e)
        if handyman_msg_manager.get_finish_task_flag():
            return False
    return False
