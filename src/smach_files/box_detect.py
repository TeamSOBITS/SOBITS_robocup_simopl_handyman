#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
import tf
from box_entry_gate_detection.srv import execute_ctrl
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


# ゴミ箱の投入口検出の処理
def box_entry_gate_detection_ctrl(mode):
    rospy.wait_for_service("/box_entry_gate_detection/execute_ctrl", 3.0)
    try:
        estimator_ctrl = rospy.ServiceProxy("/box_entry_gate_detection/execute_ctrl", execute_ctrl)
        res = estimator_ctrl(mode)
        return res.response
    except rospy.ServiceException as e:
        rospy.logerr(e)
        if handyman_msg_manager.get_finish_task_flag():
                return False
    return False


# この部分は「$ python box_detect.py」の時には実行される
if __name__ == '__main__':
    import box_detect
    print ("do processing() @grasping.py")
    rospy.init_node("debug")
    print (box_detect.box_entry_gate_detection_ctrl(True))
    res_place_pos = box_detect.wait_for_frame_exists("placeable_point", 30)
    print ("res_place_pos:",res_place_pos)
    box_detect.box_entry_gate_detection_ctrl(False)