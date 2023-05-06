#!/usr/bin/env python3
# coding: utf-8
import rospy
import geometry_msgs.msg
from smach_files import joint_controller, wheel_controller

#game_controller以外の物体とdestinationはboxの場合
def no_put_object(arm_shift_z_m):
    res_move = joint_controller.move_gripper_to_target("placeable_point", geometry_msgs.msg.Point(x=-0.3, y=0.0, z=arm_shift_z_m))
    if not res_move:
        return False
    rospy.sleep(4.0)
    wheel_controller.processing("X:30")
    rospy.sleep(5.0)
    joint_controller.open_gripper()
    rospy.sleep(2.0)
    return True


#物体＝game_controllerとdestinationはboxの場合
def no_put_object_for_game_controller(arm_shift_z_m):
    res_move = joint_controller.move_gripper_to_target_for_game_controller("placeable_point", geometry_msgs.msg.Point(x=-0.3, y=0.0, z=arm_shift_z_m))
    if not res_move:
        return False
    rospy.sleep(4.0)
    wheel_controller.processing("X:60")
    rospy.sleep(5.0)
    joint_controller.open_gripper()
    rospy.sleep(2.0)
    return True


#物体を人間に手渡す場合
def to_moderator(arm_shift_z_m):
    res_move = joint_controller.move_gripper_to_target("placeable_point", geometry_msgs.msg.Point(x=-0.3, y=0.0, z=arm_shift_z_m))
    if not res_move:
        return False
    rospy.sleep(4.0)
    wheel_controller.processing("X:12")
    rospy.sleep(5.0)
    return True


# この部分は「$ python no_put.py」の時には実行される
if __name__ == '__main__':
    import box_detect
    print ("do processing() @grasping.py")
    rospy.init_node("debug")
    joint_controller.move_to_registered_motion("DETECTING_BOX_POSE")
    box_detect.box_entry_gate_detection_ctrl(True)
    box_detect.wait_for_frame_exists("placeable_point", 30)
    no_put_object(0.2)
    box_detect.box_entry_gate_detection_ctrl(False)