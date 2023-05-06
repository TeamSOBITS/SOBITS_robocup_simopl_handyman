#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import sys
import actionlib
from smach_files import joint_controller, handyman_msg_manager
from sobit_navigation_module import SOBITNavigationLibraryPython
from actionlib_msgs.msg import GoalID
from geometry_msgs.msg import Pose

args = sys.argv

session_start_time = rospy.Time()

### hsr_navigation と sobit navigation stack が更新されたら以下の関数に乗り換える ###

#目標座標に移動する処理
def move_to_target_tf(target_tf):
    print('Determining Target Location')
    joint_controller.move_to_registered_motion("INITIAL_POSE")
    rospy.sleep(1.0)
    nav_lib = SOBITNavigationLibraryPython(args[0])
    print('Determined Target Location')
    rospy.loginfo(target_tf)
    try:
        print('Start Moving')
        flag = nav_lib.move2Location(target_tf, False)
        while nav_lib.exist_goal_:
            if rospy.Time.now() > (session_start_time + rospy.Duration(590)) or handyman_msg_manager.get_finish_task_flag():
                nav_lib.cancelMoving()  # 移動の中止（停止命令）
                print("#### send move cancel! (timeout)")
                break
        rospy.sleep(1.0) # status_id_の反映待ち
        if nav_lib.status_id_ == 3 or nav_lib.status_id_ == 1:
            rospy.loginfo('Moving -> Reached [%s]', target_tf)
            return True
        if nav_lib.status_id_ == 4:
            rospy.logerr('Moving -> Failure [%s]', target_tf)
            return False
        if handyman_msg_manager.get_finish_task_flag() == True: #or elapsed_time > rospy.Duration(10):
            rospy.logerr('Moving -> cancelled')
            return False
    except rospy.ServiceException as e:
        print ("Moving Service call failed: %s" % e)
    return False


#目標物のtfによる座標に移動する処理
def move_to_target_pose(target_pose):
    print('Determining Target Location for grasping')
    joint_controller.move_to_registered_motion("INITIAL_POSE")
    rospy.sleep(1.0)
    print (target_pose)
    print('Determined Target Location for grasping')
    nav_lib = SOBITNavigationLibraryPython(args[0])
    rospy.loginfo(target_pose)
    try:
        flag = nav_lib.move2PositionPy(target_pose.position.x, target_pose.position.y, target_pose.position.z, target_pose.orientation.x, target_pose.orientation.y, target_pose.orientation.z, target_pose.orientation.w, "map", False)
        while nav_lib.exist_goal_:
            if rospy.Time.now() > (session_start_time + rospy.Duration(590)) or handyman_msg_manager.get_finish_task_flag():
                nav_lib.cancelMoving()  # 移動の中止（停止命令）
                print("#### send move cancel! (timeout)")
                break
        rospy.sleep(1.0) # status_id_の反映待ち
        if nav_lib.status_id_ == 3 or nav_lib.status_id_ == 1:
            rospy.loginfo('Moving -> Reached [%s]', target_pose)
            return True
        if nav_lib.status_id_ == 4:
            rospy.logerr('Moving -> Failure [%s]', target_pose)
            return False
        if handyman_msg_manager.get_finish_task_flag() == True: #or elapsed_time > rospy.Duration(10):
            rospy.logerr('Moving -> cancelled')
            return False
    except rospy.ServiceException as e:
        print ("Moving Service call failed: %s" % e)
    return False


def set_session_start_time(start_time):
    global session_start_time
    session_start_time = start_time


# この部分は「$ python move.py」の時には実行される
if __name__ == '__main__':
    import estimate_position
    print ("do processing() @move.py")
    rospy.init_node('move_py_node')
    set_session_start_time(rospy.Time.now())
    target_name = "kitchen#GraspingCandidatesPosition13"
    _, pos = estimate_position.estimate_pos(target_name=target_name, distance=0.95)
    res = move_to_target_pose(pos)
