#!/usr/bin/env python3
# coding: utf-8
import rospy
from hsr_ros.srv import obj_depth
from smach_files import joint_controller

# 物体のdepthを計算する処理
def get_obj_depth():
    rospy.loginfo("Getting depth of grasped object")
    joint_controller.move_to_registered_motion("MEASUREMENT_POSE")
    rospy.sleep(4.0)
    rospy.wait_for_service('/get_object_depth', 3.0)
    rospy.loginfo('Object_depth')
    try:
        depth = rospy.ServiceProxy('/get_object_depth', obj_depth)
        result = depth()
    except rospy.ServiceException as e:
        print ("Object_depth Service call failed: %s" % e)
    joint_controller.move_to_registered_motion("MEASUREMENT_POSE")
    print ("depth:",result.x)
    return result.x + 0.1


# この部分は「$ python obj_dept_measure.py」の時には実行される
if __name__ == '__main__':
    print ("do processing() @object_depth.py")
    get_obj_depth()