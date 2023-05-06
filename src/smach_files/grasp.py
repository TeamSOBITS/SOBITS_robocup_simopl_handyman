#!/usr/bin/env python3
# coding: utf-8
from cgi import print_environ_usage
import rospy
import geometry_msgs.msg
from smach_files import joint_controller, wheel_controller, handyman_msg_manager

# 物体を把持する処理
def grasp_object(object_name, option):
    joint_controller.open_gripper()
    # 把持の微調整はここ
    if object_name == "game_controller":
        res_move = joint_controller.move_gripper_to_target_for_game_controller(object_name, geometry_msgs.msg.Point(x=-0.3, y=0.1, z=0.02 + option))
    elif "bottle" in object_name or "ketchup" in object_name:
        res_move = joint_controller.move_gripper_to_target(object_name, geometry_msgs.msg.Point(x=-0.3, y=0.0, z=option - 0.02))
    else:
        res_move = joint_controller.move_gripper_to_target(object_name, geometry_msgs.msg.Point(x=-0.3, y=0.0, z=0.01 + option))
    if not res_move:
        return False
    rospy.sleep(4.0)

    # ----------把持（一回目）-----------------------------------------------------------------------------------------------------------------------------------------
    if handyman_msg_manager.get_finish_task_flag():
        return False
    if object_name == "game_controller":
        wheel_controller.processing("X:62")
        res_move = joint_controller.move_gripper_to_target_for_game_controller("hand_palm_link", geometry_msgs.msg.Point(x=0.22, y=0.0, z= -0.1))
    else:
        wheel_controller.processing("X:32")
    rospy.sleep(2.0)
    joint_controller.close_gripper()
    rospy.sleep(2.0)
    res_grasp = joint_controller.is_grasped_target()
    # ----------把持（一回目）のおわり---------------------------------------------------------------------------------------------------------------------------------

    # ----------把持する前の位置に戻り-------------------------------------------------------------------------------------------------------------------------------------
    if res_grasp:
        if handyman_msg_manager.get_finish_task_flag():
            return False
        if object_name == "game_controller":
            wheel_controller.processing("X:-62")
        else:
            wheel_controller.processing("X:-32")
        rospy.sleep(1.0)
        return True
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------

    # ----------一回目に失敗であれば、把持（二回目）-------------------------------------------------------------------------------------------------------------------
    else:
        joint_controller.open_gripper()
        rospy.sleep(2.0)
        if handyman_msg_manager.get_finish_task_flag():
            return False
        if object_name == "game_controller":
            res_move = joint_controller.move_gripper_to_target_for_game_controller("hand_palm_link", geometry_msgs.msg.Point(x=0.0, y=0.0, z= 0.2))
            wheel_controller.processing("Y:-2")
            rospy.sleep(2.0)
            res_move = joint_controller.move_gripper_to_target_for_game_controller("hand_palm_link", geometry_msgs.msg.Point(x=0.0, y=0.0, z= -0.2))
        else:
            wheel_controller.processing("X:3")
        rospy.sleep(1.0)
        joint_controller.close_gripper()
        rospy.sleep(2.0)
        res_grasp = joint_controller.is_grasped_target()
    # ----------把持（二回目）のおわり---------------------------------------------------------------------------------------------------------------------------------

    # ----------把持する前の位置に戻り-------------------------------------------------------------------------------------------------------------------------------------
        if not res_grasp:
            joint_controller.open_gripper()
            rospy.sleep(2.0)
        if handyman_msg_manager.get_finish_task_flag():
            return False
        if object_name == "game_controller":
            wheel_controller.processing("X:-57")
        else:
            wheel_controller.processing("X:-35")
        rospy.sleep(1.0)
        # joint_controller.move_to_registered_motion("INITIAL_POSE")
        return res_grasp
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------


# この部分は「$ python grasp.py」の時には実行される
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='object_name')
    parser.add_argument('--obj', default="dog_doll", type=str)
    args = parser.parse_args()
    object_name = args.obj
    print ("do processing() @grasping.py")
    rospy.init_node("debug")
    grasp_object(object_name)