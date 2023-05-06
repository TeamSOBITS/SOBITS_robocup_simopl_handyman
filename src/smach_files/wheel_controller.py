#!/usr/bin/env python3
# coding: utf-8
import rospy
from hsr_ros.srv import odom_base

# ロボットの体の移動に関する処理
def processing(send_msg):
    rospy.wait_for_service("/robot_ctrl/base_ctrl", 3.0)
    try:
        odom_base_service = rospy.ServiceProxy("/robot_ctrl/base_ctrl", odom_base)
        res = odom_base_service(send_msg)
        return res.res_str
    except rospy.ServiceException as e:
        print ("Service call failed: %s" % e)
    return ""


# この部分は「$ python wheel_controller.py」の時には実行される
if __name__ == '__main__':
    print ("do processing() @robot_motion.py")
    processing('S:10')